import requests
import time
import pandas as pd

def get_coordinates(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "TravelGeneticPlanner/1.0"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    else:
        return None, None

def enrich_pois_with_coordinates(csv_path):
    df = pd.read_csv(csv_path)
    latitudes, longitudes = [], []
    for place in df["places"]:
        lat, lon = get_coordinates(place)
        latitudes.append(lat)
        longitudes.append(lon)
        time.sleep(1)
    df["latitude"] = latitudes
    df["longitude"] = longitudes
    return df

if __name__ == "__main__":
    enriched_df = enrich_pois_with_coordinates("data/places.csv")
    enriched_df.to_csv("data/places_with_coords.csv", index=False)
    print("Arquivo salvo com coordenadas!")
