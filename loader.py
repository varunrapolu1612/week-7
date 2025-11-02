"""
Class-based loader to geocode locations into a pandas DataFrame and save as CSV.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import sleep
from typing import Iterable, Dict, Any, List, Optional

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


@dataclass
class GeoLoader:
    """
    A small utility class for geocoding location strings using Nominatim.
    """
    agent: str = "h501-student"
    timeout: int = 5
    pause_seconds: float = 0.0
    geolocator: Nominatim = field(init=False)

    def __post_init__(self) -> None:
        self.geolocator = Nominatim(user_agent=self.agent)

    # --- Internal helpers ---

    def _resolve(self, loc: str):
        """
        Low-level resolver that returns a geopy Location or None.
        Isolated for easy mocking in tests.
        """
        try:
            if self.pause_seconds:
                sleep(self.pause_seconds)
            return self.geolocator.geocode(loc, timeout=self.timeout)
        except (GeocoderTimedOut, GeocoderServiceError):
            return None
        except Exception:
            return None

    def _to_record(self, loc: str, location_obj) -> Dict[str, Any]:
        """
        Convert a geopy Location (or None) to a stable record dict.
        Keeps invalid locations as NA rows (per Exercise 3).
        """
        if location_obj is None:
            return {
                "location": loc,
                "latitude": pd.NA,
                "longitude": pd.NA,
                "feature_type": pd.NA,
            }

        raw = getattr(location_obj, "raw", {}) or {}
        feature_type = raw.get("type") if isinstance(raw, dict) else None

        return {
            "location": loc,
            "latitude": getattr(location_obj, "latitude", None),
            "longitude": getattr(location_obj, "longitude", None),
            "feature_type": feature_type,
        }

    # --- Public API ---

    def fetch_location_data(self, loc: str) -> Dict[str, Any]:
        """
        Fetch a single location and return a record dict.
        Never returns None; invalid locations yield NA fields.
        """
        return self._to_record(loc, self._resolve(loc))

    def build_geo_dataframe(self, locations: Iterable[str]) -> pd.DataFrame:
        """
        Geocode each item in `locations` and return a DataFrame of results.

        Behavior
        --------
        - Valid geocodes: resolved coordinates and feature type.
        - Invalid/unresolved: keep the location with NA for coords/type.
        """
        rows: List[Dict[str, Any]] = []
        for loc in locations:
            rows.append(self.fetch_location_data(loc))

        return pd.DataFrame(
            rows, columns=["location", "latitude", "longitude", "feature_type"]
        )

    def to_csv(self, locations: Iterable[str], path: str) -> None:
        """
        Build a DataFrame from `locations` and write it to CSV.
        """
        df = self.build_geo_dataframe(locations)
        df.to_csv(path, index=False)


# Backward-compatible helpers (optional, if your app expects functions)
def get_geolocator(agent: str = "h501-student") -> Nominatim:
    return Nominatim(user_agent=agent)


def fetch_location_data(geolocator: Nominatim, loc: str, *, timeout: int = 5, pause_seconds: float = 0.0):
    """
    Legacy wrapper: behaves like before (returns dict on success, None on failure).
    Kept for compatibility with earlier exercises/tests that import this function.
    """
    try:
        if pause_seconds:
            sleep(pause_seconds)
        location = geolocator.geocode(loc, timeout=timeout)
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    except Exception:
        return None

    if location is None:
        return None

    raw = getattr(location, "raw", {}) or {}
    feature_type = raw.get("type") if isinstance(raw, dict) else None

    return {
        "location": loc,
        "latitude": getattr(location, "latitude", None),
        "longitude": getattr(location, "longitude", None),
        "feature_type": feature_type,
    }


def build_geo_dataframe(locations: Iterable[str], geolocator: Optional[Nominatim] = None, *, timeout: int = 5, pause_seconds: float = 0.0) -> pd.DataFrame:
    """
    Legacy wrapper using class under the hood but preserving signature.
    Retains NA rows for invalid locations (per Exercise 3).
    """
    loader = GeoLoader(agent="h501-student", timeout=timeout, pause_seconds=pause_seconds)
    if geolocator is not None:
        loader.geolocator = geolocator
    return loader.build_geo_dataframe(locations)


if __name__ == "__main__":
    loader = GeoLoader()
    locations = [
        "Museum of Modern Art",
        "iuyt8765(*&)",  # invalid → NA row
        "Alaska",
        "Franklin's Barbecue",
        "Burj Khalifa",
    ]
    loader.to_csv(locations, "./geo_data.csv")
