"""
Change Detection Output Structure:

{
  "updated_rows": [],
  "new_rows": [],
  "deleted_rows": [],
  "changed_rows": 0,
  "total_rows": 0,
  "rows_percentage_change": 0.0
}

"""


def get_structure():
    return {
        "updated_rows": [],
        "new_rows": [],
        "deleted_rows": [],
        "changed_rows": 0,
        "total_rows": 0,
        "rows_percentage_change": 0.0
    }


def detect_changes(old_row_hashes, new_row_hashes):
    data = get_structure()

    old_keys = old_row_hashes.keys()
    new_keys = new_row_hashes.keys()

    common_keys = old_keys & new_keys

    data["updated_rows"] = [
        key for key in common_keys
        if old_row_hashes[key] != new_row_hashes[key]
    ]

    data["new_rows"] = list(new_keys - old_keys)
    data["deleted_rows"] = list(old_keys - new_keys)

    data["changed_rows"] = (
        len(data["updated_rows"])
        + len(data["new_rows"])
        + len(data["deleted_rows"])
    )

    data["total_rows"] = len(new_row_hashes)

    data["rows_percentage_change"] = (
        data["changed_rows"] / data["total_rows"]
        if data["total_rows"] != 0
        else 0.0
    )

    return data