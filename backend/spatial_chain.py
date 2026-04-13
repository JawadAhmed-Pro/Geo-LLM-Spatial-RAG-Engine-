import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .config import settings
from .sql_validator import is_safe_sql
from .database import execute_read_only_query
from .geojson_builder import results_to_geojson


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.groq_api_key,
    temperature=0.0
)

# --- PASS 1: SQL GENERATION ---
SQL_SYSTEM_PROMPT = """
You are a Geospatial Database Expert for the "Geo-LLM Spatial Engine". Your goal is to translate the user's natural language question into a safe, valid PostGIS SELECT query.

Database Context:
The 'infrastructure' table contains spatial data specifically for the Swat District in Northern Pakistan. Assume the user is always asking about this region. 

Database Schema:
Table: infrastructure
Columns:
- id, name, name_ur, amenity, properties, geom (Point)
- `name` is English, `name_ur` is Urdu. Use both when available.

Table: locations
Columns:
- id, name, type, geom (Point)
- For resolving landmarks like 'Mingora'.

CRITICAL INSTRUCTIONS:
1. ONLY return a SELECT query. 
2. The coordinate system is SRID 4326.
3. Use proper parentheses for logical precedence: `WHERE amenity='hospital' AND (ST_DWithin(...) OR ST_DWithin(...))`.
4. Use meters for distance: `ST_DWithin(geom::geography, ..., 1000)`.
5. For "between [Place A] and [Place B]", use this pattern:
   `SELECT infra.*, ST_AsGeoJSON(infra.geom) AS geom_json FROM infrastructure infra WHERE infra.amenity = 'hospital' AND ST_DWithin(infra.geom::geography, ST_MakeLine((SELECT geom FROM locations WHERE name='A'), (SELECT geom FROM locations WHERE name='B'))::geography, 500)`

Example Query for "Hospitals between Mingora and Kalam":
```json
{
  "sql": "SELECT infra.*, ST_AsGeoJSON(infra.geom) AS geom_json FROM infrastructure infra WHERE infra.amenity = 'hospital' AND ST_DWithin(infra.geom::geography, ST_MakeLine((SELECT geom FROM locations WHERE name='Mingora'), (SELECT geom FROM locations WHERE name='Kalam'))::geography, 1000)",
  "thought": "Using ST_MakeLine to create a corridor between the two cities and searching within 1km of that line."
}
```

6. Always select `ST_AsGeoJSON(geom) AS geom_json`.
7. You must output valid JSON.
"""

sql_prompt = ChatPromptTemplate.from_messages([
    ("system", SQL_SYSTEM_PROMPT),
    ("user", "{question}")
])

# --- PASS 1.5: SQL CORRECTION ---
CORRECTION_SYSTEM_PROMPT = SQL_SYSTEM_PROMPT + """

URGENT: Your previous SQL query failed with the following error:
{error_message}

The faulty SQL was:
{faulty_sql}

Please fix the error and provide a corrected, valid PostGIS SELECT query.
"""

correction_prompt = ChatPromptTemplate.from_messages([
    ("system", CORRECTION_SYSTEM_PROMPT),
    ("user", "{question}")
])

sql_chain = sql_prompt | llm | JsonOutputParser()
correction_chain = correction_prompt | llm | JsonOutputParser()

# --- PASS 2: SUMMARY GENERATION ---
SUMMARY_SYSTEM_PROMPT = """
You are a friendly Geospatial Assistant. Based on the user's question and the actual database results provided below, write a helpful, concise summary.

Rules:
1. If results exist, mention a few specific names (e.g. "I found 5 hospitals, including [Name 1] and [Name 2].")
2. Always refer to the map (e.g. "You can see their locations highlighted on the map.")
3. Stay helpful and professional.
4. If no results found, explain clearly.

User Question: {question}
Database Results: {results_json}
"""

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", SUMMARY_SYSTEM_PROMPT),
    ("user", "Please summarize these results.")
])

summary_chain = summary_prompt | llm | StrOutputParser()

def process_spatial_query(user_question: str) -> dict:
    max_retries = 2
    retry_count = 0
    last_error = None
    sql_query = None

    while retry_count < max_retries:
        # 1. Generate SQL
        try:
            if retry_count == 0:
                sql_response = sql_chain.invoke({"question": user_question})
            else:
                sql_response = correction_chain.invoke({
                    "question": user_question,
                    "error_message": last_error,
                    "faulty_sql": sql_query
                })
            
            sql_query = sql_response.get("sql", "").strip()
        except Exception as e:
            return {"answer": f"AI Generation Error: {str(e)}", "sql": None, "geojson": None}
        
        if not sql_query:
            return {"answer": "I couldn't generate a query.", "sql": None, "geojson": None}

        # 2. Validate SQL
        is_safe, reason = is_safe_sql(sql_query)
        if not is_safe:
            return {"answer": f"Security Block: {reason}", "sql": sql_query, "geojson": None}

        # 3. Execute SQL
        try:
            results = execute_read_only_query(sql_query)
            break # Success! Exit the retry loop
        except Exception as e:
            last_error = str(e)
            retry_count += 1
            if retry_count >= max_retries:
                return {
                    "answer": f"Database error after {max_retries} attempts: {last_error}",
                    "sql": sql_query,
                    "geojson": None
                }

    # 4. Generate Summary & Stats
    summarizable_results = []
    amenity_counts = {}
    total_found = len(results)
    
    for r in results:
        try:
            row_dict = dict(r._mapping) if hasattr(r, "_mapping") else dict(r)
            
            # Statistics Gathering
            amenity = row_dict.get("amenity", "other")
            amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1
            
            # Use name or amenity as a label for the AI
            display_name = row_dict.get("name") or row_dict.get("name_ur") or f"Unnamed {amenity}"
            
            # Add to summarizable list (Don't filter anymore, just label better)
            simplified_row = {
                "label": display_name,
                "type": amenity
            }
            summarizable_results.append(simplified_row)
        except:
            continue
    
    results_for_ai = json.dumps(summarizable_results[:15])
    
    try:
        final_answer = summary_chain.invoke({
            "question": user_question,
            "results_json": results_for_ai
        })
    except Exception as e:
        final_answer = f"Search complete. I found {total_found} facilities in this specific area."

    # 5. Convert to GeoJSON
    geojson_collection = results_to_geojson(results)
    
    return {
        "answer": final_answer,
        "sql": sql_query,
        "geojson": geojson_collection,
        "stats": {
            "count": total_found,
            "amenity_breakdown": amenity_counts,
            "region": "Swat District"
        }
    }
