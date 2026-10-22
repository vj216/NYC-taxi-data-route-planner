# Route Planner: AI-Assisted Route & Travel-Time Predictor

Route Planner combines classical graph search algorithms with machine learning to provide intelligent, traffic-aware travel time estimation across real-world road networks.

Unlike traditional routing engines that rely solely on static road limits or generic duration estimates, Route Planner pairs a topological road graph (OpenStreetMap) with a Random Forest regression model trained on 500,000 historical New York City Taxi and Limousine Commission (TLC) trips.

---

## 🏛 System Architecture

The project is structured as a modular, end-to-end pipeline:

```text
[NYC TLC Trip Data]               [OpenStreetMap (OSM)]
        │                                   │
        ▼                                   ▼
 [Data Cleaning & Prep]            [OSMnx Road Graph]
 (500k trips, Parquet)            (Nodes, Edges, Distances)
        │                                   │
        ▼                                   ▼
[Random Forest Regressor]           [Dijkstra vs. A*]
  (MAE: 2.61 min, R²: 0.70)       (Shortest Drivable Path)
        │                                   │
        └─────────────────┬─────────────────┘
                          │
                          ▼
                  [FastAPI REST API]
                  (POST /route)
                          │
                          ▼
               [Minimal Web Frontend]
              (HTML / Vanilla JavaScript)
```

---

## 📊 Key Results & Milestones

### 1. Graph Pathfinding: A* vs. Dijkstra
- **Road Network**: Central Manhattan network extracted via OSMnx (nodes, edges with meter distances, street names, one-way constraints).
- **Comparison**: For an identical 1,268.9-meter (~0.79 mile) path:
  - **Dijkstra's Algorithm**: Explored **96 nodes** (1.39 ms).
  - **A\* Search** (Euclidean distance heuristic): Explored **17 nodes** (0.54 ms).
  - **Result**: A* achieved an **82% reduction in search space** while guaranteeing the exact same optimal distance.

### 2. Travel-Time Estimation Model (Random Forest)
- **Dataset**: 500,000 cleaned Yellow Taxi trips filtered for Manhattan (duration 1–180 min, distance 0.1–50 miles).
- **Features**: `trip_miles`, `pickup_hour`, `pickup_dayofweek`, `PULocationID`, `DOLocationID`.
- **Target**: `duration_min`.
- **Performance**:
  - **Mean Absolute Error (MAE)**: `2.61 minutes` — average prediction error on unseen test data.
  - **Coefficient of Determination (R²)**: `0.698 (~70%)` — explains ~70% of the variance in trip durations.
- **Traffic Sensitivity**: For the exact same 0.79-mile route:
  - **Monday 8:00 AM (Rush Hour)**: ~`6.8 minutes`
  - **Sunday 2:00 AM (Late Night)**: ~`4.6 minutes`
  - Demonstrates a ~48% traffic delay captured directly from empirical city records.

---

## 🖥 Frontend Interface

The current interface is a lightweight, zero-dependency HTML/JavaScript frontend that communicates directly with the FastAPI backend over REST.

- **Inputs**: Departure hour (`0–23`), Departure day (`Monday` through `Sunday`).
- **Displays**: Instant summary of estimated trip duration (minutes), drivable path distance (miles), and an expandable inspector with full route metrics and node-level coordinates.

> **Note on Current Limitations & Future Improvements:**
> - In this initial prototype, pickup (`40.7440, -73.9920`) and dropoff (`40.7536, -73.9832`) coordinates and TLC zone IDs are **hardcoded for testing and baseline validation**.
> - **Planned next update**: Replace static coordinates with:
>   1. **Interactive location selectors** (dropdowns with named landmarks e.g. Madison Square Park, Times Square).
>   2. **Editable latitude/longitude inputs** with geographic bounding-box validation.
>   3. **Interactive map picking** using Leaflet.js.

---

## 📁 Project Structure

```text
NYC-taxi-data/
├── data/
│   ├── trips_sample.parquet      # Sampled NYC TLC trip records (git-ignored)
│   ├── manhattan.graphml         # Downloaded OSMnx street network (git-ignored)
│   └── travel_time_model.pkl     # Trained Random Forest model (git-ignored)
├── frontend/
│   └── index.html                # Minimal web frontend
├── src/
│   ├── downloadmap.py            # OSMnx road graph download script
│   ├── inspect-graph.py          # Graph topology inspection script
│   ├── dijkstra.py               # Custom Dijkstra implementation & validation
│   ├── astar.py                  # Custom A* search implementation
│   ├── model.py                  # Random Forest training & evaluation
│   ├── predict-route.py          # Integrated routing + ML estimation script
│   └── api.py                    # FastAPI server exposing /health and /route
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run the Project

### 1. Activate Environment & Install Dependencies
```powershell
.\.nyc\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the FastAPI Backend
```powershell
python -m uvicorn src.api:app --reload --port 8000
```
- API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Launch the Frontend
In a separate terminal, serve the frontend directory:
```powershell
python -m http.server 5500 --directory frontend
```
Open your browser at [http://localhost:5500](http://localhost:5500) to test departure times and inspect predictions.

---

## 🔮 Roadmap
- [x] OSMnx road network extraction & graph validation
- [x] Dijkstra & A* pathfinding implementation with search reduction benchmarks
- [x] Random Forest ML duration estimation (2.61 min MAE, ~70% R²)
- [x] FastAPI REST service (`POST /route`)
- [x] Minimal working HTML/JS frontend
- [ ] Replace hardcoded coordinates with editable inputs / landmark dropdowns
- [ ] Interactive Leaflet/MapLibre map with route polyline rendering
- [ ] Dynamic edge-weighting (traffic-aware A* routing)
- [ ] Multi-city expansion (e.g. Helsinki road network & local transit/traffic estimates)
