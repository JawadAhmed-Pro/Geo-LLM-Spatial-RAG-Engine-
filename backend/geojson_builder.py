import json
from shapely import wkb

def results_to_geojson(db_results: list[dict]) -> dict:
    """
    Converts database results into a standard GeoJSON FeatureCollection.
    Expects geometry data to be in WKB or PostGIS extended format.
    To make things robust, the LLM should generate SQL like:
    SELECT name, amenity, properties, ST_AsGeoJSON(geom) as geom_json FROM infrastructure
    """
    features = []
    
    for row in db_results:
        properties = {}
        geometry = None
        
        for key, value in row.items():
            if key == "geom_json" and value:
                try:
                    geometry = json.loads(value)
                except json.JSONDecodeError:
                    pass
            elif key == "geom" and value:
                # If they didn't use ST_AsGeoJSON, attempt WKB parsing (if returned as hex string)
                if isinstance(value, str):
                    try:
                        # Sometimes PostGIS returns hex string
                        geom_obj = wkb.loads(value, hex=True)
                        geometry = {
                            "type": geom_obj.geom_type,
                            "coordinates": list(geom_obj.coords)
                        }
                    except Exception:
                        pass
            elif key == "properties" and isinstance(value, dict):
                 # Merge existing parsed JSON properties
                 properties.update(value)
            else:
                 properties[key] = value

        if geometry:
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
