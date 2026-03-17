<h1> Discrete -event simulator for an M/M/1 CPU scheduling system.</h1>

supports:
    0 -> FCFS
    1 -> non-preemptive SJF

command-line arguments:
    python3 simulator.py "<arrival_rate> <avg_service_time> <scheduler>"

Example:
    python3 simulator.py 15 0.04 0
    python3 simulator.py 15 0.04 1

Optional:
    python3 simulator.py 15 0.04 --seed 42
    python3 simulator.py 15 0.04 --max-completions 10000

Outputs:
    -average turnaround time
    -throughput
    -CPU utilization
    -Average number of processes in the Ready queue

