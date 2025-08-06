import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GeoCodingClient:
    """
    A client for geocoding operations using the Google Geocoding API.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

    def get_coordinates(self, location: str) -> tuple[float, float]:
        """
        Retrieves the latitude and longitude of a given location.
        
        :param location: The name or address of the location to geocode.
        :return: A tuple (latitude, longitude)
        :raises ValueError: If location not found or API error.
        """
        params = {
            "address": location,
            "key": self.api_key
        }

        response = requests.get(self.endpoint, params=params)
        data = response.json()

        if data["status"] != "OK":
            raise ValueError(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")

        result = data["results"][0]
        location_data = result["geometry"]["location"]
        lat = location_data["lat"]
        lng = location_data["lng"]

        return lat, lng

# if __name__ == "__main__":
#     client = GeoCodingClient()
#     place = "Fushimi Inari Taisha, Kyoto"
#     lat, lng = client.get_coordinates(place)
#     print(f"{place} -> Latitude: {lat}, Longitude: {lng}")
