import argparse
import os
import random
import time
import json
from tqdm import tqdm
from statistics import mean

from config import Global_Seed
from utils.map_utils import load_full_map
from gridworld import GridWorld
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics

# Define filepaths for each benchmark map
BENCHMARK_MAP_PATHS = {
    "easy": "src/data/maps/map_easy.json",
    "medium": "src/data/maps/map_medium.json",
    "true_maze": "src/data/maps/map_true_maze.json"
}

DEFAULT_DEPTH_RANGE = (5, 35)
DEFAULT_NOISE_RANGE = (0, 10)


def run_simulation(agent_type, grid, start, end, depth=None, noise=None, seed=None, benchmark_name=None):
    """
    Runs a single simulation with the specified agent and parameters.

    Records the result to a CSV file using Log_Path_Metrics and returns summary info.

    Returns:
        dict: Contains success status, path length, nodes explored, search time, and seed used.
    """
    if seed is not None:
        random.seed(seed)

    start_time = time.perf_counter()

    if agent_type == "depth":
        path, explored = A_Star_Search(grid, start, end, Max_Depth=depth)
    elif agent_type == "noise":
        path, explored = A_Star_Search(grid, start, end, Noise_Level=noise)
    else:
        path, explored = A_Star_Search(grid, start, end)

    end_time = time.perf_counter()
    duration = end_time - start_time

    success = path is not None and len(path) >= 2

    Log_Path_Metrics(
        grid=grid,
        start=start,
        end=end,
        path=path if success else None,
        Agent_Type=agent_type,
        Noise_Level=noise,
        Max_Depth=depth,
        Success=success,
        Nodes_Explored=explored,
        Search_Time=duration,
        is_benchmark=True,
        benchmark_name=benchmark_name,
        seed=seed
    )

    return {
        "seed": seed,
        "success": success,
        "path_length": len(path) if path else -1,
        "nodes_explored": explored,
        "search_time_sec": round(duration, 6)
    }


def run_batch(args):
    """
    Runs a full batch of benchmark simulations for the given agent and settings.

    Aggregates and prints performance metrics, and saves them as a JSON summary.
    """
    benchmark_path = BENCHMARK_MAP_PATHS[args.benchmark]
    map_data = load_full_map(benchmark_path)

    grid_data = map_data["grid"]
    start = tuple(map_data["start"])
    end = tuple(map_data["end"])
    rows, cols = len(grid_data), len(grid_data[0])

    print(f"\n[~] Starting benchmark for agent: {args.agent} | Map: {args.benchmark} | Runs: {args.runs}")

    summary_results = []

    # Loop for depth-limited agent
    if args.agent == "depth":
        for depth in range(args.min_depth, args.max_depth + 1):
            print(f"  [Depth = {depth}]")
            for run_id in tqdm(range(args.runs), desc="    Runs", leave=False):
                grid = GridWorld(cols, rows)
                grid.grid = [row[:] for row in grid_data]
                seed = (args.seed or 0) + depth * 1000 + run_id
                result = run_simulation("depth", grid.grid, start, end, depth=depth, seed=seed, benchmark_name=args.benchmark)
                summary_results.append(result)

    # Loop for noisy heuristic agent
    elif args.agent == "noise":
        for noise in range(args.min_noise, args.max_noise + 1):
            print(f"  [Noise = {noise}]")
            for run_id in tqdm(range(args.runs), desc="    Runs", leave=False):
                grid = GridWorld(cols, rows)
                grid.grid = [row[:] for row in grid_data]
                seed = (args.seed or 0) + noise * 1000 + run_id
                result = run_simulation("noise", grid.grid, start, end, noise=noise, seed=seed, benchmark_name=args.benchmark)
                summary_results.append(result)

    # Loop for dynamic environment agent
    elif args.agent == "dynamic":
        for run_id in tqdm(range(args.runs), desc="  Dynamic Runs"):
            grid = GridWorld(cols, rows)
            grid.grid = [row[:] for row in grid_data]
            seed = (args.seed or 0) + run_id
            result = run_simulation("dynamic", grid.grid, start, end, seed=seed, benchmark_name=args.benchmark)
            summary_results.append(result)

    print("\n[✓] Benchmark complete!")

    # Aggregate results
    successes = [r for r in summary_results if r["success"]]
    avg_path_len = round(mean([r["path_length"] for r in successes]), 2) if successes else 0
    avg_nodes = round(mean([r["nodes_explored"] for r in summary_results]), 2)
    avg_time = round(mean([r["search_time_sec"] for r in summary_results]), 6)

    summary = {
        "agent": args.agent,
        "benchmark": args.benchmark,
        "runs": len(summary_results),
        "successes": len(successes),
        "success_rate": round(len(successes) / len(summary_results), 2) if summary_results else 0,
        "avg_path_length": avg_path_len,
        "avg_nodes_explored": avg_nodes,
        "avg_search_time_sec": avg_time,
        "seed_base": args.seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seed_results": summary_results
    }

    # Save benchmark summary to JSON
    json_folder = os.path.join("src", "data", "metrics", args.agent, "benchmark_data")
    os.makedirs(json_folder, exist_ok=True)
    json_path = os.path.join(json_folder, f"summary_{args.benchmark}.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)

    # Print summary to terminal
    print(f"""
Agent: {args.agent}
Benchmark: {args.benchmark}
Total runs: {summary['runs']}
Successes: {summary['successes']}
Success rate: {summary['success_rate']}
Avg path length: {avg_path_len}
Avg nodes explored: {avg_nodes}
Avg search time sec: {avg_time}
Seed base: {args.seed}
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmark simulations for lookahead agents.")
    parser.add_argument("--agent", choices=["depth", "noise", "dynamic"], required=True, help="Agent type")
    parser.add_argument("--runs", type=int, default=5, help="Number of repetitions per parameter value")
    parser.add_argument("--benchmark", choices=["easy", "medium", "true_maze"], required=True, help="Benchmark map")

    parser.add_argument("--min-depth", type=int, default=DEFAULT_DEPTH_RANGE[0], help="Minimum depth (for depth agent)")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_DEPTH_RANGE[1], help="Maximum depth (for depth agent)")
    parser.add_argument("--min-noise", type=int, default=DEFAULT_NOISE_RANGE[0], help="Minimum noise (for noise agent)")
    parser.add_argument("--max-noise", type=int, default=DEFAULT_NOISE_RANGE[1], help="Maximum noise (for noise agent)")

    parser.add_argument("--seed", type=int, default=Global_Seed, help="Base random seed (optional)")
    args = parser.parse_args()
    run_batch(args)
