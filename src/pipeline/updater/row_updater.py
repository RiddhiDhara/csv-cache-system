import pandas as pd


def delete_removed_rows(processed_df, identifier_cols, deleted_rows):
    if not deleted_rows:
        return processed_df

    deleted_keys = set(deleted_rows)

    processed_df["_row_key"] = processed_df[identifier_cols].astype(str).agg("|".join, axis=1)

    processed_df = processed_df[
        ~processed_df["_row_key"].isin(deleted_keys)
    ]

    processed_df = processed_df.drop(columns=["_row_key"])

    return processed_df


def update_existing_rows(processed_df, raw_df, identifier_cols, updated_rows):
    if not updated_rows:
        return processed_df

    updated_keys = set(updated_rows)

    processed_df["_row_key"] = processed_df[identifier_cols].astype(str).agg("|".join, axis=1)
    raw_df["_row_key"] = raw_df[identifier_cols].astype(str).agg("|".join, axis=1)

    processed_df = processed_df[
        ~processed_df["_row_key"].isin(updated_keys)
    ]

    rows_to_update = raw_df[
        raw_df["_row_key"].isin(updated_keys)
    ]

    processed_df = processed_df.drop(columns=["_row_key"])
    rows_to_update = rows_to_update.drop(columns=["_row_key"])

    return pd.concat([processed_df, rows_to_update], ignore_index=True)


def add_new_rows(processed_df, raw_df, identifier_cols, new_rows):
    if not new_rows:
        return processed_df

    new_keys = set(new_rows)

    raw_df["_row_key"] = raw_df[identifier_cols].astype(str).agg("|".join, axis=1)

    rows_to_add = raw_df[
        raw_df["_row_key"].isin(new_keys)
    ]

    rows_to_add = rows_to_add.drop(columns=["_row_key"])

    return pd.concat([processed_df, rows_to_add], ignore_index=True)