# Geo-LLM Spatial RAG Engine 🌍

An enterprise-grade Spatial Intelligence Platform designed for the Swat District, Northern Pakistan. This engine translates natural language queries into precise PostGIS spatial analytics, providing real-time infrastructure and hydrology insights.

## 🚀 Key Features

- **Spatial Reasoning**: Handles complex proximity and connectivity queries (e.g., "Hospitals near the Swat River").
- **Premium Command Center**: High-fidelity dashboard built with Next.js 15, Mapbox GL, and Glassmorphism design.
- **Enterprise Security**: Dual-database architecture with restricted read-only access for LLM-generated queries.
- **Localized Context**: Integrated Urdu support (`name_ur`) and custom Location Gazetteer for the Swat region.
- **Self-Healing SQL**: Autonomous retry logic that corrects AI-generated SQL syntax errors.
- **Persistence**: Full chat and map result history stored in PostgreSQL.

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.12+), LangChain, Groq (Llama 3.3 70B).
- **Database**: PostgreSQL 16 + PostGIS 3.4 (Dockerized).
- **Frontend**: Next.js 15, Tailwind CSS, Lucide icons, `react-map-gl`.
- **Infrastructure**: Docker Compose, Mapbox.


## 🏁 Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Node.js 20+](https://nodejs.org/) and NPM.
- [Groq AI API Key](https://console.groq.com/) and [Mapbox Access Token](https://www.mapbox.com/).

### 2. Environment Setup
Create a `.env` file in the root directory (based on `.env.example` if available):
```env
# Backend
database_url=postgresql://postgres:postgres@localhost:5432/geollm
reader_database_url=postgresql://geollm_reader:reader_pass@localhost:5432/geollm
groq_api_key=your_groq_key_here

# Frontend (in frontend/.env.local)
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run the Stack (Windows)
Simply run the startup script:
```powershell
./run.bat
```
This will:
- Spin up the PostGIS database in Docker.
- Initialize the FastAPI backend.
- Start the Next.js development server.
- Open the dashboard at `http://localhost:3000`.
 <img width="1891" height="785" alt="Screenshot 2026-04-13 205058" src="https://github.com/user-attachments/assets/170ea902-34c9-42ef-acbb-89afc7a7b289" />
## 📂 Project Structure

- `/backend`: Core spatial logic, database models, and AI chaining.
- `/frontend`: Responsive dashboard UI and interactive Mapbox canvas.
- `/docker-compose.yml`: Database and spatial extensions orchestration.
- `run.bat`: One-click development runner.

## 📄 License
This project is part of the Jawad Ahmed Spatial Intelligence portfolio.
