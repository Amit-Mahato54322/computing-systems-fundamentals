<h1>CS3360 – Homework #4</h1>
<h2>M/M/1 CPU Scheduling Simulator (FCFS vs SJF)</h2>

<hr>

<h2>Overview</h2>

<p>
This project implements a <strong>discrete-event simulator</strong> for an
<strong>M/M/1 queuing system</strong> that models CPU scheduling using:
</p>

<ul>
  <li>First-Come First-Served (FCFS)</li>
  <li>Shortest Job First (SJF, non-preemptive)</li>
</ul>

<p>
Processes arrive according to a <strong>Poisson process</strong> and have
<strong>exponentially distributed service times</strong>. The simulator evaluates
system performance under varying workloads.
</p>

<hr>

<h2>System Model</h2>

<ul>
  <li><strong>Arrival process:</strong> Poisson with rate λ</li>
  <li><strong>Service time:</strong> Exponential with average Ts = 0.04 seconds</li>
  <li><strong>Service rate:</strong> μ = 1 / Ts = 25 processes/sec</li>
  <li><strong>Queue type:</strong> M/M/1 (single CPU)</li>
  <li><strong>Scheduling policies:</strong>
    <ul>
      <li>FCFS</li>
      <li>Non-preemptive SJF</li>
    </ul>
  </li>
</ul>

<hr>

<h2>Performance Metrics</h2>

<p>The simulator computes the following metrics:</p>

<ul>
  <li>Average turnaround time</li>
  <li>Throughput (processes/sec)</li>
  <li>CPU utilization</li>
  <li>Average Ready queue length</li>
</ul>

<hr>

<h2>Project Structure</h2>

<pre>
.
├── simulator.py
├── run_experiments.py
├── make_plots.py
├── results/
│   ├── results.csv
│   ├── turnaround_time.png
│   ├── throughput.png
│   ├── cpu_utilization.png
│   └── ready_queue_length.png
└── README.md
</pre>

<hr>

<h2>How to Run</h2>

<h3>1. Run a single simulation</h3>

<pre>
python3 simulator.py &lt;arrival_rate&gt; &lt;avg_service_time&gt; &lt;scheduler&gt;
</pre>

<p>Example:</p>

<pre>
python3 simulator.py 15 0.04 0
</pre>

<p><strong>Scheduler values:</strong></p>

<ul>
  <li><code>0</code> = FCFS</li>
  <li><code>1</code> = SJF</li>
</ul>

<h3>2. Run all experiments</h3>

<pre>
python3 run_experiments.py
</pre>

<p>This runs:</p>

<ul>
  <li>λ = 10 to 30</li>
  <li>Both FCFS and SJF</li>
  <li>10,000 completed processes per run</li>
</ul>

<p>Output:</p>

<pre>
results/results.csv
</pre>

<h3>3. Generate plots</h3>

<pre>
python3 make_plots.py
</pre>

<p>This creates:</p>

<ul>
  <li>turnaround_time.png</li>
  <li>throughput.png</li>
  <li>cpu_utilization.png</li>
  <li>ready_queue_length.png</li>
</ul>

<hr>

<h2>Expected Behavior</h2>

<ul>
  <li>CPU utilization increases with λ and approaches 1</li>
  <li>Throughput increases and saturates near μ = 25</li>
  <li>Turnaround time increases sharply near saturation</li>
  <li>Ready queue length grows rapidly under heavy load</li>
  <li>SJF performs better than FCFS, especially in turnaround time and queue length</li>
</ul>

<hr>

<h2>Notes</h2>

<ul>
  <li>The simulator is <strong>command-line only</strong> and uses no graphical interface</li>
  <li>Plots are generated separately for the report</li>
  <li>For λ &gt; 25, the system becomes unstable</li>
</ul>

<hr>

<h2>Key Insight</h2>

<p>This project demonstrates:</p>

<ul>
  <li>Performance degradation near system capacity</li>
  <li>The impact of scheduling policies on latency</li>
  <li>The advantage of SJF in reducing waiting time</li>
</ul>

<hr>

<h2>Submission Contents</h2>

<ul>
  <li>Source code (<code>simulator.py</code>, <code>run_experiments.py</code>, <code>make_plots.py</code>)</li>
  <li><code>README.md</code></li>
  <li>Output report with plots and analysis</li>
</ul>

<hr>

<h2>Author</h2>

<p>
Amit Mahato<br>
Computer Science – Texas State University
NetId: pgc53
</p>
