import joblib
import pandas as pd
from astar import astar
from dijkstra import load_graph, nearest_node, dijkstra
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT/"data"
MODEL = DATA/"travel_time_model.pkl"

def get_route_and_predicted_time(G, model, start_lat, start_lon, end_lat, end_lon, hour=8, dayofweek=8):
    start_node = nearest_node(G,start_lat,start_lon)
    end_node = nearest_node(G, end_lat, end_lon)

    path, dis_m, astar_expl = astar(G, start_node, end_node)
    path, dis_m,dijkstra_expl = dijkstra(G, start_node, end_node)

    if not path:
        return None

    trip_miles = dis_m / 1609.34

    #Prepare input row for the Random Forest model
    # Note: PULocationID and DOLocationID are set to common Manhattan zones (161 / 236)

    sample_input = pd.DataFrame([{
        "trip_miles": trip_miles,
        "pickup_hour": hour,
        "pickup_dayofweek": dayofweek,
        "PULocationID": 161,  # Midtown Center
        "DOLocationID": 236   # Upper East Side / Central
    }])

    predicted_minutes = float(model.predict(sample_input)[0])

    return {
        "start_node": start_node,
        "end_node": end_node,
        "distance_meters": dis_m,
        "distance_miles": trip_miles,
        "predicted_minutes": predicted_minutes,
        "path_node_count": len(path),
        "astar_explored": astar_expl,
        "dijkstra_explored": dijkstra_expl,
        "path": path,
    }

if __name__ == "__main__":
    G = load_graph()

    model = joblib.load(MODEL)

    #Start: near W 30th St & 6th Ave (40.7440, -73.9920)
    # End: near Bryant Park (40.7536, -73.9832)
    start_lat, start_lon = 40.7440, -73.9920
    end_lat, end_lon = 40.7536, -73.9832

    rush = get_route_and_predicted_time(G, model, start_lat, start_lon, end_lat, end_lon, hour=8, dayofweek=0)
    night = get_route_and_predicted_time(G, model, start_lat, start_lon, end_lat, end_lon, hour=2, dayofweek=6)

    print("\n================ ROUTEMIND ROUTE SUMMARY ================")
    print(f"Path Distance:         {rush['distance_meters']:,.1f} m ({rush['distance_miles']:.2f} miles)")
    print(f"Path Length:           {rush['path_node_count']} intersections")
    print(f"Nodes Explored (A*):   {rush['astar_explored']} nodes")
    print(f"Nodes Explored (Dijk): {rush['dijkstra_explored']} nodes")
    print(f"Search Reduction:      {100 * (1 - rush['astar_explored'] / rush['dijkstra_explored']):.0f}% fewer nodes with A*")
    print("---------------------------------------------------------")
    print(f"Monday 8:00 AM (Rush Hour):  {rush['predicted_minutes']:.1f} minutes")
    print(f"Sunday 2:00 AM (Late Night): {night['predicted_minutes']:.1f} minutes")
    print("=========================================================")



