from pathlib import Path
from datetime import datetime

from src.hashing.file_hash.file_hashing import file_hasher
from src.hashing.row_hash.row_hashing import row_hasher
from src.cache.comparator.change_detector import detect_changes
from src.decision.strategy.decision_engine import decision_engine
from src.decision.tuner.threshold_tuner import threshold_tuner
from src.pipeline.executor.pipeline_executor import execute_pipeline
from src.utils.json_handler import read_json, write_json


def main():
    base_dir = Path(__file__).resolve().parents[1]

    csv_path = base_dir / "data" / "raw" / "Titanic-Dataset.csv"
    processed_path = base_dir / "data" / "processed" / "partitions"

    print("Starting pipeline check...")
    print(f"CSV File: {csv_path}")
    print(f"Processed Partition Folder: {processed_path}")

    file_state = read_json("file_state.json")
    config = read_json("config.json")
    performance = read_json("performance.json")
    history = read_json("history.json")

    identifier_cols = file_state["row_identifier_columns"]
    old_row_hashes = file_state.get("row_hashes", {})

    new_file_hash = file_hasher(str(csv_path))
    new_row_hashes = row_hasher(str(csv_path))

    print(f"New File Hash: {new_file_hash}")
    print(f"Total Row Hashes Generated: {len(new_row_hashes)}")

    change_report = detect_changes(old_row_hashes, new_row_hashes)

    decision_output = decision_engine(change_report, config)

    print("\nDecision Output:")
    print(f"Decision: {decision_output['decision']}")
    print(f"Threshold Used: {decision_output['threshold_used']}")

    execution_time, actual_execution, partition_metadata = execute_pipeline(
        decision_output,
        change_report,
        str(csv_path),
        str(processed_path),
        identifier_cols
    )

    if partition_metadata is not None:
        write_json("partitions.json", partition_metadata)
        print("partitions.json updated successfully.")

    run_data = {
        "decision": decision_output["decision"],
        "actual_execution": actual_execution,
        "rows_percentage_change": change_report["rows_percentage_change"],
        "changed_rows": change_report["changed_rows"],
        "total_rows": change_report["total_rows"],
        "execution_time": execution_time,
        "threshold_used": decision_output["threshold_used"],
        "timestamp": datetime.now().isoformat()
    }

    # ---------------- RUN.JSON ----------------
    write_json("run.json", run_data)
    print("\nrun.json updated successfully.")

    # ---------------- HISTORY.JSON ----------------
    history["history"].append(run_data)

    write_json("history.json", history)
    print("history.json updated successfully.")

    # ---------------- PERFORMANCE.JSON ----------------
    if actual_execution == "incremental_update":
        performance["last_incremental_time"] = execution_time

    elif actual_execution == "full_recompute":
        performance["last_full_recompute_time"] = execution_time

    write_json("performance.json", performance)
    print("performance.json updated successfully.")

    # ---------------- THRESHOLD TUNING ----------------
    new_threshold = threshold_tuner(performance, config)
    config["current_threshold"] = new_threshold

    write_json("config.json", config)
    print(f"config.json updated successfully. New threshold: {new_threshold}")

    # ---------------- FILE STATE ----------------
    file_state["input_file_path"] = str(csv_path)
    file_state["last_file_hash"] = new_file_hash
    file_state["processed_file_path"] = str(processed_path)
    file_state["row_hashes"] = new_row_hashes

    write_json("file_state.json", file_state)
    print("file_state.json updated successfully.")


if __name__ == "__main__":
    main()












































