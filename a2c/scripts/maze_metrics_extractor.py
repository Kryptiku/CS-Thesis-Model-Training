import argparse
import csv
import heapq
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


class MazeGenerator:
    """Isolated copy of the maze generator used in the main training script."""

    def __init__(self, size=20, seed_type="PRNG"):
        self.size = size
        self.seed_type = seed_type

    def generate(self, seed=None):
        maze = np.ones((self.size, self.size), dtype=int)
        if seed is not None:
            random.seed(seed)
        elif self.seed_type == "PRNG":
            random.seed(None)

        def carve(x, y):
            maze[y, x] = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < self.size and 0 <= ny < self.size and maze[ny, nx] == 1:
                    maze[y + dy, x + dx] = 0
                    carve(nx, ny)

        carve(1, 1)
        maze[1, 1] = 0
        maze[self.size - 2, self.size - 2] = 0
        return maze


def load_seeds(seed_csv_path, seed_column="number", limit=None):
    df = pd.read_csv(seed_csv_path)
    if seed_column not in df.columns:
        raise ValueError(
            f"Column '{seed_column}' not found in {seed_csv_path}. "
            f"Available columns: {list(df.columns)}"
        )

    seeds = []
    for raw_value in df[seed_column].tolist():
        if pd.isna(raw_value):
            continue
        seeds.append(int(raw_value))

    if limit is not None:
        seeds = seeds[:limit]

    if not seeds:
        raise ValueError("No valid seeds found after parsing the seed CSV.")

    return seeds


def get_open_cells(maze):
    ys, xs = np.where(maze == 0)
    return {(int(y), int(x)) for y, x in zip(ys, xs)}


def build_cell_graph(maze):
    open_cells = get_open_cells(maze)
    neighbors = {cell: [] for cell in open_cells}

    for y, x in open_cells:
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if (ny, nx) in open_cells:
                neighbors[(y, x)].append((ny, nx))

    undirected_edges = sum(len(v) for v in neighbors.values()) // 2
    return neighbors, len(open_cells), undirected_edges


def dijkstra_shortest_path(cell_graph, start, goal):
    if start not in cell_graph or goal not in cell_graph:
        return float("inf"), []

    pq = [(0, start)]
    dist = {start: 0}
    prev = {}
    visited = set()

    while pq:
        curr_dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            break

        for nb in cell_graph[node]:
            nd = curr_dist + 1
            if nd < dist.get(nb, float("inf")):
                dist[nb] = nd
                prev[nb] = node
                heapq.heappush(pq, (nd, nb))

    if goal not in dist:
        return float("inf"), []

    path = [goal]
    node = goal
    while node != start:
        node = prev[node]
        path.append(node)
    path.reverse()
    return dist[goal], path


def _turn_count_on_chain(chain_nodes):
    """
    Count direction changes along a node chain.
    chain_nodes includes both endpoints in traversal order.
    """
    if len(chain_nodes) < 3:
        return 0

    turns = 0
    prev_dir = None
    for i in range(1, len(chain_nodes)):
        y0, x0 = chain_nodes[i - 1]
        y1, x1 = chain_nodes[i]
        cur_dir = (y1 - y0, x1 - x0)
        if prev_dir is not None and cur_dir != prev_dir:
            turns += 1
        prev_dir = cur_dir
    return turns


def collapse_to_corridor_graph(cell_graph, start, goal):
    # Core nodes: non-degree-2 cells, plus forced start/goal anchors.
    core_nodes = {node for node, nbs in cell_graph.items() if len(nbs) != 2}
    if start in cell_graph:
        core_nodes.add(start)
    if goal in cell_graph:
        core_nodes.add(goal)

    adjacency = defaultdict(set)
    corridor_edges = []
    seen_directed = set()

    for core in core_nodes:
        for nb in cell_graph[core]:
            directed_key = (core, nb)
            if directed_key in seen_directed:
                continue

            chain = [core, nb]
            prev = core
            curr = nb
            seen_directed.add((core, nb))

            while curr not in core_nodes:
                next_candidates = [n for n in cell_graph[curr] if n != prev]
                if not next_candidates:
                    break
                nxt = next_candidates[0]
                chain.append(nxt)
                seen_directed.add((curr, nxt))
                prev, curr = curr, nxt

            end_core = curr
            if end_core not in core_nodes:
                continue

            length = len(chain) - 1
            turns = _turn_count_on_chain(chain)
            edge_key = tuple(sorted([core, end_core]))

            # Avoid duplicate undirected corridor edges.
            if any(existing["edge_key"] == edge_key for existing in corridor_edges):
                continue

            corridor_edges.append(
                {
                    "u": core,
                    "v": end_core,
                    "length": length,
                    "turns": turns,
                    "is_straight": int(turns == 0),
                    "edge_key": edge_key,
                }
            )
            adjacency[core].add(end_core)
            adjacency[end_core].add(core)

    for node in core_nodes:
        adjacency[node] = adjacency[node]

    corridor_degrees = {node: len(nbs) for node, nbs in adjacency.items()}

    dead_end_count = sum(1 for d in corridor_degrees.values() if d == 1)
    junction_nodes = [node for node, d in corridor_degrees.items() if d >= 3]
    junction_count = len(junction_nodes)
    degree3_count = sum(1 for d in corridor_degrees.values() if d == 3)
    degree4_count = sum(1 for d in corridor_degrees.values() if d == 4)

    if junction_count > 0:
        p3 = degree3_count / junction_count
        p4 = degree4_count / junction_count
    else:
        p3 = 0.0
        p4 = 0.0

    straight_corridors = sum(e["is_straight"] for e in corridor_edges)
    turning_corridors = len(corridor_edges) - straight_corridors
    turns_total = sum(e["turns"] for e in corridor_edges)
    mean_turns = turns_total / len(corridor_edges) if corridor_edges else 0.0

    return {
        "corridor_nodes": len(corridor_degrees),
        "corridor_edges": len(corridor_edges),
        "dead_end_count": dead_end_count,
        "junction_count": junction_count,
        "degree3_count": degree3_count,
        "degree4_count": degree4_count,
        "p3": p3,
        "p4": p4,
        "straight_corridors": straight_corridors,
        "turning_corridors": turning_corridors,
        "turns_total": turns_total,
        "mean_turns_per_corridor": mean_turns,
    }


def iqr(values):
    if len(values) == 0:
        return np.nan
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    return float(q3 - q1)


def summarize_metrics(df):
    rows = []

    def add_stats(metric_name, series, include_std=False):
        clean = series.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
        row = {
            "metric": metric_name,
            "count": int(clean.shape[0]),
            "mean": float(clean.mean()) if len(clean) else np.nan,
            "median": float(clean.median()) if len(clean) else np.nan,
            "iqr": iqr(clean.values) if len(clean) else np.nan,
        }
        if include_std:
            row["std"] = float(clean.std(ddof=1)) if len(clean) > 1 else np.nan
        rows.append(row)

    add_stats("shortest_path_len", df["shortest_path_len"])
    add_stats("tortuosity", df["tortuosity"])
    add_stats("dead_end_count", df["dead_end_count"], include_std=True)
    add_stats("p3", df["p3"])
    add_stats("p4", df["p4"])
    add_stats("mean_turns_per_corridor", df["mean_turns_per_corridor"])

    return pd.DataFrame(rows)


def extract_metrics_for_seed(generator, seed, size):
    maze = generator.generate(seed=seed)
    start = (1, 1)
    goal = (size - 2, size - 2)

    cell_graph, cell_nodes, cell_edges = build_cell_graph(maze)

    shortest_path_len, shortest_path_nodes = dijkstra_shortest_path(cell_graph, start, goal)
    manhattan = abs(goal[0] - start[0]) + abs(goal[1] - start[1])

    if np.isfinite(shortest_path_len) and manhattan > 0:
        tortuosity = float(shortest_path_len / manhattan)
    else:
        tortuosity = np.nan

    corridor = collapse_to_corridor_graph(cell_graph, start, goal)

    return {
        "seed": int(seed),
        "size": int(size),
        "start_y": start[0],
        "start_x": start[1],
        "goal_y": goal[0],
        "goal_x": goal[1],
        "cell_nodes": cell_nodes,
        "cell_edges": cell_edges,
        "corridor_nodes": corridor["corridor_nodes"],
        "corridor_edges": corridor["corridor_edges"],
        "shortest_path_len": float(shortest_path_len) if np.isfinite(shortest_path_len) else np.nan,
        "shortest_path_nodes": len(shortest_path_nodes),
        "manhattan_distance": int(manhattan),
        "tortuosity": tortuosity,
        "dead_end_count": corridor["dead_end_count"],
        "junction_count": corridor["junction_count"],
        "degree3_count": corridor["degree3_count"],
        "degree4_count": corridor["degree4_count"],
        "p3": corridor["p3"],
        "p4": corridor["p4"],
        "straight_corridors": corridor["straight_corridors"],
        "turning_corridors": corridor["turning_corridors"],
        "turns_total": corridor["turns_total"],
        "mean_turns_per_corridor": corridor["mean_turns_per_corridor"],
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate mazes from a seed CSV and extract structural metrics to CSV."
    )
    parser.add_argument(
        "--seeds",
        required=True,
        help="Path to seed CSV (e.g., prng_seeds.csv or qrng_seeds.csv).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path for per-maze metrics.",
    )
    parser.add_argument(
        "--summary-output",
        default=None,
        help="Optional output CSV path for aggregate summary stats.",
    )
    parser.add_argument(
        "--seed-column",
        default="number",
        help="Seed column name in the seed CSV. Default: number",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=20,
        help="Maze size (must match the generator setup). Default: 20",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of seeds to process.",
    )
    parser.add_argument(
        "--seed-type",
        default="PRNG",
        help="Generator seed_type passthrough (kept for parity with main).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    seeds_path = Path(args.seeds)
    output_path = Path(args.output)

    if args.summary_output is None:
        summary_output_path = output_path.with_name(f"{output_path.stem}_summary.csv")
    else:
        summary_output_path = Path(args.summary_output)

    seeds = load_seeds(seeds_path, seed_column=args.seed_column, limit=args.limit)
    generator = MazeGenerator(size=args.size, seed_type=args.seed_type)

    records = []
    for idx, seed in enumerate(seeds, start=1):
        rec = extract_metrics_for_seed(generator, seed, size=args.size)
        records.append(rec)

        if idx % 100 == 0 or idx == len(seeds):
            print(f"Processed {idx}/{len(seeds)} seeds")

    metrics_df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)

    summary_df = summarize_metrics(metrics_df)
    summary_output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_output_path, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"Saved per-maze metrics: {output_path}")
    print(f"Saved summary metrics: {summary_output_path}")


if __name__ == "__main__":
    main()
