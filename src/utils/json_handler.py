import json
from pathlib import Path


# Project root:
# json_handler.py -> src/utils/json_handler.py
# parents[2] takes us back to project root
BASE_DIR = Path(__file__).resolve().parents[2]
METADATA_DIR = BASE_DIR / "metadata"


def read_json(file_name):
    """
    Reads a JSON file from the metadata folder
    and returns it as a Python dictionary.
    """
    file_path = METADATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_name, data):
    """
    Writes a Python dictionary into a JSON file
    inside the metadata folder.
    """
    file_path = METADATA_DIR / file_name

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)