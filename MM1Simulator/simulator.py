#!/usr/bin/env python3
"""
Discrete-event simulator for an M/M/1 CPU scheduling system.

Supports:
    0 -> FCFS
    1 -> non-preemptive SJF

Command-line arguments:
    python3 simulator.py <arrival_rate_lambda> <avg_service_time> <scheduler>

Example:
    python3 simulator.py 15 0.04 0
    python3 simulator.py 15 0.04 1

Optional:
    python3 simulator.py 15 0.04 0 --seed 42
    python3 simulator.py 15 0.04 0 --max-completions 10000

Outputs:
    - Average turnaround time
    - Throughput
    - CPU utilization
    - Average number of processes in the Ready queue
"""

from __future__ import annotations

import argparse
import heapq
import math
import random
import sys
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


# Event type constants
ARRIVAL = 0
DEPARTURE = 1

# Scheduler type constants
FCFS = 0
SJF = 1


@dataclass
class Process:
    """
    Represents a process in the system.
    """
    pid: int
    arrival_time: float
    service_time: float
    start_time: Optional[float] = None
    finish_time: Optional[float] = None


@dataclass(order=True)
class Event:
    """
    Represents an event in the event queue.

    The dataclass is ordered so heapq can sort events by:
        1. time
        2. priority
        3. seq
    """
    time: float
    priority: int
    seq: int
    event_type: int = field(compare=False)
    process: Optional[Process] = field(compare=False, default=None)


class MM1Simulator:
    """
    Discrete-event simulator for an M/M/1 queuing system with either:
        - FCFS scheduling
        - non-preemptive SJF scheduling
    """

    def __init__(
        self,
        arrival_rate: float,
        avg_service_time: float,
        scheduler_type: int,
        max_completions: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        # Validate input early
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

        if seed is not None:
            random.seed(seed)

        # Simulation clock
        self.clock: float = 0.0

        # CPU state
        self.cpu_busy: bool = False
        self.current_process: Optional[Process] = None

        # Event queue: min-heap ordered by event time
        self.event_queue: List[Event] = []

        # Ready queue
        # FCFS: use deque
        # SJF: use heap of tuples (service_time, arrival_time, pid, process)
        self.ready_queue_fcfs: deque[Process] = deque()
        self.ready_queue_sjf: List[Tuple[float, float, int, Process]] = []

        # Counters
        self.completed_processes: int = 0
        self.next_pid: int = 1
        self.next_event_seq: int = 0

        # Statistics accumulators
        self.total_turnaround_time: float = 0.0
        self.total_cpu_busy_time: float = 0.0
        self.total_ready_queue_area: float = 0.0

    # ------------------------------------------------------------------
    # Random generation
    # ------------------------------------------------------------------

    def exponential_random(self, mean: float) -> float:
        """
        Generate an exponentially distributed random value with the given mean.

        Python's random.expovariate(rate) uses rate = 1 / mean.
        """
        rate = 1.0 / mean
        return random.expovariate(rate)

    # ------------------------------------------------------------------
    # Ready queue helpers
    # ------------------------------------------------------------------

    def ready_queue_size(self) -> int:
        """
        Return the number of processes currently waiting in the Ready queue.
        """
        if self.scheduler_type == FCFS:
            return len(self.ready_queue_fcfs)
        return len(self.ready_queue_sjf)

    def push_ready_queue(self, process: Process) -> None:
        """
        Insert a process into the Ready queue according to the scheduler.
        """
        if self.scheduler_type == FCFS:
            self.ready_queue_fcfs.append(process)
        else:
            # SJF: sort by service_time, then arrival_time, then pid
            heapq.heappush(
                self.ready_queue_sjf,
                (process.service_time, process.arrival_time, process.pid, process),
            )

    def pop_ready_queue(self) -> Process:
        """
        Remove and return the next process chosen by the scheduler.
        """
        if self.scheduler_type == FCFS:
            return self.ready_queue_fcfs.popleft()

        _, _, _, process = heapq.heappop(self.ready_queue_sjf)
        return process

    # ------------------------------------------------------------------
    # Event queue helpers
    # ------------------------------------------------------------------

    def schedule_event(self, time: float, event_type: int, process: Optional[Process] = None) -> None:
        """
        Create and insert an event into the Event Queue.

        priority is used to break ties when two events happen at the same time.
        We give DEPARTURE priority over ARRIVAL at the same timestamp so that
        a completion at time t can free the CPU before handling a new arrival at time t.
        This is a valid and consistent tie-breaking rule.
        """
        if event_type == DEPARTURE:
            priority = 0
        else:
            priority = 1

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
        """
        Remove and return the earliest event from the Event Queue.
        """
        return heapq.heappop(self.event_queue)

    # ------------------------------------------------------------------
    # Statistics update
    # ------------------------------------------------------------------

    def update_time_stats(self, new_time: float) -> None:
        """
        Update time-based statistics for the interval [clock, new_time).

        Important:
        The system state during this interval is the OLD state, before the new event
        is processed.
        """
        delta = new_time - self.clock
        if delta < 0:
            raise RuntimeError("Simulation clock would move backward, which should never happen.")

        # CPU busy time
        if self.cpu_busy:
            self.total_cpu_busy_time += delta

        # Ready queue time-average area
        self.total_ready_queue_area += self.ready_queue_size() * delta

    # ------------------------------------------------------------------
    # Service / dispatch helpers
    # ------------------------------------------------------------------

    def start_service(self, process: Process) -> None:
        """
        Start CPU service for a process immediately at the current clock time
        and schedule its departure event.
        """
        process.start_time = self.clock
        self.current_process = process
        self.cpu_busy = True

        departure_time = self.clock + process.service_time
        self.schedule_event(departure_time, DEPARTURE, process)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def handle_arrival(self) -> None:
        """
        Handle an ARRIVAL event:
            1. Create the arriving process
            2. Schedule the next arrival
            3. If CPU is idle, start service immediately
               otherwise, put process into Ready queue
        """
        # Create the new process
        process = Process(
            pid=self.next_pid,
            arrival_time=self.clock,
            service_time=self.exponential_random(self.avg_service_time),
        )
        self.next_pid += 1

        # Schedule the next arrival
        interarrival_time = self.exponential_random(1.0 / self.arrival_rate)
        next_arrival_time = self.clock + interarrival_time
        self.schedule_event(next_arrival_time, ARRIVAL)

        # Dispatch or queue
        if not self.cpu_busy:
            self.start_service(process)
        else:
            self.push_ready_queue(process)

    def handle_departure(self, process: Process) -> None:
        """
        Handle a DEPARTURE event:
            1. Mark process finished
            2. Update turnaround and completed count
            3. Free the CPU
            4. If Ready queue not empty, dispatch next process
        """
        process.finish_time = self.clock

        turnaround = process.finish_time - process.arrival_time
        self.total_turnaround_time += turnaround
        self.completed_processes += 1

        # CPU becomes free
        self.current_process = None
        self.cpu_busy = False

        # If a process is waiting, start it immediately
        if self.ready_queue_size() > 0:
            next_process = self.pop_ready_queue()
            self.start_service(next_process)

    # ------------------------------------------------------------------
    # Simulation control
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the simulation by scheduling the very first arrival.
        """
        first_arrival_time = self.exponential_random(1.0 / self.arrival_rate)
        self.schedule_event(first_arrival_time, ARRIVAL)

    def run(self) -> dict:
        """
        Run the simulation until max_completions processes have completed.

        Returns a dictionary containing the final metrics.
        """
        self.initialize()

        while self.completed_processes < self.max_completions:
            event = self.pop_next_event()

            # Update time-based stats using the OLD state
            self.update_time_stats(event.time)

            # Move clock to the event time
            self.clock = event.time

            # Process event
            if event.event_type == ARRIVAL:
                self.handle_arrival()
            elif event.event_type == DEPARTURE:
                if event.process is None:
                    raise RuntimeError("Departure event missing process.")
                self.handle_departure(event.process)
            else:
                raise RuntimeError(f"Unknown event type: {event.event_type}")

        total_simulation_time = self.clock

        # Avoid division by zero, though in practice clock should be > 0
        if total_simulation_time <= 0:
            raise RuntimeError("Total simulation time is not positive.")

        avg_turnaround_time = self.total_turnaround_time / self.completed_processes
        throughput = self.completed_processes / total_simulation_time
        cpu_utilization = self.total_cpu_busy_time / total_simulation_time
        avg_ready_queue_length = self.total_ready_queue_area / total_simulation_time

        return {
            "arrival_rate": self.arrival_rate,
            "avg_service_time": self.avg_service_time,
            "scheduler": "FCFS" if self.scheduler_type == FCFS else "SJF",
            "completed_processes": self.completed_processes,
            "total_simulation_time": total_simulation_time,
            "average_turnaround_time": avg_turnaround_time,
            "throughput": throughput,
            "cpu_utilization": cpu_utilization,
            "average_ready_queue_length": avg_ready_queue_length,
        }


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Discrete-event simulator for an M/M/1 CPU scheduling system."
    )
    parser.add_argument(
        "arrival_rate",
        type=float,
        help="Average arrival rate lambda (processes per second).",
    )
    parser.add_argument(
        "avg_service_time",
        type=float,
        help="Average service time (seconds).",
    )
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
        help="Number of completed processes before stopping the simulation (default: 10000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducibility.",
    )
    return parser.parse_args()


def main() -> int:
    """
    Program entry point.
    """
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