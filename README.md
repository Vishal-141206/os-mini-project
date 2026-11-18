# Interactive OS Algorithm Lab

A Python-based mini-project for visualizing and comparing core Operating Systems algorithms through an interactive Streamlit interface.

## Overview

This project helps students understand CPU scheduling, virtual memory (page replacement), and deadlock avoidance through interactive simulations, metric tables, and visualizations (Gantt charts, fault-rate bar charts, step-by-step memory traces).

## Modules

### 1. CPU Scheduling (`algorithms/scheduling.py`)
- FCFS (First Come, First Served) — non-preemptive
- SJF (Shortest Job First) — non-preemptive
- SRTF (Shortest Remaining Time First) — preemptive
- Round Robin — preemptive, configurable time quantum
- Priority Scheduling — non-preemptive (lower number = higher priority)

Each algorithm returns waiting time, turnaround time, response time, per-process metrics, and a chronological execution sequence (including CPU idle segments) for Gantt-chart rendering.

### 2. Page Replacement (`algorithms/page_replacement.py`)
- FIFO (First In, First Out)
- LRU (Least Recently Used)
- Optimal (MIN / future-knowledge)

Each algorithm returns page hits, page faults, fault/hit rates, and a step-by-step history of frame states. All three can be run simultaneously for a side-by-side fault-rate comparison.

### 3. Deadlock Avoidance — Banker's Algorithm (`algorithms/bankers.py`)
- Accepts Allocation, Maximum, and Available matrices
- Computes the Need matrix (Need = Max − Allocation)
- Safety algorithm: returns safe/unsafe verdict and the safe sequence
- Step-by-step Work/Finish trace for inspection

## Technology Stack

- **Python** — algorithm implementation
- **Streamlit** — interactive web interface
- **Plotly** — visualizations (Gantt chart, fault-rate bar chart)
- **pandas** — result dataframes
- **pytest** — automated testing

## Project Structure

```
os-mini-project/
├── app.py                    # Streamlit application
├── requirements.txt          # streamlit, plotly, pandas, pytest
├── README.md
├── algorithms/
│   ├── __init__.py
│   ├── scheduling.py         # CPU scheduling algorithms
│   ├── page_replacement.py   # Page replacement algorithms
│   └── bankers.py            # Banker's deadlock avoidance
└── tests/
    └── test_algorithms.py    # pytest cases (24 tests)
```

## Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Vishal-141206/os-mini-project.git
cd os-mini-project
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```

Then open the URL shown by Streamlit (typically `http://localhost:8501`).

## Running Tests

```bash
pytest tests/test_algorithms.py
```

The suite uses classic textbook OS examples to verify algorithmic correctness (24 test cases, all passing).

## Usage

- **CPU Scheduling:** Add processes (Arrival Time, Burst Time, Priority) dynamically, pick an algorithm (and Round Robin quantum), then view the metrics dataframe, averages, and an interactive Gantt chart.
- **Page Replacement:** Enter a comma-separated reference string and frame count; view a fault-rate comparison bar chart plus per-algorithm step-by-step memory-state tables.
- **Deadlock Avoidance:** Edit the Allocation, Maximum, and Available matrices in grid inputs, run the Banker's algorithm, and see the Need matrix, SAFE/UNSAFE verdict, safe sequence, and safety trace.

## Scope

This is an educational simulator of selected OS algorithms, not a real operating system or kernel-level implementation.
