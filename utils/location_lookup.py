# utils/location_lookup.py

import requests

# 🔑 Replace with your OpenCage API key
OPENCAGE_API_KEY = "ea484554055445888e89a4f95b93d415"

def get_lat_lon(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": place_name,
        "key": OPENCAGE_API_KEY,
        "language": "ta",
        "pretty": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['results']:
        geometry = data['results'][0]['geometry']
        return geometry['lat'], geometry['lng']
    else:
        raise ValueError(f"Unable to find coordinates for: {place_name}")
