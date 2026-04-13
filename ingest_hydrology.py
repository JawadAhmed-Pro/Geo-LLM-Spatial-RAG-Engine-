import json
import psycopg2
from sqlalchemy import create_engine, text
from backend.config import settings

# Use the ADMIN engine for ingestion
engine = create_engine(settings.database_url)

def ingest_hydrology():
    with open('hydrology_data.json', 'r') as f:
        data = json.load(f)

    # 1. Create the hydrology table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS hydrology (
        id SERIAL PRIMARY KEY,
        osm_id BIGINT,
        name TEXT,
        type TEXT,
        geom GEOMETRY(LineString, 4326)
    );
    CREATE INDEX IF NOT EXISTS hydrology_geom_idx ON hydrology USING GIST(geom);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("Hydrology table ready.")

    # 2. Process OSM elements into LineStrings
    # We need to map nodes to coordinates first
    nodes = {el['id']: (el['lon'], el['lat']) for el in data['elements'] if el['type'] == 'node'}
    ways = [el for el in data['elements'] if el['type'] == 'way']

    insert_count = 0
    with engine.connect() as conn:
        for way in ways:
            way_nodes = way.get('nodes', [])
            if len(way_nodes) < 2:
                continue
            
            coords = []
            valid = True
            for node_id in way_nodes:
                if node_id in nodes:
                    lon, lat = nodes[node_id]
                    coords.append(f"{lon} {lat}")
                else:
                    valid = False
                    break
            
            if not valid:
                continue
                
            wkt_line = f"LINESTRING({', '.join(coords)})"
            name = way.get('tags', {}).get('name', 'Unnamed Stream')
            w_type = way.get('tags', {}).get('waterway', 'river')
            osm_id = way['id']

            sql = "INSERT INTO hydrology (osm_id, name, type, geom) VALUES (:osm_id, :name, :type, ST_GeomFromText(:wkt, 4326))"
            conn.execute(text(sql), {"osm_id": osm_id, "name": name, "type": w_type, "wkt": wkt_line})
            insert_count += 1
        
        conn.commit()
    
    print(f"Successfully ingested {insert_count} river segments.")

if __name__ == "__main__":
    ingest_hydrology()
