
import time
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.pipeline.partitioner.partition_manager import (
    create_partitions_from_csv,
    get_affected_partitions,
    load_partition_df,
    save_partition_df
)

from src.pipeline.updater.row_updater import (
    delete_removed_rows,
    update_existing_rows,
    add_new_rows
)

from src.utils.json_handler import read_json


def process_single_partition(
    partition_id,
    processed_path,
    raw_df,
    identifier_cols,
    change_report
):
    partition_df = load_partition_df(
        processed_path,
        partition_id
    )

    partition_df = delete_removed_rows(
        partition_df,
        identifier_cols,
        change_report["deleted_rows"]
    )

    partition_df = update_existing_rows(
        partition_df,
        raw_df,
        identifier_cols,
        change_report["updated_rows"]
    )

    partition_df = add_new_rows(
        partition_df,
        raw_df,
        identifier_cols,
        change_report["new_rows"]
    )

    save_partition_df(
        partition_df,
        processed_path,
        partition_id
    )

    return partition_id


def execute_pipeline(decision_output, change_report, csv_path, processed_path, identifier_cols):
    decision = decision_output["decision"]
    actual_execution = decision
    partition_metadata = None

    start_time = time.time()

    # ---------------- FULL RECOMPUTE ----------------
    if decision == "full_recompute":
        print("Running Full Recompute with Partitioning...")

        partition_metadata = create_partitions_from_csv(
            csv_path,
            processed_path,
            identifier_cols
        )

        actual_execution = "full_recompute"

    # ---------------- INCREMENTAL UPDATE ----------------
    elif decision == "incremental_update":
        print("Running Incremental Update...")
        print(f"Updated Rows: {change_report['updated_rows']}")
        print(f"New Rows: {change_report['new_rows']}")
        print(f"Deleted Rows: {change_report['deleted_rows']}")

        if not os.path.exists(processed_path):
            print("Partition folder not found. Falling back to full recompute...")

            partition_metadata = create_partitions_from_csv(
                csv_path,
                processed_path,
                identifier_cols
            )

            actual_execution = "full_recompute"

        else:
            print("Running Parallel Partitioned Incremental Update...")

            partitions_metadata = read_json("partitions.json")
            num_partitions = partitions_metadata["num_partitions"]

            affected_partitions = get_affected_partitions(
                change_report["updated_rows"],
                change_report["new_rows"],
                change_report["deleted_rows"],
                num_partitions
            )

            print(f"Affected Partitions: {affected_partitions}")

            raw_df = pd.read_csv(csv_path)

            max_workers = min(len(affected_partitions), os.cpu_count() or 1)

            if affected_partitions:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(
                            process_single_partition,
                            partition_id,
                            processed_path,
                            raw_df,
                            identifier_cols,
                            change_report
                        )
                        for partition_id in affected_partitions
                    ]

                    for future in as_completed(futures):
                        completed_partition = future.result()
                        print(f"Partition {completed_partition} updated successfully.")
            else:
                print("No affected partitions found. Nothing to update.")

            actual_execution = "incremental_update"

    else:
        raise ValueError(f"Unknown decision: {decision}")

    end_time = time.time()
    execution_time = end_time - start_time

    return execution_time, actual_execution, partition_metadata
























