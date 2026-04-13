import requests
import json

def fetch_swat_locations():
    """
    Fetches major towns and cities in Swat District from Overpass API.
    """
    # Overpass QL for cities, towns, and villages in Swat bounding box
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:60];
    (
      node["place"~"city|town|village"](34.5, 72.0, 35.5, 73.0);
    );
    out body;
    """
    
    print("Fetching location data (cities/towns) for Swat...")
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        with open('locations_data.json', 'w') as f:
            json.dump(data, f)
        print(f"Successfully saved {len(data['elements'])} locations to locations_data.json")
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    fetch_swat_locations()
