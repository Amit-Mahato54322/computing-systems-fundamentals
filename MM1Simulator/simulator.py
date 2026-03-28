#!/usr/bin/env python3
"""
Discrete-event simulator for an M/M/1 CPU scheduling system.

Supports:
    0 -> FCFS
    1 -> non-preemptive SJF

Usage:
    python3 simulator.py <arrival_rate_lambda> <avg_service_time> <scheduler>

Examples:
    python3 simulator.py 15 0.04 0
    python3 simulator.py 15 0.04 1
    python3 simulator.py 15 0.04 0 --seed 42
    python3 simulator.py 15 0.04 0 --max-completions 10000
"""

from __future__ import annotations

import argparse
import heapq
import random
import sys
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


ARRIVAL = 0
DEPARTURE = 1

FCFS = 0
SJF = 1


@dataclass
class Process:
    pid: int
    arrival_time: float
    service_time: float
    start_time: Optional[float] = None
    finish_time: Optional[float] = None


@dataclass(order=True)
class Event:
    time: float
    priority: int
    seq: int
    event_type: int = field(compare=False)
    process: Optional[Process] = field(compare=False, default=None)


class MM1Simulator:
    def __init__(
        self,
        arrival_rate: float,
        avg_service_time: float,
        scheduler_type: int,
        max_completions: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        if arrival_rate <= 0:
            raise ValueError("arrival_rate must be > 0")
        if avg_service_time <= 0:
            raise ValueError("avg_service_time must be > 0")
        if scheduler_type not in (FCFS, SJF):
            raise ValueError("scheduler_type must be 0 (FCFS) or 1 (SJF)")
        if max_completions <= 0:
            raise ValueError("max_completions must be > 0")

        self.arrival_rate = arrival_rate
        self.avg_service_time = avg_service_time
        self.scheduler_type = scheduler_type
        self.max_completions = max_completions
        self.rng = random.Random(seed)

        self.clock = 0.0
        self.sim_start_time: Optional[float] = None

        self.cpu_busy = False
        self.current_process: Optional[Process] = None

        self.event_queue: list[Event] = []

        self.ready_queue_fcfs: deque[Process] = deque()
        self.ready_queue_sjf: list[tuple[float, float, int, Process]] = []

        self.completed_processes = 0
        self.next_pid = 1
        self.next_event_seq = 0

        self.total_turnaround_time = 0.0
        self.total_cpu_busy_time = 0.0
        self.total_ready_queue_area = 0.0

    def generate_interarrival_time(self) -> float:
        return self.rng.expovariate(self.arrival_rate)

    def generate_service_time(self) -> float:
        return self.rng.expovariate(1.0 / self.avg_service_time)

    def ready_queue_size(self) -> int:
        if self.scheduler_type == FCFS:
            return len(self.ready_queue_fcfs)
        return len(self.ready_queue_sjf)

    def push_ready_queue(self, process: Process) -> None:
        if self.scheduler_type == FCFS:
            self.ready_queue_fcfs.append(process)
        else:
            heapq.heappush(
                self.ready_queue_sjf,
                (process.service_time, process.arrival_time, process.pid, process),
            )

    def pop_ready_queue(self) -> Process:
        if self.scheduler_type == FCFS:
            return self.ready_queue_fcfs.popleft()
        _, _, _, process = heapq.heappop(self.ready_queue_sjf)
        return process

    def schedule_event(
        self,
        time: float,
        event_type: int,
        process: Optional[Process] = None,
    ) -> None:
        priority = 0 if event_type == DEPARTURE else 1
        event = Event(
            time=time,
            priority=priority,
            seq=self.next_event_seq,
            event_type=event_type,
            process=process,
        )
        self.next_event_seq += 1
        heapq.heappush(self.event_queue, event)

    def pop_next_event(self) -> Event:
        if not self.event_queue:
            raise RuntimeError("Event queue is empty before simulation completed.")
        return heapq.heappop(self.event_queue)

    def update_time_stats(self, new_time: float) -> None:
        delta = new_time - self.clock
        if delta < 0:
            raise RuntimeError("Simulation clock moved backward.")

        if self.cpu_busy:
            self.total_cpu_busy_time += delta

        self.total_ready_queue_area += self.ready_queue_size() * delta

    def start_service(self, process: Process) -> None:
        process.start_time = self.clock
        self.current_process = process
        self.cpu_busy = True

        departure_time = self.clock + process.service_time
        self.schedule_event(departure_time, DEPARTURE, process)

    def handle_arrival(self) -> None:
        process = Process(
            pid=self.next_pid,
            arrival_time=self.clock,
            service_time=self.generate_service_time(),
        )
        self.next_pid += 1

        if self.completed_processes < self.max_completions:
            next_arrival_time = self.clock + self.generate_interarrival_time()
            self.schedule_event(next_arrival_time, ARRIVAL)

        if not self.cpu_busy:
            self.start_service(process)
        else:
            self.push_ready_queue(process)

    def handle_departure(self, process: Process) -> None:
        process.finish_time = self.clock
        self.total_turnaround_time += process.finish_time - process.arrival_time
        self.completed_processes += 1

        self.current_process = None
        self.cpu_busy = False

        if self.ready_queue_size() > 0:
            next_process = self.pop_ready_queue()
            self.start_service(next_process)

    def initialize(self) -> None:
        first_arrival_time = self.generate_interarrival_time()
        self.schedule_event(first_arrival_time, ARRIVAL)

    def run(self) -> dict:
        self.initialize()

        first_event = True

        while self.completed_processes < self.max_completions:
            event = self.pop_next_event()

            if first_event:
                self.clock = event.time
                self.sim_start_time = event.time
                first_event = False
            else:
                self.update_time_stats(event.time)
                self.clock = event.time

            if event.event_type == ARRIVAL:
                self.handle_arrival()
            elif event.event_type == DEPARTURE:
                if event.process is None:
                    raise RuntimeError("Departure event missing process.")
                self.handle_departure(event.process)
            else:
                raise RuntimeError(f"Unknown event type: {event.event_type}")

        if self.sim_start_time is None:
            raise RuntimeError("Simulation never started.")

        total_simulation_time = self.clock - self.sim_start_time
        if total_simulation_time <= 0:
            raise RuntimeError("Total simulation time must be positive.")

        return {
            "arrival_rate": self.arrival_rate,
            "avg_service_time": self.avg_service_time,
            "scheduler_id": self.scheduler_type,
            "scheduler": "FCFS" if self.scheduler_type == FCFS else "SJF",
            "completed_processes": self.completed_processes,
            "simulation_start_time": self.sim_start_time,
            "simulation_end_time": self.clock,
            "total_simulation_time": total_simulation_time,
            "average_turnaround_time": self.total_turnaround_time / self.completed_processes,
            "throughput": self.completed_processes / total_simulation_time,
            "cpu_utilization": self.total_cpu_busy_time / total_simulation_time,
            "average_ready_queue_length": self.total_ready_queue_area / total_simulation_time,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discrete-event simulator for an M/M/1 CPU scheduling system."
    )
    parser.add_argument("arrival_rate", type=float, help="Average arrival rate lambda.")
    parser.add_argument("avg_service_time", type=float, help="Average service time.")
    parser.add_argument(
        "scheduler",
        type=int,
        choices=[0, 1],
        help="Scheduler: 0 for FCFS, 1 for SJF.",
    )
    parser.add_argument(
        "--max-completions",
        type=int,
        default=10000,
        help="Stop after this many completed processes.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        sim = MM1Simulator(
            arrival_rate=args.arrival_rate,
            avg_service_time=args.avg_service_time,
            scheduler_type=args.scheduler,
            max_completions=args.max_completions,
            seed=args.seed,
        )
        results = sim.run()

        print("===== M/M/1 Discrete-Event Simulation Results =====")
        print(f"Scheduler:                     {results['scheduler']}")
        print(f"Arrival rate (lambda):        {results['arrival_rate']:.6f} processes/sec")
        print(f"Average service time:         {results['avg_service_time']:.6f} sec")
        print(f"Completed processes:          {results['completed_processes']}")
        print(f"Simulation start time:        {results['simulation_start_time']:.6f} sec")
        print(f"Simulation end time:          {results['simulation_end_time']:.6f} sec")
        print(f"Total simulation time:        {results['total_simulation_time']:.6f} sec")
        print(f"Average turnaround time:      {results['average_turnaround_time']:.6f} sec")
        print(f"Throughput:                   {results['throughput']:.6f} processes/sec")
        print(f"CPU utilization:              {results['cpu_utilization']:.6f}")
        print(f"Average Ready queue length:   {results['average_ready_queue_length']:.6f}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())