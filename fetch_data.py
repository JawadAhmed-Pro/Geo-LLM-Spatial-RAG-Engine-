"""
Phase 0: Automated Data Acquisition
Fetches hospital data from OpenStreetMap's Overpass API for the Swat region
and saves it as a valid GeoJSON FeatureCollection.
"""

import json
import sys
import time
from pathlib import Path

import requests

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

OVERPASS_QUERY = """
[out:json][timeout:60];
(
  node["amenity"="hospital"](34.7, 72.0, 35.8, 72.9);
  way["amenity"="hospital"](34.7, 72.0, 35.8, 72.9);
  relation["amenity"="hospital"](34.7, 72.0, 35.8, 72.9);
);
out center body;
"""

OUTPUT_FILE = Path(__file__).parent / "swat_hospitals.geojson"


def fetch_overpass_data(query: str, max_retries: int = 3) -> dict:
    """Send a query to the Overpass API and return the JSON response."""
    for attempt in range(1, max_retries + 1):
        print(f"[INFO] Querying Overpass API (attempt {attempt}/{max_retries})...")
        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=120,
                headers={"User-Agent": "GeoLLM-SpatialRAG/1.0"},
            )
            response.raise_for_status()
            data = response.json()
            print(f"[OK]   Received {len(data.get('elements', []))} elements.")
            return data
        except requests.exceptions.Timeout:
            print(f"[WARN] Request timed out on attempt {attempt}.")
            if attempt < max_retries:
                wait = 5 * attempt
                print(f"[INFO] Retrying in {wait}s...")
                time.sleep(wait)
        except requests.exceptions.HTTPError as exc:
            print(f"[ERROR] HTTP error: {exc}")
            if response.status_code == 429:
                wait = 10 * attempt
                print(f"[INFO] Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except requests.exceptions.RequestException as exc:
            print(f"[ERROR] Network error: {exc}")
            raise

    print("[FATAL] All retry attempts exhausted.")
    sys.exit(1)


def extract_coordinates(element: dict) -> tuple[float, float] | None:
    """
    Extract (longitude, latitude) from an Overpass element.
    Nodes have direct lat/lon; ways and relations use the 'center' field.
    Returns coordinates in GeoJSON order: [longitude, latitude].
    """
    if element["type"] == "node":
        lon = element.get("lon")
        lat = element.get("lat")
    else:
        center = element.get("center", {})
        lon = center.get("lon")
        lat = center.get("lat")

    if lon is not None and lat is not None:
        return (float(lon), float(lat))
    return None


def build_feature(element: dict) -> dict | None:
    """Convert a single Overpass element into a GeoJSON Feature."""
    coords = extract_coordinates(element)
    if coords is None:
        return None

    tags = element.get("tags", {})
    properties = {
        "osm_id": element.get("id"),
        "osm_type": element.get("type"),
        "name": tags.get("name", tags.get("name:en", "Unknown")),
        "amenity": tags.get("amenity", "hospital"),
    }

    extra_keys = [
        "name:ur", "name:en", "addr:city", "addr:street",
        "addr:postcode", "phone", "website", "operator",
        "healthcare", "beds", "emergency", "opening_hours",
    ]
    for key in extra_keys:
        if key in tags:
            properties[key.replace(":", "_")] = tags[key]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": list(coords),
        },
        "properties": properties,
    }


def build_geojson(overpass_data: dict) -> dict:
    """Convert the full Overpass response into a GeoJSON FeatureCollection."""
    features = []
    skipped = 0

    for element in overpass_data.get("elements", []):
        feature = build_feature(element)
        if feature is not None:
            features.append(feature)
        else:
            skipped += 1

    if skipped > 0:
        print(f"[WARN] Skipped {skipped} elements without valid coordinates.")

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }
    return geojson


def validate_geojson(geojson: dict) -> bool:
    """Basic validation of the GeoJSON structure."""
    if geojson.get("type") != "FeatureCollection":
        print("[ERROR] Root type is not FeatureCollection.")
        return False

    features = geojson.get("features", [])
    if len(features) == 0:
        print("[ERROR] No features found in the FeatureCollection.")
        return False

    for i, feature in enumerate(features):
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) != 2:
            print(f"[ERROR] Feature {i} has invalid coordinates: {coords}")
            return False

        lon, lat = coords
        if not (-180 <= lon <= 180):
            print(f"[ERROR] Feature {i} longitude out of range: {lon}")
            return False
        if not (-90 <= lat <= 90):
            print(f"[ERROR] Feature {i} latitude out of range: {lat}")
            return False

    print(f"[OK]   GeoJSON validation passed. {len(features)} valid features.")
    return True


def main():
    print("=" * 60)
    print("  Geo-LLM Spatial RAG Engine — Data Acquisition")
    print("  Fetching hospitals in Swat, Pakistan from OpenStreetMap")
    print("=" * 60)
    print()

    raw_data = fetch_overpass_data(OVERPASS_QUERY)

    geojson = build_geojson(raw_data)

    if not validate_geojson(geojson):
        print("[FATAL] GeoJSON validation failed. Check the data source.")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print()
    print(f"[DONE] Saved {len(geojson['features'])} hospitals to: {OUTPUT_FILE}")

    print("\n--- Sample Feature ---")
    print(json.dumps(geojson["features"][0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
