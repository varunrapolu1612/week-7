import unittest
from unittest.mock import Mock
import pandas as pd

from loader import build_geo_dataframe, fetch_location_data


class DummyLocation:
    def __init__(self, lat: float, lon: float, feature_type: str):
        self.latitude = lat
        self.longitude = lon
        self.raw = {"type": feature_type}


class TestLoader(unittest.TestCase):
    def test_valid_locations(self):
        """
        Validate that the loader gathers known places (coords and type).
        Uses a mocked geolocator for deterministic, fast tests.
        """
        geolocator = Mock()
        # Side effects in the order of the locations list
        geolocator.geocode.side_effect = [
            DummyLocation(40.7618552, -73.9782438, "museum"),  # Museum of Modern Art
            DummyLocation(30.684373, -88.015316, "park"),      # USS Alabama Battleship Memorial Park
        ]

        locations = [
            "Museum of Modern Art",
            "USS Alabama Battleship Memorial Park",
        ]
        df = build_geo_dataframe(locations, geolocator=geolocator)

        # Exactly two rows
        self.assertEqual(len(df), 2)
        self.assertEqual(
            list(df.columns), ["location", "latitude", "longitude", "feature_type"]
        )

        # Check values by location name
        recs = {row["location"]: row for _, row in df.iterrows()}

        moma = recs["Museum of Modern Art"]
        self.assertAlmostEqual(moma["latitude"], 40.7618552, places=6)
        self.assertAlmostEqual(moma["longitude"], -73.9782438, places=6)
        self.assertIn("museum", str(moma["feature_type"]).lower())

        uss = recs["USS Alabama Battleship Memorial Park"]
        self.assertAlmostEqual(uss["latitude"], 30.684373, places=6)
        self.assertAlmostEqual(uss["longitude"], -88.015316, places=6)
        self.assertIn("park", str(uss["feature_type"]).lower())

        # Ensure geocode was called with the expected strings
        calls = [call.args[0] for call in geolocator.geocode.call_args_list]
        self.assertEqual(calls, locations)

    def test_invalid_location(self):
        """
        Invalid locations should remain in the DataFrame with NA values
        for latitude, longitude, and feature_type.
        """
        geolocator = Mock()
        geolocator.geocode.return_value = None  # simulate not found

        invalid = "asdfqwer1234"
        df = build_geo_dataframe([invalid], geolocator=geolocator)

        self.assertEqual(len(df), 1)
        row = df.iloc[0]
        self.assertEqual(row["location"], invalid)
        self.assertTrue(pd.isna(row["latitude"]))
        self.assertTrue(pd.isna(row["longitude"]))
        self.assertTrue(pd.isna(row["feature_type"]))

        # Also confirm fetch_location_data returns None in this case (unit-level)
        self.assertIsNone(fetch_location_data(geolocator, invalid))


if __name__ == "__main__":
    unittest.main(verbosity=2)
