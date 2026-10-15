import time
from pathlib import Path

import matplotlib.pyplot as plt
import osmnx as ox

# ---------- Settings ----------
ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.requests_timeout = 60
ox.settings.overpass_rate_limit = False

OVERPASS_SERVERS = [
    "https://overpass-api.de/api",
    "https://overpass.kumi.systems/api",
    "https://overpass.private.coffee/api",
]
ATTEMPTS_PER_SERVER = 3

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Download ----------
CENTER = (40.7484, -73.9857)

G = None
for server in OVERPASS_SERVERS:
    ox.settings.overpass_url = server
    for attempt in range(1, ATTEMPTS_PER_SERVER + 1):
        print(f"\n>>> {server} (attempt {attempt}/{ATTEMPTS_PER_SERVER})")
        try:
            G = ox.graph.graph_from_point(
                CENTER,
                dist=800,
                dist_type="bbox",   # simple rectangle = lighter query
                network_type="drive",
                simplify=True,
            )
            break
        except Exception as error:
            print(f"!!! Failed: {type(error).__name__}")
            time.sleep(5 * attempt)   # wait 5 s, then 10 s, then 15 s
    if G is not None:
        break

if G is None:
    raise SystemExit("All servers and retries failed.")

print("\nDownload succeeded.")
print(f"Number of intersections/nodes: {len(G.nodes):,}")
print(f"Number of road connections/edges: {len(G.edges):,}")

output_file = DATA_DIR / "manhattan.graphml"
ox.io.save_graphml(G, filepath=output_file)
print(f"Road network saved to: {output_file}")

# ---------- Draw ----------
fig, ax = ox.plot.plot_graph(
    G,
    node_size=0,
    edge_color="steelblue",
    edge_linewidth=0.8,
    bgcolor="white",
    show=False,
    close=False,
)

map_file = DATA_DIR / "manhattan_roads.png"
fig.savefig(map_file, dpi=200, bbox_inches="tight")
print(f"Map image saved to: {map_file}")

plt.show()