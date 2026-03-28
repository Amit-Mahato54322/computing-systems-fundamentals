#!/usr/bin/env python3

import csv
import os
import sys
import matplotlib.pyplot as plt


INPUT_CSV = "results/results.csv"
OUTPUT_DIR = "results"


def read_results(csv_file):
    rows = []

    with open(csv_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "arrival_rate": float(row["arrival_rate"]),
                "scheduler": row["scheduler"].strip(),
                "average_turnaround_time": float(row["average_turnaround_time"]),
                "throughput": float(row["throughput"]),
                "cpu_utilization": float(row["cpu_utilization"]),
                "average_ready_queue_length": float(row["average_ready_queue_length"]),
            })

    return rows


def split_by_scheduler(rows):
    fcfs = [r for r in rows if r["scheduler"] == "FCFS"]
    sjf = [r for r in rows if r["scheduler"] == "SJF"]

    fcfs.sort(key=lambda r: r["arrival_rate"])
    sjf.sort(key=lambda r: r["arrival_rate"])

    return fcfs, sjf


def make_plot(fcfs, sjf, metric, ylabel, title, output_file):
    plt.figure(figsize=(8, 5))

    plt.plot(
        [r["arrival_rate"] for r in fcfs],
        [r[metric] for r in fcfs],
        marker="o",
        label="FCFS",
    )

    plt.plot(
        [r["arrival_rate"] for r in sjf],
        [r[metric] for r in sjf],
        marker="s",
        label="SJF",
    )

    plt.xlabel("Arrival rate λ (processes/sec)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: could not find {INPUT_CSV}")
        print("Run this first:")
        print("    python3 run_experiments.py")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = read_results(INPUT_CSV)
    fcfs, sjf = split_by_scheduler(rows)

    if not fcfs or not sjf:
        print("Error: CSV must contain both FCFS and SJF rows.")
        sys.exit(1)

    make_plot(
        fcfs,
        sjf,
        "average_turnaround_time",
        "Average Turnaround Time (sec)",
        "Average Turnaround Time vs Arrival Rate",
        os.path.join(OUTPUT_DIR, "turnaround_time.png"),
    )

    make_plot(
        fcfs,
        sjf,
        "throughput",
        "Throughput (processes/sec)",
        "Throughput vs Arrival Rate",
        os.path.join(OUTPUT_DIR, "throughput.png"),
    )

    make_plot(
        fcfs,
        sjf,
        "cpu_utilization",
        "CPU Utilization",
        "CPU Utilization vs Arrival Rate",
        os.path.join(OUTPUT_DIR, "cpu_utilization.png"),
    )

    make_plot(
        fcfs,
        sjf,
        "average_ready_queue_length",
        "Average Ready Queue Length",
        "Average Ready Queue Length vs Arrival Rate",
        os.path.join(OUTPUT_DIR, "ready_queue_length.png"),
    )

    print("Created:")
    print(f"  {OUTPUT_DIR}/turnaround_time.png")
    print(f"  {OUTPUT_DIR}/throughput.png")
    print(f"  {OUTPUT_DIR}/cpu_utilization.png")
    print(f"  {OUTPUT_DIR}/ready_queue_length.png")


if __name__ == "__main__":
    main()