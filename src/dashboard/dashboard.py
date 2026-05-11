import json
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Adaptive CSV Cache Engine",
    page_icon="⚡",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]
METADATA_DIR = BASE_DIR / "metadata"


def read_json(file_name):
    file_path = METADATA_DIR / file_name

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def metric_card(title, value, delta=None):
    st.metric(label=title, value=value, delta=delta)


run_data = read_json("run.json")
history_data = read_json("history.json")
config_data = read_json("config.json")
performance_data = read_json("performance.json")
partitions_data = read_json("partitions.json")
file_state = read_json("file_state.json")


st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    margin-top: 20px;
    margin-bottom: 0;
    background: linear-gradient(90deg, #00DBDE, #FC00FF, #00DBDE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 300% auto;
    animation: gradientMove 6s linear infinite;
}

@keyframes gradientMove {
    0% { background-position: 0% center; }
    100% { background-position: 300% center; }
}

.subtitle {
    font-size: 18px;
    color: #9aa0a6;
    margin-top: 4px;
    margin-bottom: 2rem;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: #60a5fa;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #1f2937);
    border: 1px solid #374151;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    border: 1px solid #60a5fa;
    box-shadow: 0 8px 20px rgba(96,165,250,0.25);
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

pre {
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    """
    <div class="main-title">
        ⚡ Adaptive CSV Cache Engine
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Parallel Incremental Processing • Dynamic Threshold Tuning • Partitioned Caching
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP KPIs
# =========================================================

if run_data and performance_data and config_data:
    incremental_time = performance_data.get("last_incremental_time")
    full_time = performance_data.get("last_full_recompute_time")

    speedup = None
    if incremental_time and full_time and incremental_time != 0:
        speedup = round(full_time / incremental_time, 2)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Execution Type", run_data.get("actual_execution", "N/A"))

    with col2:
        metric_card(
            "Execution Time",
            f"{round(run_data.get('execution_time', 0), 4)} sec"
        )

    with col3:
        metric_card("Current Threshold", config_data.get("current_threshold", "N/A"))

    with col4:
        metric_card("Speedup", f"{speedup}x" if speedup else "N/A")


# =========================================================
# CURRENT RUN
# =========================================================

st.markdown(
    '<div class="section-title">🚀 Current Run Summary</div>',
    unsafe_allow_html=True
)

if run_data:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Decision", run_data.get("decision"))

    with col2:
        metric_card("Changed Rows", run_data.get("changed_rows"))

    with col3:
        metric_card(
            "Rows Changed %",
            f"{round(run_data.get('rows_percentage_change', 0) * 100, 4)} %"
        )

    with col4:
        metric_card("Total Rows", run_data.get("total_rows"))

    st.info(f"🕒 Last Run Timestamp: {run_data.get('timestamp')}")
else:
    st.warning("run.json not found.")


# =========================================================
# PERFORMANCE SECTION
# =========================================================

st.markdown(
    '<div class="section-title">⚡ Performance Metrics</div>',
    unsafe_allow_html=True
)

if performance_data:
    col1, col2 = st.columns(2)

    incremental_time = performance_data.get("last_incremental_time")
    full_time = performance_data.get("last_full_recompute_time")

    with col1:
        metric_card(
            "Incremental Update Time",
            f"{round(incremental_time, 4)} sec" if incremental_time is not None else "N/A"
        )

    with col2:
        metric_card(
            "Full Recompute Time",
            f"{round(full_time, 4)} sec" if full_time is not None else "N/A"
        )
else:
    st.warning("performance.json not found.")


# =========================================================
# FULL VS INCREMENTAL COMPARISON
# =========================================================

st.markdown(
    '<div class="section-title">📊 Full Recompute vs Incremental Update</div>',
    unsafe_allow_html=True
)

if performance_data:
    incremental_time = performance_data.get("last_incremental_time")
    full_time = performance_data.get("last_full_recompute_time")

    if incremental_time is not None and full_time is not None:
        comparison_df = pd.DataFrame({
            "Execution Type": [
                "Incremental Update",
                "Full Recompute"
            ],
            "Execution Time (sec)": [
                incremental_time,
                full_time
            ]
        })

        st.bar_chart(comparison_df.set_index("Execution Type"))

        if incremental_time > 0:
            speedup = round(full_time / incremental_time, 2)

            st.success(
                f"🚀 Incremental CSV processing is currently **{speedup}x faster** than full recompute."
            )
    else:
        st.info("Both incremental and full recompute timings are needed for comparison.")
else:
    st.warning("performance.json not found.")


# =========================================================
# PARTITION SECTION
# =========================================================

st.markdown(
    '<div class="section-title">🧩 Partition Architecture</div>',
    unsafe_allow_html=True
)

if partitions_data:
    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Partitions", partitions_data.get("num_partitions"))

    with col2:
        metric_card("Partition Strategy", partitions_data.get("partition_strategy"))

    with col3:
        metric_card(
            "Partition Files",
            len(partitions_data.get("partition_files", []))
        )

    with st.expander("📂 View Partition Files"):
        partition_files = partitions_data.get("partition_files", [])

        partition_df = pd.DataFrame({
            "Partition Files": partition_files
        })

        st.dataframe(partition_df, use_container_width=True)
else:
    st.warning("partitions.json not found.")


# =========================================================
# THRESHOLD CONFIG
# =========================================================

st.markdown(
    '<div class="section-title">⚙️ Dynamic Threshold Tuning</div>',
    unsafe_allow_html=True
)

if config_data:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Current Threshold", config_data.get("current_threshold"))

    with col2:
        metric_card("Minimum Threshold", config_data.get("min_threshold"))

    with col3:
        metric_card("Maximum Threshold", config_data.get("max_threshold"))

    with col4:
        metric_card("Step Size", config_data.get("step_size"))
else:
    st.warning("config.json not found.")


# =========================================================
# HISTORY ANALYTICS
# =========================================================

st.markdown(
    '<div class="section-title">📈 Historical Analytics</div>',
    unsafe_allow_html=True
)

if history_data and history_data.get("history"):
    history_df = pd.DataFrame(history_data["history"])

    st.subheader("Execution Time Trend")
    st.line_chart(history_df["execution_time"])

    st.subheader("Threshold Trend")
    st.line_chart(history_df["threshold_used"])

    st.subheader("Rows Changed Trend")
    st.line_chart(history_df["rows_percentage_change"])

    st.subheader("Execution Type Distribution")
    execution_counts = history_df["actual_execution"].value_counts()
    st.bar_chart(execution_counts)

    st.subheader("Run History Table")
    st.dataframe(history_df, use_container_width=True)

else:
    st.info("No history data available yet.")


# =========================================================
# FILE STATE
# =========================================================

st.markdown(
    '<div class="section-title">🗂️ File State Metadata</div>',
    unsafe_allow_html=True
)

if file_state:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Input File")
        st.code(file_state.get("input_file_path"))

        st.markdown("### Last File Hash")
        st.code(file_state.get("last_file_hash"))

    with col2:
        st.markdown("### Processed Partition Folder")
        st.code(file_state.get("processed_file_path"))

        st.metric(
            "Stored Row Hashes",
            len(file_state.get("row_hashes", {}))
        )
else:
    st.warning("file_state.json not found.")


# =========================================================
# CONCLUSION
# =========================================================

st.markdown(
    '<div class="section-title">🏁 Conclusion</div>',
    unsafe_allow_html=True
)

if performance_data:
    incremental_time = performance_data.get("last_incremental_time")
    full_time = performance_data.get("last_full_recompute_time")

    if incremental_time is not None and full_time is not None and incremental_time > 0:
        speedup = round(full_time / incremental_time, 2)

        st.success(
            f"""
            ✅ The adaptive CSV caching engine is working successfully.

            By using row hashing, partitioned storage, parallel partition updates, and dynamic threshold tuning,
            the system is currently loading/updating CSV data **{speedup}x faster** than full recomputation.
            """
        )
    else:
        st.info("Run both full recompute and incremental update once to generate a final speedup conclusion.")
else:
    st.warning("performance.json not found.")


st.markdown("---")
st.caption(
    "Adaptive CSV Cache Engine • Partitioned Incremental Processing • Parallel Execution Framework"
)