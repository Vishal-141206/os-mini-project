"""CPU scheduling algorithms for the Interactive OS Algorithm Lab.

Implemented algorithms:
    - FCFS  : First Come First Served (non-preemptive)
    - SJF   : Shortest Job First (non-preemptive)
    - SRTF  : Shortest Remaining Time First (preemptive)
    - RR    : Round Robin (preemptive, time-sliced)
    - PRIORITY : Non-preemptive Priority (lower priority number = higher priority)

Each algorithm accepts a list of process dictionaries with keys:
    pid          : str   - process identifier
    arrival_time : int   - arrival time in time units
    burst_time   : int   - total CPU burst time
    priority     : int   - priority value (lower number = higher priority)

Each algorithm returns a dictionary with:
    processes          : list of per-process metric dicts
    gantt              : chronological list of (pid, start_time, end_time)
                         tuples suitable for Gantt chart rendering
    avg_waiting_time   : float
    avg_turnaround_time: float
    avg_response_time  : float
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Process:
    """A single process with the metrics calculated by a scheduling algorithm."""

    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = field(init=False)
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: Optional[int] = None

    def __post_init__(self) -> None:
        self.remaining_time = self.burst_time


def _build_result(processes: List[Process], gantt: List[Tuple[str, int, int]]) -> Dict[str, Any]:
    """Assemble the standardized result dictionary shared by all schedulers."""
    n = len(processes)
    if n == 0:
        return {
            "processes": [],
            "gantt": [],
            "avg_waiting_time": 0.0,
            "avg_turnaround_time": 0.0,
            "avg_response_time": 0.0,
        }

    total_wt = sum(p.waiting_time for p in processes)
    total_tt = sum(p.turnaround_time for p in processes)
    total_rt = sum((p.response_time or 0) for p in processes)

    return {
        "processes": [
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": p.priority,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "waiting_time": p.waiting_time,
                "turnaround_time": p.turnaround_time,
                "response_time": p.response_time,
            }
            for p in processes
        ],
        "gantt": gantt,
        "avg_waiting_time": round(total_wt / n, 4),
        "avg_turnaround_time": round(total_tt / n, 4),
        "avg_response_time": round(total_rt / n, 4),
    }


def _to_processes(processes_input: List[Dict[str, Any]]) -> List[Process]:
    """Convert raw input dictionaries into :class:`Process` objects."""
    procs: List[Process] = []
    for p in processes_input:
        procs.append(
            Process(
                pid=str(p["pid"]),
                arrival_time=int(p["arrival_time"]),
                burst_time=int(p["burst_time"]),
                priority=int(p.get("priority", 0)),
            )
        )
    return procs


# ---------------------------------------------------------------------------
# FCFS - First Come First Served (non-preemptive)
# ---------------------------------------------------------------------------
def fcfs(processes_input: List[Dict[str, Any]]) -> Dict[str, Any]:
    """First Come First Served scheduling.

    Processes are executed in order of arrival time. If the CPU is idle when
    the next process has not arrived yet, an ``("Idle", start, end)`` segment
    is recorded in the Gantt sequence.
    """
    procs = _to_processes(processes_input)
    procs.sort(key=lambda p: (p.arrival_time, p.pid))

    gantt: List[Tuple[str, int, int]] = []
    current_time = 0

    for p in procs:
        # Account for CPU idle time before the next process arrives.
        if current_time < p.arrival_time:
            gantt.append(("Idle", current_time, p.arrival_time))
            current_time = p.arrival_time

        p.start_time = current_time
        p.response_time = current_time - p.arrival_time
        p.end_time = current_time + p.burst_time
        gantt.append((p.pid, current_time, p.end_time))

        current_time = p.end_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time  # == response (non-preemptive)

    return _build_result(procs, gantt)


# ---------------------------------------------------------------------------
# SJF - Shortest Job First (non-preemptive)
# ---------------------------------------------------------------------------
def sjf_non_preemptive(processes_input: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Shortest Job First scheduling (non-preemptive).

    Whenever the CPU becomes free, the arrived process with the shortest burst
    time is selected next. Ties are broken by arrival time, then pid.
    """
    procs = _to_processes(processes_input)
    gantt: List[Tuple[str, int, int]] = []
    current_time = 0
    remaining = list(procs)

    while remaining:
        available = [p for p in remaining if p.arrival_time <= current_time]
        if not available:
            # No process has arrived yet; the CPU stays idle until the next one.
            next_arrival = min(p.arrival_time for p in remaining)
            gantt.append(("Idle", current_time, next_arrival))
            current_time = next_arrival
            continue

        p = min(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        remaining.remove(p)

        p.start_time = current_time
        p.response_time = current_time - p.arrival_time
        p.end_time = current_time + p.burst_time
        gantt.append((p.pid, current_time, p.end_time))

        current_time = p.end_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time

    return _build_result(procs, gantt)


# ---------------------------------------------------------------------------
# SRTF - Shortest Remaining Time First (preemptive)
# ---------------------------------------------------------------------------
def srtf(processes_input: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Shortest Remaining Time First scheduling (preemptive).

    At every arrival or completion event the process with the smallest remaining
    burst time runs. If a newly arrived process has a strictly smaller remaining
    time than the currently running process, the running process is preempted.
    Ties keep the currently running process (no unnecessary context switch).
    """
    procs = _to_processes(processes_input)
    n = len(procs)
    gantt: List[Tuple[str, int, int]] = []
    current_time = 0

    arrival_order = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
    idx = 0  # next process to be admitted into the ready queue
    ready: List[Process] = []
    cur: Optional[Process] = None
    cur_start: Optional[int] = None
    completed = 0

    def admit_arrivals(t: int) -> None:
        """Move every process arriving at or before ``t`` into the ready queue."""
        nonlocal idx
        while idx < n and arrival_order[idx].arrival_time <= t:
            ready.append(arrival_order[idx])
            idx += 1
        ready.sort(key=lambda p: (p.remaining_time, p.arrival_time, p.pid))

    while completed < n:
        admit_arrivals(current_time)

        # Preemption check: a ready process with strictly less remaining time.
        if cur is not None and ready:
            best = ready[0]
            if best.pid != cur.pid and best.remaining_time < cur.remaining_time:
                gantt.append((cur.pid, cur_start, current_time))
                ready.append(cur)
                ready.sort(key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
                cur = None
                cur_start = None

        if cur is None and ready:
            cur = ready.pop(0)
            cur_start = current_time
            if cur.response_time is None:
                cur.response_time = current_time - cur.arrival_time

        if cur is None:
            # CPU idle: fast-forward to the next arrival.
            if idx < n:
                current_time = arrival_order[idx].arrival_time
                continue
            break  # defensive: nothing left to run

        # Run until completion or until the next arrival forces a re-evaluation.
        next_arrival = arrival_order[idx].arrival_time if idx < n else None
        time_to_complete = cur.remaining_time
        run_time = (
            min(time_to_complete, next_arrival - current_time)
            if next_arrival is not None
            else time_to_complete
        )

        if run_time <= 0:
            # An arrival at the current instant will be admitted next loop.
            continue

        cur.remaining_time -= run_time
        current_time += run_time

        if cur.remaining_time == 0:
            gantt.append((cur.pid, cur_start, current_time))
            cur.end_time = current_time
            cur.turnaround_time = cur.end_time - cur.arrival_time
            cur.waiting_time = cur.turnaround_time - cur.burst_time
            completed += 1
            cur = None
            cur_start = None

    return _build_result(procs, gantt)


# ---------------------------------------------------------------------------
# Round Robin (preemptive, time-sliced)
# ---------------------------------------------------------------------------
def round_robin(
    processes_input: List[Dict[str, Any]], quantum: int = 2
) -> Dict[str, Any]:
    """Round Robin scheduling with the given time quantum.

    The ready queue is FIFO. A running process is preempted when its quantum
    expires and moved to the back of the ready queue; new arrivals that occur
    during the quantum join the queue ahead of the preempted process.
    """
    if quantum <= 0:
        raise ValueError("Time quantum must be a positive integer.")

    procs = _to_processes(processes_input)
    n = len(procs)
    gantt: List[Tuple[str, int, int]] = []
    current_time = 0

    arrival_order = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
    idx = 0
    queue: List[Process] = []
    cur: Optional[Process] = None
    cur_start: Optional[int] = None
    remaining = {p.pid: p.burst_time for p in procs}
    completed = 0

    def admit_arrivals(t: int) -> None:
        nonlocal idx
        while idx < n and arrival_order[idx].arrival_time <= t:
            queue.append(arrival_order[idx])
            idx += 1

    pid_to_proc = {p.pid: p for p in procs}

    while completed < n:
        admit_arrivals(current_time)

        if cur is None and queue:
            cur = queue.pop(0)
            cur_start = current_time
            if cur.response_time is None:
                cur.response_time = current_time - cur.arrival_time

        if cur is None:
            # CPU idle: fast-forward to the next arrival.
            if idx < n:
                current_time = arrival_order[idx].arrival_time
                continue
            break  # defensive

        run_time = min(remaining[cur.pid], quantum)
        current_time += run_time
        remaining[cur.pid] -= run_time
        admit_arrivals(current_time)  # arrivals during the quantum join first

        if remaining[cur.pid] == 0:
            gantt.append((cur.pid, cur_start, current_time))
            p = pid_to_proc[cur.pid]
            p.end_time = current_time
            p.turnaround_time = current_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed += 1
            cur = None
            cur_start = None
        else:
            gantt.append((cur.pid, cur_start, current_time))
            queue.append(cur)  # preempted process goes to the back
            cur = None
            cur_start = None

    return _build_result(procs, gantt)


# ---------------------------------------------------------------------------
# Priority (non-preemptive)
# ---------------------------------------------------------------------------
def priority_non_preemptive(processes_input: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Non-preemptive Priority scheduling.

    The process with the lowest priority number (highest priority) among the
    arrived processes runs to completion. Ties are broken by arrival time, then
    pid. CPU idle time is recorded when no process has arrived yet.
    """
    procs = _to_processes(processes_input)
    gantt: List[Tuple[str, int, int]] = []
    current_time = 0
    remaining = list(procs)

    while remaining:
        available = [p for p in remaining if p.arrival_time <= current_time]
        if not available:
            next_arrival = min(p.arrival_time for p in remaining)
            gantt.append(("Idle", current_time, next_arrival))
            current_time = next_arrival
            continue

        p = min(available, key=lambda p: (p.priority, p.arrival_time, p.pid))
        remaining.remove(p)

        p.start_time = current_time
        p.response_time = current_time - p.arrival_time
        p.end_time = current_time + p.burst_time
        gantt.append((p.pid, current_time, p.end_time))

        current_time = p.end_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time

    return _build_result(procs, gantt)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
ALGORITHMS: Dict[str, Any] = {
    "FCFS": fcfs,
    "SJF (Non-Preemptive)": sjf_non_preemptive,
    "SRTF (Preemptive)": srtf,
    "Round Robin": round_robin,
    "Priority (Non-Preemptive)": priority_non_preemptive,
}


def schedule(
    algorithm: str,
    processes_input: List[Dict[str, Any]],
    quantum: int = 2,
) -> Dict[str, Any]:
    """Run the requested scheduling algorithm and return its result dictionary."""
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown scheduling algorithm: {algorithm}")

    func = ALGORITHMS[algorithm]
    if algorithm == "Round Robin":
        return func(processes_input, quantum=quantum)
    return func(processes_input)
