'''
Script to load geographical data into a pandas DataFrame, and save it as a CSV file.
'''

from geopy.geocoders import Nominatim
import pandas as pd
import time


def get_geolocator(agent='h501-student', timeout=10):#added timeout parameter
    """
    Initiate a Nominatim geolocator instance given an `agent`.

    Parameters
    ----------
    agent : str, optional
        Agent name for Nominatim, by default 'h501-student'
    """
    return Nominatim(user_agent=agent)

def fetch_location_data(geolocator, loc, attempts=3): #added attempts parameter to handle Franklin's Barbecue
    for _ in range(attempts):
        try:
            location = geolocator.geocode(loc)

            if location is None:
                return {"location": loc, "latitude": None, "longitude": None, "type": None}
    
            return {"location": loc, "latitude": location.latitude, "longitude": location.longitude, "type": location.raw.get('type', None)}
        except Exception as e:
            print(f" {attempts} Attempts  failed for '{loc}': {e}")
            time.sleep(2)

        print(f"Failed to fetch '{loc}' after {attempts} attempts.")
        return None


def build_geo_dataframe(geolocator, locations):

    geo_data = [location_data for loc in locations
        if (location_data := fetch_location_data(geolocator, loc)) is not None
]
    
    return pd.DataFrame(geo_data)


if __name__ == "__main__":
    geo = get_geolocator()

    locations = ["Museum of Modern Art", "iuyt8765(*&)", "Alaska", "Franklin's Barbecue", "Burj Khalifa"]

    df = build_geo_dataframe(geo,locations)

    df.to_csv("./geo_data.csv")
