import os
import requests
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class RoutesClient:
    """
    A client for interacting with the Google Routes API (computeRouteMatrix).
    Accepts a DataFrame with latitude and longitude to compute pairwise travel times and distances.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.endpoint = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        self.base_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
        }

    def compute_duration_and_distance(self, places_df) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Main method to call the API and return separate duration and distance matrices.

        :param places_df: DataFrame with latitude and longitude columns
        :param mode: Travel mode
        :return: Tuple of (duration_df, distance_df)
        """
        combined_matrix = self._get_travel_matrix(places_df)
        return self._split_matrix(combined_matrix)
    
    def _get_travel_matrix(self, places_df) -> pd.DataFrame:
        """
        Computes the matrix between all points in the DataFrame.

        :param places_df: DataFrame with 'latitude' and 'longitude' columns.
        :param mode: Travel mode: WALK, DRIVE, BICYCLE, TRANSIT
        :return: DataFrame NxN with tuples (duration in minutes, distance in meters).
        """
        coordinates = list(zip(places_df['latitude'], places_df['longitude']))
        waypoints = [
            {
                "waypoint": {
                    "location": {
                        "latLng": {
                            "latitude": lat,
                            "longitude": lng
                        }
                    }
                }
            }
            for lat, lng in coordinates
        ]

        body = {
            "origins": waypoints,
            "destinations": waypoints,
            "travelMode": "WALK",
        }

        # Always request both fields
        field_mask = ["originIndex", "destinationIndex", "duration", "distanceMeters"]

        headers = self.base_headers.copy()
        headers["X-Goog-FieldMask"] = ",".join(field_mask)

        response = requests.post(self.endpoint, headers=headers, json=body)

        if response.status_code != 200:
            raise ValueError(f"HTTP error {response.status_code}: {response.text}")

        data = response.json()
        n = len(places_df)
        matrix = [[None for _ in range(n)] for _ in range(n)]

        for item in data:
            i = item["originIndex"]
            j = item["destinationIndex"]
            raw_duration = item.get("duration", "0s")
            duration_seconds = int(raw_duration.rstrip("s")) if isinstance(raw_duration, str) else 0
            duration_minutes = duration_seconds // 60
            distance = item.get("distanceMeters", 0)
            matrix[i][j] = (duration_minutes, distance)

        return pd.DataFrame(matrix, index=places_df['places'], columns=places_df['places'])

    def _split_matrix(self, matrix_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits a DataFrame of tuples (duration, distance) into two DataFrames.

        :param matrix_df: DataFrame with (duration, distance) tuples
        :return: (duration_df in minutes, distance_df in meters)
        """
        duration_df = matrix_df.applymap(lambda x: x[0] if isinstance(x, tuple) else None)
        duration_df.head()
        distance_df = matrix_df.applymap(lambda x: x[1] if isinstance(x, tuple) else None)
        distance_df.head()
        return duration_df, distance_df