def calculate_pace(distance_m: float, time_s: float) -> dict:
    if distance_m <= 0 or time_s <= 0:
        return {"error": "distance_m and time_s must be positive"}
    pace_per_km = (time_s / 60) / (distance_m / 1000)
    pace_min = int(pace_per_km)
    pace_sec = round((pace_per_km - pace_min) * 60)
    speed_kmh = round((distance_m / 1000) / (time_s / 3600), 2)
    return {
        "distance_m": distance_m,
        "time_s": time_s,
        "pace_per_km": f"{pace_min}:{pace_sec:02d}",
        "speed_kmh": speed_kmh,
    }


RACE_PREDICTIONS = {
    3000: 1.07,
    5000: 1.06,
    10000: 1.05,
    21097: 1.04,
    42195: 1.03,
}


def predict_race_time(recent_distance_m: float, recent_time_s: float, target_distance_m: float) -> dict:
    if recent_distance_m <= 0 or recent_time_s <= 0 or target_distance_m <= 0:
        return {"error": "All inputs must be positive"}
    recent_pace = recent_time_s / recent_distance_m
    factor = 1.05
    for dist, f in RACE_PREDICTIONS.items():
        if target_distance_m >= dist:
            factor = f
    predicted_time_s = round(recent_pace * target_distance_m * factor)
    return {
        "recent_distance_m": recent_distance_m,
        "recent_time_s": recent_time_s,
        "target_distance_m": target_distance_m,
        "predicted_time_s": predicted_time_s,
    }


def calculate_splits(target_distance_m: float, target_time_s: float, split_distance_m: float = 1000) -> dict:
    if target_distance_m <= 0 or target_time_s <= 0 or split_distance_m <= 0:
        return {"error": "All inputs must be positive"}
    num_splits = int(target_distance_m // split_distance_m)
    pace_per_m = target_time_s / target_distance_m
    splits = []
    cumulative_s = 0.0
    for i in range(1, num_splits + 1):
        cumulative_s += pace_per_m * split_distance_m
        splits.append({
            "split_num": i,
            "distance_m": i * split_distance_m,
            "cumulative_time_s": round(cumulative_s),
        })
    remaining = target_distance_m - num_splits * split_distance_m
    if remaining > 0:
        cumulative_s += pace_per_m * remaining
        splits.append({
            "split_num": num_splits + 1,
            "distance_m": target_distance_m,
            "cumulative_time_s": round(cumulative_s),
        })
    return {
        "target_distance_m": target_distance_m,
        "target_time_s": target_time_s,
        "splits": splits,
    }


def training_zones(max_hr: int, resting_hr: int) -> dict:
    if max_hr <= 0 or resting_hr <= 0 or resting_hr >= max_hr:
        return {"error": "max_hr must be > resting_hr and both must be positive"}
    hrr = max_hr - resting_hr
    zones = {
        "1_recovery": {
            "range": f"<{int(resting_hr + 0.59 * hrr)} bpm",
            "percent_of_max": "<60%",
            "purpose": "Recovery, warm-up, cool-down",
        },
        "2_endurance": {
            "range": f"{int(resting_hr + 0.60 * hrr)}-{int(resting_hr + 0.69 * hrr)} bpm",
            "percent_of_max": "60-70%",
            "purpose": "Aerobic base, fat burning",
        },
        "3_tempo": {
            "range": f"{int(resting_hr + 0.70 * hrr)}-{int(resting_hr + 0.79 * hrr)} bpm",
            "percent_of_max": "70-80%",
            "purpose": "Aerobic fitness, marathon pace",
        },
        "4_threshold": {
            "range": f"{int(resting_hr + 0.80 * hrr)}-{int(resting_hr + 0.89 * hrr)} bpm",
            "percent_of_max": "80-90%",
            "purpose": "Lactate threshold, 10K pace",
        },
        "5_vo2max": {
            "range": f"{int(resting_hr + 0.90 * hrr)}-{max_hr} bpm",
            "percent_of_max": "90-100%",
            "purpose": "VO2max, intervals, 5K pace",
        },
    }
    return {"max_hr": max_hr, "resting_hr": resting_hr, "zones": zones}
