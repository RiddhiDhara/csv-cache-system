def both_not_null(i_time, fr_time):
    return i_time is not None and fr_time is not None


def threshold_tuner(performance, config):
    # from performance
    last_incremental_time = performance["last_incremental_time"]
    last_full_recompute_time = performance["last_full_recompute_time"]

    # from config
    current_threshold = config["current_threshold"]
    min_threshold = config["min_threshold"]
    max_threshold = config["max_threshold"]
    step_size = config["step_size"]

    # if we don't have both values, do nothing
    if not both_not_null(last_incremental_time, last_full_recompute_time):
        return current_threshold

    # incremental is faster → increase threshold
    if last_incremental_time < last_full_recompute_time:
        new_threshold = current_threshold + step_size
        if new_threshold > max_threshold:
            new_threshold = max_threshold

    # full recompute is faster → decrease threshold
    elif last_full_recompute_time < last_incremental_time:
        new_threshold = current_threshold - step_size
        if new_threshold < min_threshold:
            new_threshold = min_threshold

    # equal → no change
    else:
        new_threshold = current_threshold

    return round(new_threshold, 2)