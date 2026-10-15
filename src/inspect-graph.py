from pathlib import Path
import osmnx as ox

PROJECT_ROOT = Path(__file__).resolve().parents[1]
G= ox.io.load_graphml(PROJECT_ROOT/"data"/"manhattan.graphml")

print(f"Nodes:{len(G.nodes):,} Edges:{len(G.edges):,}")

#One intersection (node)
node_id = list(G.nodes)[0]
print("\nOne node:", node_id)
print(G.nodes[node_id])

#One road segment (edge)
u, v,key,data = list(G.edges(keys= True, data= True))[0]
print(f"\nOne edge: {u}->{v}")
print("name: ", data.get("name"))
print("length: ",data.get("length"),"metres")
print("oneway", data.get("oneway"))
print("highway", data.get("highway"))