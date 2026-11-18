"""Page replacement algorithms for the Interactive OS Algorithm Lab.

Implemented algorithms:
    - FIFO   : First In First Out
    - LRU    : Least Recently Used
    - OPTIMAL: Optimal (future-knowledge, MIN) replacement

Each algorithm accepts:
    reference_string : list of int - page references
    frame_capacity   : int         - number of available frames

Each algorithm returns a dictionary with:
    hits       : int   - total page hits
    faults     : int   - total page faults
    fault_rate : float - faults / total references (0.0 when empty)
    hit_rate   : float - hits / total references
    history    : list of step dicts:
        {
            "step": int,            # 1-based step number
            "page": int,            # page referenced at this step
            "event": str,           # "Hit" or "Fault"
            "frames": list[int],    # frame contents after this step (copy)
        }
"""

from __future__ import annotations

from typing import Any, Dict, List


def _empty_result() -> Dict[str, Any]:
    return {
        "hits": 0,
        "faults": 0,
        "fault_rate": 0.0,
        "hit_rate": 0.0,
        "history": [],
    }


def _validate(reference_string: List[int], frame_capacity: int) -> None:
    if frame_capacity is None or int(frame_capacity) <= 0:
        raise ValueError("Frame capacity must be a positive integer.")
    if not reference_string:
        raise ValueError("Reference string must not be empty.")


def _record(history: List[Dict[str, Any]], step: int, page: int, event: str, frames: List[int]) -> None:
    history.append(
        {
            "step": step,
            "page": page,
            "event": event,
            "frames": list(frames),
        }
    )


# ---------------------------------------------------------------------------
# FIFO - First In First Out
# ---------------------------------------------------------------------------
def fifo(reference_string: List[int], frame_capacity: int) -> Dict[str, Any]:
    """First In First Out page replacement.

    Pages are loaded into frames in arrival order. On a fault with full frames,
    the oldest resident page (the one at the front of the queue) is evicted.
    """
    _validate(reference_string, frame_capacity)
    capacity = int(frame_capacity)

    frames: List[int] = []
    queue: List[int] = []  # pages in load order (front = oldest)
    hits = 0
    faults = 0
    history: List[Dict[str, Any]] = []

    for step, page in enumerate(reference_string, start=1):
        if page in frames:
            hits += 1
            _record(history, step, page, "Hit", frames)
        else:
            faults += 1
            if len(frames) < capacity:
                frames.append(page)
                queue.append(page)
            else:
                evicted = queue.pop(0)
                frames.remove(evicted)
                frames.append(page)
                queue.append(page)
            _record(history, step, page, "Fault", frames)

    total = len(reference_string)
    return {
        "hits": hits,
        "faults": faults,
        "fault_rate": round(faults / total, 4),
        "hit_rate": round(hits / total, 4),
        "history": history,
    }


# ---------------------------------------------------------------------------
# LRU - Least Recently Used
# ---------------------------------------------------------------------------
def lru(reference_string: List[int], frame_capacity: int) -> Dict[str, Any]:
    """Least Recently Used page replacement.

    The resident page that has not been referenced for the longest time is
    evicted on a fault. On a hit the page is promoted to most-recently used.
    """
    _validate(reference_string, frame_capacity)
    capacity = int(frame_capacity)

    frames: List[int] = []           # ordered from LRU (front) to MRU (back)
    hits = 0
    faults = 0
    history: List[Dict[str, Any]] = []

    for step, page in enumerate(reference_string, start=1):
        if page in frames:
            hits += 1
            frames.remove(page)
            frames.append(page)  # promote to most-recently used
            _record(history, step, page, "Hit", frames)
        else:
            faults += 1
            if len(frames) == capacity:
                frames.pop(0)  # evict least-recently used
            frames.append(page)
            _record(history, step, page, "Fault", frames)

    total = len(reference_string)
    return {
        "hits": hits,
        "faults": faults,
        "fault_rate": round(faults / total, 4),
        "hit_rate": round(hits / total, 4),
        "history": history,
    }


# ---------------------------------------------------------------------------
# OPTIMAL - Optimal page replacement (MIN)
# ---------------------------------------------------------------------------
def optimal(reference_string: List[int], frame_capacity: int) -> Dict[str, Any]:
    """Optimal page replacement.

    On a fault, the resident page whose next reference occurs farthest in the
    future (or never again) is evicted. Requires knowledge of the full string.
    """
    _validate(reference_string, frame_capacity)
    capacity = int(frame_capacity)
    n = len(reference_string)

    frames: List[int] = []
    hits = 0
    faults = 0
    history: List[Dict[str, Any]] = []

    for step, page in enumerate(reference_string, start=1):
        idx = step - 1  # zero-based index in the reference string
        if page in frames:
            hits += 1
            _record(history, step, page, "Hit", frames)
            continue

        faults += 1
        if len(frames) < capacity:
            frames.append(page)
        else:
            # Choose the resident page whose next use is farthest away.
            farthest = -1
            evict_page = frames[0]
            for resident in frames:
                next_use = None
                for future in range(idx + 1, n):
                    if reference_string[future] == resident:
                        next_use = future
                        break
                # Never referenced again -> evict immediately.
                distance = n if next_use is None else next_use
                if distance > farthest:
                    farthest = distance
                    evict_page = resident
            frames.remove(evict_page)
            frames.append(page)

        _record(history, step, page, "Fault", frames)

    total = len(reference_string)
    return {
        "hits": hits,
        "faults": faults,
        "fault_rate": round(faults / total, 4),
        "hit_rate": round(hits / total, 4),
        "history": history,
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
ALGORITHMS: Dict[str, Any] = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
}


def run_all(reference_string: List[int], frame_capacity: int) -> Dict[str, Dict[str, Any]]:
    """Run every page replacement algorithm and return results keyed by name."""
    return {
        name: func(reference_string, frame_capacity)
        for name, func in ALGORITHMS.items()
    }
