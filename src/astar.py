import heapq
import math
import time
import matplotlib.pyplot as plt
import osmnx as ox

from dijkstra import(
    DATA_DIR,
    dijkstra,
    edge_length,
    haversine_m,
    load_graph,
    nearest_node,
)

def astar(G, source, target):
    ty, tx = G.nodes[target]["y"], G.nodes[target]["x"]
    def h(n):
        return haversine_m(G.nodes[n]["y"], G.nodes[n]["x"], ty, tx)
    g = {source: 0.0}              # real cost so far
    prev = {}
    heap = [(h(source), source)]   # priority = g + h
    visited = set()

    while heap:
        _, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == target:
            break
        for v in G.successors(u):
            new_g = g[u] + edge_length(G, u, v)
            if new_g < g.get(v, math.inf):
                g[v] = new_g
                prev[v] = u
                heapq.heappush(heap, (new_g + h(v), v))

    if target not in g:
        return None, math.inf, len(visited)

    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return path, g[target], len(visited)


if __name__ == "__main__":
    G = load_graph()
    start = nearest_node(G, 40.7440, -73.9920)
    end = nearest_node(G, 40.7536, -73.9832)

    t0 = time.perf_counter()
    d_path, d_m, d_explored = dijkstra(G, start, end)
    t1 = time.perf_counter()
    a_path, a_m, a_explored = astar(G, start, end)
    t2 = time.perf_counter()

    print(f"{'':10}{'metres':>10}{'explored':>10}{'ms':>8}")
    print(f"{'Dijkstra':10}{d_m:>10,.1f}{d_explored:>10}{(t1 - t0) * 1000:>8.2f}")
    print(f"{'A*':10}{a_m:>10,.1f}{a_explored:>10}{(t2 - t1) * 1000:>8.2f}")

    assert math.isclose(d_m, a_m), "A* and Dijkstra disagree, there's a bug!"
    saved = 100 * (1 - a_explored / d_explored)
    print(f"\nSame distance. A* explored {saved:.0f}% fewer nodes.")

    fig, ax = ox.plot.plot_graph_route(
        G,
        a_path,
        route_color="green",
        route_linewidth=4,
        node_size=0,
        bgcolor="white",
        show=False,
        close=False,
    )
    out = DATA_DIR / "route_astar.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.show()