# Product Requirements Document (PRD)

**Project Name:** Geo-LLM Spatial RAG Engine (AI Geo PoC)
**Target Market:** Enterprise Climate Intelligence & Spatial Decision Support
**Primary Objective:** Deliver a high-performance web application that translates natural language queries into PostGIS spatial SQL, rendering real-time climate hazard data on an interactive map interface.

---

## 1. System Architecture & Tech Stack

| Layer | Technology |
|---|---|
| **Database** | PostgreSQL with PostGIS extension (Deployed locally via Docker) |
| **Backend Framework** | Python / FastAPI |
| **AI Orchestration** | LangChain / LangGraph |
| **LLM Inference** | Groq API (Llama 3.3 70B for near-instant Text-to-SQL) |
| **Frontend Framework** | Next.js (React) with Tailwind CSS |
| **Geospatial Visualization** | React Map GL (Mapbox wrapper) |

---

## 2. Core Feature Specifications

### Feature A: The Spatial Brain (Text-to-SQL Pipeline)

**Description:** The system must accept a user's natural language question and securely translate it into a valid PostGIS query.

**Requirements:**
- Must utilize LangChain's SQL Agent or a custom chains workflow.
- Must inject the database schema (table names, geometric column types) into the LLM context automatically.
- Must validate the SQL query before execution to prevent destructive commands (Read-Only access).
- The backend must return both the human-readable text answer AND the raw GeoJSON data resulting from the SQL query.

### Feature B: The "Command Center" UI

**Description:** A split-screen web interface featuring a chat panel and a dynamic map.

**Requirements:**
- **Theme:** Dark mode by default (Dark Mapbox style, charcoal UI).
- **Chat Panel (Left):** Real-time streaming text (SSE) from the FastAPI backend.
- **Map Canvas (Right):** Interactive map initialized to northern Pakistan (Swat coordinates).
- **Dynamic Actions:** When the backend returns GeoJSON data, the map must automatically ingest it as a new layer, draw polygons, drop markers, and smoothly animate the camera to fit the data bounds.

---

## 3. Execution Plan (Prompt Modules)

### Phase 0: Automated Data Acquisition (Run First)

Create a `fetch_data.py` script using the `requests` library to query the Overpass API (`http://overpass-api.de/api/interpreter`). The Overpass QL query should search the area **Swat** and find all nodes, ways, and relations where `amenity=hospital`. Format the response into a valid GeoJSON FeatureCollection (ensuring coordinates are `[lon, lat]`) and save it locally as `swat_hospitals.geojson`. Execute this script to generate the file.

### Phase 1: Database Setup (The Foundation)

Create a `docker-compose.yml` file that sets up a PostgreSQL database with the PostGIS extension. Once running, write a Python script using `sqlalchemy` and `geopandas` that creates a table named `infrastructure` (Geometry Type: Point). The script should read the `swat_hospitals.geojson` file generated in the previous step and insert all features into this new PostGIS table.

### Phase 2: The FastAPI & LangChain Backend (The Brain)

Initialize a FastAPI project. Create an endpoint `/api/chat` that accepts a user string. Implement a LangChain workflow that connects to the local PostGIS database (from Phase 1). Use the Groq API (Llama 3) to translate the user's string into a PostGIS SQL query targeting the `infrastructure` table. Execute the query, format the result into a valid GeoJSON FeatureCollection, and return it alongside a natural language summary.

### Phase 3: The Next.js Command Center (The Interface)

Initialize a Next.js frontend with Tailwind CSS. Create a split-screen dashboard layout. The left side should be a chat interface that communicates with the FastAPI `/api/chat` endpoint. The right side should integrate `react-map-gl` using a dark theme. When the chat API returns a GeoJSON FeatureCollection, dynamically render it on the map as a new point layer and animate the map's viewport to bound the new data.

---

## 4. Key Constraints

- **Coordinate Format:** All GeoJSON must use `[Longitude, Latitude]` order.
- **SQL Safety:** All LLM-generated SQL must be validated as read-only before execution.
- **Incremental Build:** Each phase must be tested and verified before proceeding to the next.
