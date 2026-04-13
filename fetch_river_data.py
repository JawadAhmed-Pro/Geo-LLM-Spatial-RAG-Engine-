import requests
import json

def fetch_river_data():
    """
    Fetches the Swat River (and major tributaries) from Overpass API.
    """
    # Overpass QL for the Swat River - Tighter search to avoid 504
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:60];
    (
      way["waterway"="river"]["name"~"Swat"](34.5, 72.0, 35.5, 73.0);
      relation["waterway"="river"]["name"~"Swat"](34.5, 72.0, 35.5, 73.0);
    );
    out body;
    >;
    out skel qt;
    """
    
    print("Fetching river data for Swat region...")
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        with open('hydrology_data.json', 'w') as f:
            json.dump(data, f)
        print(f"Successfully saved {len(data['elements'])} river segments to hydrology_data.json")
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    fetch_river_data()
