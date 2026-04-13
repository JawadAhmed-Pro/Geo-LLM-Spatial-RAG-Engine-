"""
Phase 1: Database Setup
Reads the generated swat_hospitals.geojson and ingests it into PostGIS
using SQLAlchemy and GeoPandas.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

# Make sure we're reading the db url correctly; default matches docker-compose
DATABASE_URL = "postgresql://geollm:geollm_secret@localhost:5432/geollm"

engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    amenity = Column(String)
    # Using SRID 4326 (WGS 84) to match standard GeoJSON Lon/Lat
    geom = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True))
    properties = Column(JSONB)


def main():
    print("=" * 60)
    print("  Geo-LLM Spatial RAG Engine — Database Ingestion")
    print("=" * 60)
    print()

    geojson_path = Path(__file__).parent / "swat_hospitals.geojson"
    if not geojson_path.exists():
        print(f"[FATAL] GeoJSON file not found: {geojson_path}")
        print("Please run `python fetch_data.py` first.")
        sys.exit(1)

    print("[INFO] Creating database engine...")
    try:
        # Test connection and create tables
        Base.metadata.create_all(engine)
        print("[OK]   Connected to PostGIS and created tables.")
    except Exception as exc:
        print("[FATAL] Database connection failed.")
        print(f"Make sure you ran `docker compose up -d`.\nError: {exc}")
        sys.exit(1)

    print(f"[INFO] Reading {geojson_path}...")
    
    # Read GeoJSON using GeoPandas
    gdf = gpd.read_file(geojson_path)
    
    # For hospitals where name might be missing
    if "name" not in gdf.columns:
        gdf["name"] = "Unknown"
    if "amenity" not in gdf.columns:
        gdf["amenity"] = "hospital"

    print(f"[OK]   Loaded {len(gdf)} features into memory.")

    # Convert remaining columns to JSONB properties
    skip_cols = {"geometry", "name", "amenity"}
    prop_cols = [c for c in gdf.columns if c not in skip_cols]

    print("[INFO] Formatting data for PostGIS insertion...")
    insertion_list = []
    
    for idx, row in gdf.iterrows():
        # Build properties dict
        props = {}
        for col in prop_cols:
            val = row[col]
            if val is not None and str(val) != "nan":
                 props[col] = val
                 
        # Format geometry into WKT (Well-Known Text) for GeoAlchemy2 to parse
        geom_wkt = f"SRID=4326;{row.geometry.wkt}"
        
        name_val = row["name"] if str(row["name"]) != "nan" else "Unknown"

        record = {
            "name": name_val,
            "amenity": row.get("amenity", "hospital"),
            "geom": geom_wkt,
            "properties": props
        }
        insertion_list.append(record)

    print("[INFO] Writing to the infrastructure table...")
    
    # We clear existing table for the PoC to be idempotent
    with engine.begin() as conn:
        conn.execute(Infrastructure.__table__.delete())
        print("[OK]   Cleared existing data.")
        conn.execute(Infrastructure.__table__.insert(), insertion_list)

    print(f"[DONE] Successfully ingested {len(insertion_list)} records.")

if __name__ == "__main__":
    main()
