import json
from sqlalchemy import create_engine, text
from backend.config import settings

# Use the ADMIN engine for ingestion
engine = create_engine(settings.database_url)

def ingest_locations():
    with open('locations_data.json', 'r') as f:
        data = json.load(f)

    # 1. Create the locations table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS locations (
        id SERIAL PRIMARY KEY,
        osm_id BIGINT,
        name TEXT,
        type TEXT,
        geom GEOMETRY(Point, 4326)
    );
    CREATE INDEX IF NOT EXISTS locations_geom_idx ON locations USING GIST(geom);
    CREATE INDEX IF NOT EXISTS locations_name_idx ON locations(name);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("Locations table ready.")

    # 2. Process OSM node elements
    nodes = [el for el in data['elements'] if el['type'] == 'node']

    insert_count = 0
    with engine.connect() as conn:
        for node in nodes:
            name = node.get('tags', {}).get('name')
            if not name:
                continue
                
            l_type = node.get('tags', {}).get('place')
            osm_id = node['id']
            lat = node['lat']
            lon = node['lon']

            wkt_point = f"POINT({lon} {lat})"
            
            sql = "INSERT INTO locations (osm_id, name, type, geom) VALUES (:osm_id, :name, :type, ST_GeomFromText(:wkt, 4326))"
            conn.execute(text(sql), {"osm_id": osm_id, "name": name, "type": l_type, "wkt": wkt_point})
            insert_count += 1
        
        conn.commit()
    
    print(f"Successfully ingested {insert_count} named locations.")

if __name__ == "__main__":
    ingest_locations()
