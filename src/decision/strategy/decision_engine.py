def get_output_structure():
    return {
        "decision": None,
        "threshold_used": None
    }


def decision_engine(change_report, config):
    rows_percentage_change = change_report["rows_percentage_change"]
    current_threshold = config["current_threshold"]

    output = get_output_structure()

    if rows_percentage_change <= current_threshold:
        output["decision"] = "incremental_update"
    else:
        output["decision"] = "full_recompute"

    output["threshold_used"] = current_threshold

    return output