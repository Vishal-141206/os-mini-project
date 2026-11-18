"""Pytest suite for the Interactive OS Algorithm Lab.

Uses classic textbook operating-systems examples to verify algorithmic
correctness. Run with:  pytest tests/test_algorithms.py
"""

import pytest

from algorithms.scheduling import schedule
from algorithms.page_replacement import fifo, lru, optimal, run_all
from algorithms.bankers import bankers


# ---------------------------------------------------------------------------
# Shared textbook example: 4 processes with varied arrival times
# P1: AT=0 BT=5  P2: AT=1 BT=3  P3: AT=2 BT=8  P4: AT=3 BT=6
# ---------------------------------------------------------------------------
TEXTBOOK_PROCS = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 6},
]


def _metrics(result):
    return {p["pid"]: p for p in result["processes"]}


# ---------------------------------------------------------------------------
# CPU Scheduling tests
# ---------------------------------------------------------------------------
class TestFCFS:
    def test_order_and_metrics(self):
        result = schedule("FCFS", TEXTBOOK_PROCS)
        m = _metrics(result)
        # Execution order follows arrival time.
        assert [g[0] for g in result["gantt"]] == ["P1", "P2", "P3", "P4"]
        assert m["P1"]["waiting_time"] == 0
        assert m["P2"]["waiting_time"] == 4   # starts at 5, arrived at 1
        assert m["P3"]["waiting_time"] == 6   # starts at 8, arrived at 2
        assert m["P4"]["waiting_time"] == 13  # starts at 16, arrived at 3
        assert result["avg_waiting_time"] == pytest.approx(5.75)
        # Non-preemptive: response time equals waiting time.
        for p in result["processes"]:
            assert p["response_time"] == p["waiting_time"]

    def test_turnaround_equals_waiting_plus_burst(self):
        result = schedule("FCFS", TEXTBOOK_PROCS)
        for p in result["processes"]:
            assert p["turnaround_time"] == p["waiting_time"] + p["burst_time"]

    def test_gantt_segments_are_chronological(self):
        result = schedule("FCFS", TEXTBOOK_PROCS)
        for i in range(1, len(result["gantt"])):
            assert result["gantt"][i - 1][2] <= result["gantt"][i][1]

    def test_empty_input(self):
        result = schedule("FCFS", [])
        assert result["processes"] == []
        assert result["gantt"] == []
        assert result["avg_waiting_time"] == 0.0


class TestSJF:
    def test_shortest_job_first_order(self):
        result = schedule("SJF (Non-Preemptive)", TEXTBOOK_PROCS)
        assert [g[0] for g in result["gantt"]] == ["P1", "P2", "P4", "P3"]
        m = _metrics(result)
        assert m["P1"]["waiting_time"] == 0
        assert m["P2"]["waiting_time"] == 4
        assert m["P4"]["waiting_time"] == 5   # starts at 8, arrived at 3
        assert m["P3"]["waiting_time"] == 12  # starts at 14, arrived at 2
        assert result["avg_waiting_time"] == pytest.approx(5.25)

    def test_idle_time_before_first_arrival(self):
        procs = [{"pid": "P1", "arrival_time": 5, "burst_time": 2}]
        result = schedule("SJF (Non-Preemptive)", procs)
        assert result["gantt"] == [("Idle", 0, 5), ("P1", 5, 7)]


class TestSRTF:
    def test_preemptive_order_and_metrics(self):
        result = schedule("SRTF (Preemptive)", TEXTBOOK_PROCS)
        # P1 starts, is preempted by shorter P2 at t=1, resumes after P2.
        assert result["gantt"][0] == ("P1", 0, 1)
        assert result["gantt"][1] == ("P2", 1, 4)
        assert result["gantt"][2] == ("P1", 4, 8)
        m = _metrics(result)
        assert m["P1"]["waiting_time"] == 3
        assert m["P2"]["waiting_time"] == 0
        assert m["P3"]["waiting_time"] == 12
        assert m["P4"]["waiting_time"] == 5
        assert result["avg_waiting_time"] == pytest.approx(5.0)

    def test_response_time_is_first_dispatch(self):
        result = schedule("SRTF (Preemptive)", TEXTBOOK_PROCS)
        m = _metrics(result)
        assert m["P1"]["response_time"] == 0
        assert m["P2"]["response_time"] == 0   # dispatched at its arrival t=1
        assert m["P4"]["response_time"] == 5   # first dispatched at t=8


class TestRoundRobin:
    def test_round_robin_metrics_q2(self):
        result = schedule("Round Robin", TEXTBOOK_PROCS, quantum=2)
        m = _metrics(result)
        assert m["P1"]["waiting_time"] == 9
        assert m["P2"]["waiting_time"] == 7
        assert m["P3"]["waiting_time"] == 12
        assert m["P4"]["waiting_time"] == 11
        assert result["avg_waiting_time"] == pytest.approx(9.75)
        assert m["P1"]["response_time"] == 0
        assert m["P2"]["response_time"] == 1   # first dispatched at t=2, arrived t=1

    def test_invalid_quantum_raises(self):
        with pytest.raises(ValueError):
            schedule("Round Robin", TEXTBOOK_PROCS, quantum=0)


class TestPriority:
    def test_lowest_priority_number_wins(self):
        procs = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 3},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1},
            {"pid": "P3", "arrival_time": 2, "burst_time": 8, "priority": 4},
            {"pid": "P4", "arrival_time": 3, "burst_time": 6, "priority": 2},
        ]
        result = schedule("Priority (Non-Preemptive)", procs)
        assert [g[0] for g in result["gantt"]] == ["P1", "P2", "P4", "P3"]


# ---------------------------------------------------------------------------
# Page Replacement tests
# ---------------------------------------------------------------------------
class TestPageReplacement:
    REFERENCE_STRING = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    FRAMES = 3

    def test_fifo_classic_example(self):
        result = fifo(self.REFERENCE_STRING, self.FRAMES)
        assert result["hits"] == 3
        assert result["faults"] == 9
        assert result["fault_rate"] == pytest.approx(0.75)
        assert len(result["history"]) == len(self.REFERENCE_STRING)

    def test_lru_classic_example(self):
        result = lru(self.REFERENCE_STRING, self.FRAMES)
        assert result["hits"] == 2
        assert result["faults"] == 10
        assert result["fault_rate"] == pytest.approx(round(10 / 12, 4))

    def test_optimal_classic_example(self):
        result = optimal(self.REFERENCE_STRING, self.FRAMES)
        assert result["hits"] == 5
        assert result["faults"] == 7
        assert result["fault_rate"] == pytest.approx(round(7 / 12, 4))

    def test_fault_plus_hit_equals_total(self):
        for algo in (fifo, lru, optimal):
            result = algo(self.REFERENCE_STRING, self.FRAMES)
            assert result["hits"] + result["faults"] == len(self.REFERENCE_STRING)
            assert result["fault_rate"] + result["hit_rate"] == pytest.approx(1.0)

    def test_history_records_every_step(self):
        result = fifo(self.REFERENCE_STRING, self.FRAMES)
        assert [h["step"] for h in result["history"]] == list(range(1, 13))
        assert all(set(h.keys()) == {"step", "page", "event", "frames"} for h in result["history"])
        assert all(h["event"] in ("Hit", "Fault") for h in result["history"])

    def test_empty_reference_string(self):
        with pytest.raises(ValueError):
            fifo([], 3)

    def test_invalid_frame_capacity(self):
        with pytest.raises(ValueError):
            fifo([1, 2, 3], 0)
        with pytest.raises(ValueError):
            fifo([1, 2, 3], -1)

    def test_single_frame_faults_on_every_change(self):
        result = fifo([1, 2, 1, 2], 1)
        assert result["faults"] == 4


# ---------------------------------------------------------------------------
# Banker's Algorithm tests
# ---------------------------------------------------------------------------
class TestBankers:
    def test_textbook_safe_state(self):
        allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        maximum = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]
        available = [3, 3, 2]
        result = bankers(allocation, maximum, available)
        assert result["safe"] is True
        assert result["safe_sequence"] == ["P1", "P3", "P4", "P0", "P2"]
        assert result["need"] == [
            [7, 4, 3],
            [1, 2, 2],
            [6, 0, 0],
            [0, 1, 1],
            [4, 3, 1],
        ]

    def test_unsafe_state(self):
        # All resources allocated; neither process can obtain its remaining need.
        allocation = [[1], [1]]
        maximum = [[2], [2]]
        available = [0]
        result = bankers(allocation, maximum, available)
        assert result["safe"] is False
        assert result["safe_sequence"] == []

    def test_need_matrix_is_max_minus_allocation(self):
        allocation = [[1, 0], [0, 1]]
        maximum = [[3, 2], [2, 3]]
        available = [1, 1]
        result = bankers(allocation, maximum, available)
        assert result["need"] == [[2, 2], [2, 2]]

    def test_mismatched_dimensions_raise(self):
        with pytest.raises(ValueError):
            bankers([[1], [1]], [[1]], [0])
        with pytest.raises(ValueError):
            bankers([[1], [1]], [[1], [1]], [])

    def test_all_finished_is_safe(self):
        allocation = [[0], [0]]
        maximum = [[0], [0]]
        available = [0]
        result = bankers(allocation, maximum, available)
        assert result["safe"] is True
        assert result["safe_sequence"] == ["P0", "P1"]
