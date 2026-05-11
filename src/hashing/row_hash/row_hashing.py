import hashlib
import json
import pandas as pd
from src.utils.json_handler import read_json


def validate_identifier_columns(df, identifier_cols):
    if not identifier_cols:
        raise ValueError("No row identifier columns found in file_state.json")

    missing_cols = [col for col in identifier_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Identifier columns not found in CSV: {missing_cols}")

    if df[identifier_cols].isnull().any().any():
        raise ValueError(f"Identifier columns contain null values: {identifier_cols}")

    if df.duplicated(subset=identifier_cols).any():
        raise ValueError(f"Duplicate row identifiers found for columns: {identifier_cols}")


def normalize_value(value):
    if value is None or value == "" or pd.isna(value):
        return "NULL"

    if isinstance(value, (int, float)):
        return f"{float(value):.6f}"

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def create_row_key(row, identifier_cols):
    return "|".join(str(row[col]).strip() for col in identifier_cols)


def row_hasher(filepath):
    store = {}

    df = pd.read_csv(filepath, header=0)

    file_state = read_json("file_state.json")
    identifier_cols = file_state["row_identifier_columns"]

    validate_identifier_columns(df, identifier_cols)

    for _, row in df.iterrows():
        key = create_row_key(row, identifier_cols)

        remaining_row = row.drop(labels=identifier_cols).to_dict()

        normalized_row = {
            col: normalize_value(value)
            for col, value in remaining_row.items()
        }

        stable_row_string = json.dumps(normalized_row, sort_keys=True)

        hasher = hashlib.md5()
        hasher.update(stable_row_string.encode("utf-8"))

        store[key] = hasher.hexdigest()

    return store