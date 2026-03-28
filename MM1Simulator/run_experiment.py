#!/usr/bin/env python3
"""
Batch runner for HW #4.

Runs lambda = 10..30 for both schedulers and saves results to CSV.
No graphics are produced.

Usage:
    python3 run_experiments.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from simulator import MM1Simulator, FCFS, SJF


AVG_SERVICE_TIME = 0.04
MAX_COMPLETIONS = 10000
LAMBDAS = list(range(10, 31))
OUTPUT_DIR = Path("results")
OUTPUT_CSV = OUTPUT_DIR / "results.csv"


def run_all() -> list[dict]:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows: list[dict] = []

    for scheduler in (FCFS, SJF):
        for lam in LAMBDAS:
            seed = 1000 + scheduler * 100 + lam

            sim = MM1Simulator(
                arrival_rate=float(lam),
                avg_service_time=AVG_SERVICE_TIME,
                scheduler_type=scheduler,
                max_completions=MAX_COMPLETIONS,
                seed=seed,
            )
            result = sim.run()
            rows.append(result)

            print(
                f"done: lambda={lam:2d}, scheduler={result['scheduler']}, "
                f"TAT={result['average_turnaround_time']:.6f}, "
                f"THR={result['throughput']:.6f}, "
                f"UTIL={result['cpu_utilization']:.6f}, "
                f"RQ={result['average_ready_queue_length']:.6f}"
            )

    return rows


def write_csv(rows: list[dict]) -> None:
    fieldnames = [
        "arrival_rate",
        "avg_service_time",
        "scheduler_id",
        "scheduler",
        "completed_processes",
        "simulation_start_time",
        "simulation_end_time",
        "total_simulation_time",
        "average_turnaround_time",
        "throughput",
        "cpu_utilization",
        "average_ready_queue_length",
    ]

    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = run_all()
    write_csv(rows)
    print(f"\nSaved results to: {OUTPUT_CSV.resolve()}")


if __name__ == "__main__":
    main()