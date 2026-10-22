import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from astar import astar, load_graph, nearest_node
from dijkstra import dijkstra


app = FastAPI(
    title="RouteMind API",
    description="Graph routing with ML travel-time estimation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


GRAPH_PATH = SRC_DIR.parent / "data" / "manhattan_graph.graphml"
MODEL_PATH = SRC_DIR.parent / "data" / "travel_time_model.pkl"

G = load_graph()

model = None
if MODEL_PATH.exists():
    model = joblib.load(MODEL_PATH)
    print("ML model loaded successfully.")
else:
    print("ML model not found")



class RouteRequest(BaseModel):
    start_lat: float = Field(default=40.7440, description="Start latitude")
    start_lon: float = Field(default=-73.9920, description="Start longitude")
    end_lat: float = Field(default=40.7536, description="End latitude")
    end_lon: float = Field(default=-73.9832, description="End longitude")
    pickup_hour: int = Field(default=8, ge=0, le=23, description="Hour of day (0-23)")
    pickup_dayofweek: int = Field(default=0, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    PULocationID: int = Field(default=161, description="TLC Pickup Zone ID")
    DOLocationID: int = Field(default=236, description="TLC Dropoff Zone ID")



# --- Endpoints ---
@app.get("/")
def root():
    return {
        "message": "Welcome to RouteMind API",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "model_loaded": model is not None,
    }


@app.post("/route")
def calculate_route(req: RouteRequest):
    # 1. Snap coordinates to nearest graph intersections
    start_node = nearest_node(G, req.start_lat, req.start_lon)
    end_node = nearest_node(G, req.end_lat, req.end_lon)

    if start_node == end_node:
        raise HTTPException(status_code=400, detail="Start and end locations snap to the same node.")

    # 2. Run A* 
    path, dist_meters, astar_explored = astar(G, start_node, end_node)
    if not path:
        raise HTTPException(status_code=404, detail="No route found between selected points.")

    # 3. Also run Dijkstra to report search efficiency comparison
    _, _, dijk_explored = dijkstra(G, start_node, end_node)
    reduction_pct = round((1 - astar_explored / dijk_explored) * 100, 1) if dijk_explored > 0 else 0.0

    # 4. Convert meters to miles for the ML model
    trip_miles = dist_meters / 1609.34

    # 5. Predict travel time using the trained Random Forest model
    predicted_minutes = None
    if model is not None:
        features = pd.DataFrame([{
            "trip_miles": trip_miles,
            "pickup_hour": req.pickup_hour,
            "pickup_dayofweek": req.pickup_dayofweek,
            "PULocationID": 161,  # Midtown Center default zone
            "DOLocationID": 236,  # Upper East Side default zone
        }])
        predicted_minutes = round(float(model.predict(features)[0]), 2)

    # 6. Extract coordinate sequence for rendering on maps
    route_coords = [
        {"lat": G.nodes[n]["y"], "lon": G.nodes[n]["x"]}
        for n in path
    ]

    return {
        "distance_meters": round(dist_meters, 1),
        "distance_miles": round(trip_miles, 2),
        "predicted_minutes": predicted_minutes,
        "nodes_in_path": len(path),
        "astar_nodes_explored": astar_explored,
        "dijkstra_nodes_explored": dijk_explored,
        "search_reduction_percent": reduction_pct,
        "route_coordinates": route_coords,
    }
