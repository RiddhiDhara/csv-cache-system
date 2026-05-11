import os
import hashlib
import pandas as pd


def get_file_size(csv_path):
    
    file_size = os.path.getsize(csv_path) 
    
    return file_size


def decide_num_partitions(file_size):
    # less than 100 KB
    if file_size < 100 * 1024:
        return 4
    # 100 KB to 500 KB
    elif file_size < 500 * 1024:
        return 8
    # 500 KB to 1 MB
    elif file_size < 1 * 1024 * 1024:
        return 16
    # 1 MB to 10 MB
    elif file_size < 10 * 1024 * 1024:
        return 32
    # 10 MB to 100 MB
    elif file_size < 100 * 1024 * 1024:
        return 64
    # greater than 100 MB
    else:
        return 128


def create_row_key(row, identifier_cols):

    key_parts = []
    for col in identifier_cols:
        key_parts.append(str(row[col]))
    row_key = "|".join(key_parts)
    
    return row_key


def get_partition_id(row_key, num_partitions):

    row_key_byte = row_key.encode("utf-8")
    hasher = hashlib.md5()
    hasher.update(row_key_byte)
    get_hash = hasher.hexdigest()
    hash_integer = int(get_hash, 16)
    partition_id = hash_integer % num_partitions
    
    return partition_id


def create_partition_folder(partition_folder_path):

    if not os.path.exists(partition_folder_path):
        os.makedirs(partition_folder_path)


def clear_old_partitions(partition_folder_path):

    if not os.path.exists(partition_folder_path):
        return
    for file_name in os.listdir(partition_folder_path):
        if file_name.startswith("part_") and file_name.endswith(".csv"):
            file_path = os.path.join(partition_folder_path, file_name)
            os.remove(file_path)

def write_full_partitions(raw_df, partition_folder_path, identifier_cols, num_partitions):
    
    partition_buckets = {i: [] for i in range(num_partitions)}
    # distribute rows into buckets
    for _, row in raw_df.iterrows():
        row_key = create_row_key(row, identifier_cols)
        partition_id = get_partition_id(row_key, num_partitions)
        partition_buckets[partition_id].append(row)
        
    partition_files = []

    # write each partition into CSV
    for partition_id, rows in partition_buckets.items():
        partition_df = pd.DataFrame(rows)
        file_name = f"part_{partition_id}.csv"
        file_path = os.path.join(partition_folder_path, file_name)
        partition_df.to_csv(file_path, index=False)
        partition_files.append(file_name)

    return partition_files


def build_partition_metadata(num_partitions, identifier_cols, partition_folder_path, partition_files):
    metadata = {
        "num_partitions": num_partitions,
        "partition_strategy": "md5",
        "partition_key_columns": identifier_cols,
        "partition_folder_path": partition_folder_path,
        "partition_files": partition_files
    }

    return metadata


def get_partition_file_path(partition_folder_path, partition_id):

    file_name = f"part_{partition_id}.csv"
    file_path = os.path.join(partition_folder_path, file_name)

    return file_path


def get_affected_partitions(updated_rows, new_rows, deleted_rows, num_partitions):

    affected_partitions = set()
    all_changed_rows = (updated_rows + new_rows + deleted_rows)
    for row_key in all_changed_rows:
        partition_id = get_partition_id(row_key, num_partitions)
        affected_partitions.add(partition_id)

    return affected_partitions


def load_partition_df(partition_folder_path, partition_id):

    file_path = get_partition_file_path(
        partition_folder_path,
        partition_id
    )
    if os.path.exists(file_path):
        partition_df = pd.read_csv(file_path)
    else:
        partition_df = pd.DataFrame()

    return partition_df


def save_partition_df(partition_df, partition_folder_path, partition_id):

    file_path = get_partition_file_path(
        partition_folder_path,
        partition_id
    )
    partition_df.to_csv(file_path, index=False)


# main public function
def create_partitions_from_csv(csv_path, partition_folder_path, identifier_cols):

    # get file size
    file_size = get_file_size(csv_path)
    # decide number of partitions
    num_partitions = decide_num_partitions(file_size)
    # create partition folder
    create_partition_folder(partition_folder_path)
    # clear old partition files
    clear_old_partitions(partition_folder_path)
    # load raw csv
    raw_df = pd.read_csv(csv_path)
    # write partition csv files
    partition_files = write_full_partitions(
        raw_df,
        partition_folder_path,
        identifier_cols,
        num_partitions
    )
    # build metadata
    metadata = build_partition_metadata(
        num_partitions,
        identifier_cols,
        partition_folder_path,
        partition_files
    )

    return metadata