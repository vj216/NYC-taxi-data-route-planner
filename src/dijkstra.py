import heapq
import math
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT/"data"

def load_graph():
    G=ox.io.load_graphml(DATA_DIR/"manhattan.graphml")
    # Keeping only the part of the map where every node can reach every other.
    # Cutting a map out of a city can leave one-way dead ends that trap routes.
    return ox.truncate.largest_component(G, strongly=True)

def haversine_m(lat1, lon1, lat2, lon2):
    """Straight-line distance in metres between two lat/lon points."""
    """The Haversine formula calculates the shortest distance between two points on a sphere using their latitudes and longitudes"""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p1 - p2
    dlmb = math.radians(lon2-lon1)
    a = math.sin(dphi/2)** 2 +  math.cos(p1)*math.cos(p2)* math.sin(dlmb/2) **2
    return 2* r* math.asin(math.sqrt(a))

def nearest_node(G, lat, lon):
    """Find the intersection closest to a lat/lon point"""
    return min(G.nodes, key= lambda n: haversine_m(lat, lon, G.nodes[n]["y"], G.nodes[n]["x"]),)

def edge_length(G, u, v):
    """Two nodes can have parallel roads, use the shortest one"""
    return min(data["length"] for data in G[u][v].values())

def dijkstra(G, source, target):
    dist={source: 0.0} #best known distance to each node
    prev = {}
    heap=[(0.0, source)] #priority queue of (distance, node)
    visited = set()

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue # stale entry, we already found a better one
        visited.add(u)
        if u==target:
            break
        for v in G.successors(u): # successors respects one-way streets
            new_d = d+ edge_length(G,u,v)
            if new_d < dist.get(v, math.inf):
                dist[v] = new_d
                prev[v] = u
                heapq.heappush(heap, (new_d, v))

    if target not in dist:
        return None, math.inf, len(visited)

    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return path,dist[target],len(visited)

if __name__ == "__main__":
    G = load_graph()
    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

    start = nearest_node(G, 40.7440, -73.9920)   # near 6th Ave & W 30th St
    end = nearest_node(G, 40.7536, -73.9832)     # near Bryant Park
    print(f"Start node: {start}   End node: {end}")

    path, metres, explored = dijkstra(G, start, end)
    print(f"My Dijkstra: {metres:,.1f} m, {len(path)} nodes, explored {explored} nodes")

    # Check against NetworkX's trusted implementation
    nx_metres = nx.shortest_path_length(G, start, end, weight="length")
    print(f"NetworkX:    {nx_metres:,.1f} m")
    assert math.isclose(metres, nx_metres), "Distances differ, there's a bug!"
    print("Distances match. My Dijkstra is correct.")

    fig, ax = ox.plot.plot_graph_route(
        G,
        path,
        route_color="red",
        route_linewidth=4,
        node_size=0,
        bgcolor="white",
        show=False,
        close=False,
    )
    out = DATA_DIR / "route_dijkstra.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.show()