# Interactive OS Algorithm Lab

A Python-based mini-project for visualizing and comparing core Operating Systems algorithms.

**Status:** Initial setup — implementation planned.

## Overview

This project aims to help students understand CPU scheduling, virtual memory, and deadlock avoidance through interactive simulations and algorithm comparisons.

## Planned Modules

### 1. CPU Scheduling
- FCFS (First Come, First Served)
- SJF (non-preemptive)
- SRTF (preemptive SJF)
- Round Robin
- Priority Scheduling (non-preemptive)
- Gantt charts and waiting, turnaround, and response-time metrics

### 2. Page Replacement
- FIFO
- LRU
- Optimal
- Page-frame visualization, page hits, page faults, and fault-rate comparison

### 3. Deadlock Avoidance
- Banker's Algorithm
- Allocation, Maximum, Available, and Need matrices
- Safe-sequence detection
- Safe and unsafe state analysis

## Technology Stack

- **Python** — algorithm implementation
- **Streamlit** — interactive interface
- **Plotly** — visualizations
- **pandas** — result tables
- **pytest** — automated testing
- **Git and GitHub** — version control

## Planned Project Structure

    os-mini-project/
    ├── app.py
    ├── algorithms/
    │   ├── scheduling.py
    │   ├── page_replacement.py
    │   └── bankers.py
    ├── tests/
    ├── requirements.txt
    └── README.md

## Planned Setup

Once the implementation is added, clone the repository:

    git clone https://github.com/Vishal-141206/os-mini-project.git
    cd os-mini-project
    python -m venv .venv

Install the dependencies listed in `requirements.txt`, then launch the application using:

    streamlit run app.py

## Evaluation Plan

The algorithms will be tested with known examples and edge cases. The project will compare algorithm performance using consistent inputs and calculated results.

## Scope

This is an educational simulator of selected OS algorithms, not a real operating system or kernel-level implementation.
