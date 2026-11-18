"""Interactive OS Algorithm Lab — Streamlit application.

Modules:
    - CPU Scheduling        : FCFS, SJF, SRTF, Round Robin, Priority
    - Page Replacement      : FIFO, LRU, Optimal
    - Deadlock Avoidance    : Banker's Algorithm

Run with:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from algorithms.bankers import bankers
from algorithms.page_replacement import run_all
from algorithms.scheduling import ALGORITHMS as SCHEDULING_ALGORITHMS
from algorithms.scheduling import schedule

st.set_page_config(
    page_title="Interactive OS Algorithm Lab",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ Interactive OS Algorithm Lab")
st.caption("CPU Scheduling  •  Page Replacement  •  Deadlock Avoidance (Banker's Algorithm)")

MODULES = ["CPU Scheduling", "Page Replacement", "Deadlock Avoidance"]
module = st.sidebar.radio("Navigate to", MODULES, index=0)

# ---------------------------------------------------------------------------
# CPU Scheduling module
# ---------------------------------------------------------------------------
if module == "CPU Scheduling":
    st.header("🧮 CPU Scheduling")

    # --- Dynamic process table in session state ---------------------------
    if "processes" not in st.session_state:
        st.session_state.processes = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 3},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1},
            {"pid": "P3", "arrival_time": 2, "burst_time": 8, "priority": 4},
            {"pid": "P4", "arrival_time": 3, "burst_time": 6, "priority": 2},
        ]

    with st.expander("➕ Add / Edit Processes", expanded=True):
        with st.form("add_process_form", clear_on_submit=True):
            c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1])
            new_pid = c1.text_input("Process ID", placeholder="e.g. P5")
            new_arrival = c2.number_input("Arrival Time", min_value=0, step=1, value=0)
            new_burst = c3.number_input("Burst Time", min_value=1, step=1, value=4)
            new_priority = c4.number_input("Priority", min_value=0, step=1, value=0)
            add_clicked = c5.form_submit_button("Add Process", use_container_width=True)

            if add_clicked:
                pids = [p["pid"] for p in st.session_state.processes]
                if not new_pid.strip():
                    st.error("Process ID cannot be empty.")
                elif new_pid in pids:
                    st.error(f"Process '{new_pid}' already exists.")
                else:
                    st.session_state.processes.append(
                        {
                            "pid": new_pid.strip(),
                            "arrival_time": int(new_arrival),
                            "burst_time": int(new_burst),
                            "priority": int(new_priority),
                        }
                    )
                    st.success(f"Added process {new_pid}.")

    # Remove-process controls
    st.subheader("Current Processes")
    proc_df = pd.DataFrame(st.session_state.processes)
    if not proc_df.empty:
        for i, p in enumerate(list(st.session_state.processes)):
            cols = st.columns([1, 1, 1, 1, 0.5])
            cols[0].write(f"**{p['pid']}**")
            cols[1].write(p["arrival_time"])
            cols[2].write(p["burst_time"])
            cols[3].write(p["priority"])
            if cols[4].button("🗑️", key=f"remove_proc_{i}", help=f"Remove {p['pid']}"):
                st.session_state.processes.pop(i)
                st.rerun()

    if st.button("Clear All Processes"):
        st.session_state.processes = []
        st.rerun()

    # --- Algorithm selection ---------------------------------------------
    st.divider()
    algo_name = st.selectbox("Scheduling Algorithm", list(SCHEDULING_ALGORITHMS.keys()), index=0)
    quantum = 2
    if algo_name == "Round Robin":
        quantum = st.number_input("Time Quantum", min_value=1, step=1, value=2)
        st.caption("Round Robin is preemptive with the given time quantum.")

    if st.button("Run Scheduling Algorithm", type="primary", use_container_width=True):
        if not st.session_state.processes:
            st.warning("Please add at least one process before running.")
        else:
            try:
                result = schedule(algo_name, st.session_state.processes, quantum=quantum)

                # --- Metrics table ----------------------------------------
                st.subheader("Results")
                metrics_df = pd.DataFrame(result["processes"])
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Avg Waiting Time", f"{result['avg_waiting_time']:.3f}")
                c2.metric("Avg Turnaround Time", f"{result['avg_turnaround_time']:.3f}")
                c3.metric("Avg Response Time", f"{result['avg_response_time']:.3f}")

                # --- Gantt chart ------------------------------------------
                st.subheader("Gantt Chart")
                gantt_rows = []
                for pid, start, end in result["gantt"]:
                    gantt_rows.append({"Task": pid, "Start": int(start), "Finish": int(end)})
                gantt_df = pd.DataFrame(gantt_rows)

                if gantt_df.empty:
                    st.info("No execution segments to display.")
                else:
                    # Only apply the Idle colour mapping when an Idle segment exists.
                    colour_map = {}
                    if "Idle" in set(gantt_df["Task"]):
                        colour_map["Idle"] = "#cccccc"

                    fig = px.timeline(
                        gantt_df,
                        x_start="Start",
                        x_end="Finish",
                        y="Task",
                        color="Task",
                        title=f"Gantt Chart — {algo_name}",
                        color_discrete_map=colour_map or None,
                    )
                    fig.update_yaxes(autorange="reversed")  # conventional Gantt layout
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Process",
                        height=max(300, 200 + 40 * len(gantt_df)),
                        legend_title_text="Task",
                        bargap=0.2,
                    )
                    # Integer ticks on the (numeric) time axis.
                    fig.update_xaxes(dtick=1, tickformat="d")
                    st.plotly_chart(fig, use_container_width=True)

            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:  # pragma: no cover - defensive UI guard
                st.error(f"Unexpected error: {exc}")

# ---------------------------------------------------------------------------
# Page Replacement module
# ---------------------------------------------------------------------------
elif module == "Page Replacement":
    st.header("📄 Page Replacement")

    with st.form("page_form"):
        c1, c2 = st.columns([2, 1])
        ref_text = c1.text_area(
            "Page Reference String",
            value="1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5",
            help="Comma-separated page numbers, e.g. 1, 2, 3, 4, 1, 2, 5",
        )
        frame_capacity = c2.number_input("Frame Capacity", min_value=1, step=1, value=3)
        run_clicked = st.form_submit_button("Run All Algorithms", type="primary")

    if run_clicked:
        try:
            reference = [int(tok.strip()) for tok in ref_text.split(",") if tok.strip()]
        except ValueError:
            st.error("Reference string must contain only integers separated by commas.")
            reference = None

        if reference is not None:
            if not reference:
                st.warning("Please enter a non-empty reference string.")
            else:
                results = run_all(reference, frame_capacity)

                # --- Fault-rate comparison bar chart ----------------------
                st.subheader("Fault Rate Comparison")
                compare_df = pd.DataFrame(
                    [
                        {"Algorithm": name, "Fault Rate": res["fault_rate"], "Faults": res["faults"], "Hits": res["hits"]}
                        for name, res in results.items()
                    ]
                )
                fig = px.bar(
                    compare_df,
                    x="Algorithm",
                    y="Fault Rate",
                    text="Faults",
                    title=f"Page Fault Rate (frames = {frame_capacity}, references = {len(reference)})",
                    color="Algorithm",
                )
                fig.update_traces(texttemplate="%{text}", textposition="outside")
                fig.update_layout(yaxis_tickformat=".0%", yaxis=dict(range=[0, 1]))
                st.plotly_chart(fig, use_container_width=True)

                # --- Summary table ----------------------------------------
                st.subheader("Summary")
                st.dataframe(compare_df[["Algorithm", "Hits", "Faults", "Fault Rate"]], use_container_width=True, hide_index=True)

                # --- Step-by-step history per algorithm -------------------
                st.subheader("Step-by-Step Memory States")
                tabs = st.tabs(list(results.keys()))
                for tab, (name, res) in zip(tabs, results.items()):
                    with tab:
                        history_df = pd.DataFrame(res["history"])
                        history_df["Frames"] = history_df["frames"].apply(lambda f: "[" + ", ".join(map(str, f)) + "]")
                        history_df = history_df[["step", "page", "event", "Frames"]]
                        history_df.columns = ["Step", "Page", "Event", "Frame Contents"]
                        st.dataframe(history_df, use_container_width=True, hide_index=True)
                        st.caption(f"Hits: {res['hits']}  |  Faults: {res['faults']}  |  Fault Rate: {res['fault_rate']:.2%}")

# ---------------------------------------------------------------------------
# Deadlock Avoidance module (Banker's Algorithm)
# ---------------------------------------------------------------------------
else:
    st.header("🛡️ Deadlock Avoidance — Banker's Algorithm")

    st.write(
        "Enter the current system state. The algorithm computes the **Need** matrix "
        "(Need = Max − Allocation) and checks whether a safe sequence exists."
    )

    c1, c2 = st.columns(2)
    n_processes = c1.number_input("Number of Processes", min_value=1, step=1, value=5)
    n_resources = c2.number_input("Number of Resource Types", min_value=1, step=1, value=3)

    # (Re)initialize matrix editors when dimensions change.
    key_n = f"n_{n_processes}"
    key_m = f"m_{n_resources}"
    if st.session_state.get("bankers_dims") != (n_processes, n_resources):
        st.session_state["bankers_dims"] = (n_processes, n_resources)
        alloc_default = [[0] * n_resources for _ in range(n_processes)]
        max_default = [[0] * n_resources for _ in range(n_processes)]
        # Prefill the classic textbook example when dimensions match.
        if n_processes == 5 and n_resources == 3:
            alloc_default = [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2],
            ]
            max_default = [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3],
            ]
        st.session_state["bankers_alloc"] = alloc_default
        st.session_state["bankers_max"] = max_default
        st.session_state["bankers_avail"] = [3, 3, 2] if (n_processes, n_resources) == (5, 3) else [0] * n_resources

    alloc_df = pd.DataFrame(
        st.session_state["bankers_alloc"],
        index=[f"P{i}" for i in range(n_processes)],
        columns=[f"R{j}" for j in range(n_resources)],
    )
    max_df = pd.DataFrame(
        st.session_state["bankers_max"],
        index=[f"P{i}" for i in range(n_processes)],
        columns=[f"R{j}" for j in range(n_resources)],
    )
    avail_df = pd.DataFrame(
        [st.session_state["bankers_avail"]],
        columns=[f"R{j}" for j in range(n_resources)],
        index=["Available"],
    )

    st.subheader("Allocation Matrix")
    alloc_edited = st.data_editor(alloc_df, num_rows="fixed", use_container_width=True, key="edit_alloc")
    st.subheader("Maximum Matrix")
    max_edited = st.data_editor(max_df, num_rows="fixed", use_container_width=True, key="edit_max")
    st.subheader("Available Vector")
    avail_edited = st.data_editor(avail_df, num_rows="fixed", use_container_width=True, key="edit_avail")

    if st.button("Run Banker's Algorithm", type="primary", use_container_width=True):
        try:
            allocation = alloc_edited.astype(int).values.tolist()
            maximum = max_edited.astype(int).values.tolist()
            available = [int(v) for v in avail_edited.iloc[0].tolist()]

            result = bankers(allocation, maximum, available)

            # --- Need matrix ----------------------------------------------
            st.subheader("Need Matrix  (Need = Max − Allocation)")
            need_df = pd.DataFrame(
                result["need"],
                index=[f"P{i}" for i in range(n_processes)],
                columns=[f"R{j}" for j in range(n_resources)],
            )
            st.dataframe(need_df, use_container_width=True)

            # --- Safety verdict -------------------------------------------
            if result["safe"]:
                st.success("✅ System is in a SAFE state — no deadlock possible.")
                seq_str = " → ".join(result["safe_sequence"])
                st.markdown(f"**Safe Sequence:**  `{seq_str}`")
            else:
                st.error("❌ System is in an UNSAFE state — deadlock is possible.")
                st.markdown("**Safe Sequence:** none (not all processes can finish).")

            # --- Work / Finish trace --------------------------------------
            with st.expander("Step-by-Step Safety Trace"):
                trace_rows = []
                for entry in result["work_trace"]:
                    proc = entry["process"] or "—"
                    trace_rows.append(
                        {
                            "Step": entry["step"],
                            "Process": proc,
                            "Action": entry["action"],
                            "Work": "[" + ", ".join(map(str, entry["work"])) + "]",
                            "Finish": "[" + ", ".join("T" if f else "F" for f in entry["finish"]) + "]",
                        }
                    )
                st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)

        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - defensive UI guard
            st.error(f"Unexpected error: {exc}")

st.divider()
st.caption("Built with Streamlit • Plotly • Pandas  |  Interactive OS Algorithm Lab")
