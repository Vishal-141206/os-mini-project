"""Banker's Algorithm for deadlock avoidance.

Given the current resource allocation state of a system, the Banker's algorithm
determines whether the state is *safe* (there exists at least one order in which
all processes can finish without deadlock) and returns such a safe sequence.

Inputs:
    allocation : list[list[int]]  (n processes x m resources) currently held
    maximum    : list[list[int]]  (n processes x m resources) maximum demand
    available  : list[int]        (m resources) currently free instances

Outputs:
    {
        "safe": bool,
        "need": list[list[int]],
        "safe_sequence": list[str],
        "work_trace": list[dict],  # step-by-step Work/Finish trace for display
    }
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _validate(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available: List[int],
) -> Tuple[int, int]:
    """Validate matrix shapes and return (n_processes, n_resources)."""
    if not allocation or not maximum:
        raise ValueError("Allocation and Maximum matrices must not be empty.")
    if len(allocation) != len(maximum):
        raise ValueError("Allocation and Maximum must have the same number of processes.")

    n = len(allocation)
    m = len(available)

    for i, row in enumerate(allocation):
        if len(row) != m:
            raise ValueError(f"Allocation row {i} does not match Available length.")
    for i, row in enumerate(maximum):
        if len(row) != m:
            raise ValueError(f"Maximum row {i} does not match Available length.")

    if any(v < 0 for row in allocation for v in row):
        raise ValueError("Allocation values must be non-negative.")
    if any(v < 0 for row in maximum for v in row):
        raise ValueError("Maximum values must be non-negative.")
    if any(v < 0 for v in available):
        raise ValueError("Available values must be non-negative.")

    return n, m


def bankers(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available: List[int],
) -> Dict[str, Any]:
    """Run the Banker's safety algorithm.

    Computes Need = Maximum - Allocation, then repeatedly finds a process whose
    Need <= Work. When found, it "finishes" (Work += Allocation) and is appended
    to the safe sequence. If every process finishes, the state is safe.
    """
    n, m = _validate(allocation, maximum, available)

    # Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j]
    need: List[List[int]] = [
        [maximum[i][j] - allocation[i][j] for j in range(m)] for i in range(n)
    ]

    work = list(available)
    finish = [False] * n
    safe_sequence: List[str] = []
    work_trace: List[Dict[str, Any]] = []

    # Initial snapshot.
    work_trace.append(
        {
            "step": 0,
            "process": None,
            "action": "Initial",
            "work": list(work),
            "finish": list(finish),
        }
    )

    step = 0
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if finish[i]:
                continue
            if all(need[i][j] <= work[j] for j in range(m)):
                # Process i can be satisfied; it runs to completion and releases resources.
                step += 1
                progress = True
                finish[i] = True
                safe_sequence.append(f"P{i}")
                for j in range(m):
                    work[j] += allocation[i][j]
                work_trace.append(
                    {
                        "step": step,
                        "process": f"P{i}",
                        "action": f"Need[{i}] <= Work -> finish, release Allocation[{i}]",
                        "work": list(work),
                        "finish": list(finish),
                    }
                )

    safe = all(finish)

    return {
        "safe": safe,
        "need": need,
        "safe_sequence": safe_sequence,
        "work_trace": work_trace,
    }
