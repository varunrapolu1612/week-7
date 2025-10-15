import unittest
import pandas as pd
from loader import *

class TestLoader(unittest.TestCase):
    def test_valid_locations(self):
        
        geolocator = get_geolocator(timeout=10)
        # Create a DataFrame to hold known locations and their expected data
        known_locations = {
            "Museum of Modern Art": {
                "latitude": 40.7618552,
                "longitude": -73.9782438,
                "type": "museum"
            },
            "USS Alabama Battleship Memorial Park": {
                "latitude": 30.684373,
                "longitude": -88.015316,
                "type": "park"
            }
        }
        # Test each known location
        for name, expected in known_locations.items():
            result = fetch_location_data(geolocator, name)
            self.assertIsNotNone(result, f"Location '{name}' should not be None")

            # Check latitude and longitude with a tolerance
            self.assertAlmostEqual(result["latitude"], expected["latitude"], places=2)
            self.assertAlmostEqual(result["longitude"], expected["longitude"], places=2)

            # Check type if available
            if result["type"]:
                self.assertEqual(result["type"].lower(), expected["type"].lower())
        return None

    def test_invalid_location(self):
        geolocator = get_geolocator()
        result = fetch_location_data(geolocator, "asdfqwer1234")
        #self.assertIsNone(result, "A nonexistent location should have an empty result.")
        
        # Ensure the result is not None
        self.assertEqual(result["location"], "asdfqwer1234")
        self.assertTrue(pd.isna(result["latitude"]))
        self.assertTrue(pd.isna(result["longitude"]))
        self.assertTrue(pd.isna(result["type"]))

if __name__ == "__main__":
    unittest.main()
