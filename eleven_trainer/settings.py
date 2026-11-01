"""Validate the observed string-valued settings format and build sequences."""

from copy import deepcopy
import json
import math
from pathlib import Path

MAX_ROWS = 5000  # Local allocation guard, not a claimed game limit.
FIELDS = {
    "position": ("x", "y", "z"),
    "direction": ("horizontalAngle", "verticalAngle"),
    "spin": ("topBottom", "leftRight", "screw"),
    "speedAndRate": ("speed", "secondsPerLaunch", "PostDelay"),
}


def finite_number(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a numeric string")
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def validate(data):
    if not isinstance(data, dict) or data.get("settingsVersion") != "1":
        raise ValueError("Expected settingsVersion '1'; unsupported settings format")
    if data.get("shuffle") not in ("True", "False"):
        raise ValueError("shuffle must be the string 'True' or 'False'")
    shots = data.get("shots")
    rows = shots.get("data") if isinstance(shots, dict) else None
    if not isinstance(rows, dict) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError(f"Expected 1..{MAX_ROWS} rows in shots.data")
    active = 0
    for key, row in rows.items():
        if not isinstance(row, dict) or row.get("isActive") not in ("True", "False"):
            raise ValueError(f"{key}: isActive must be 'True' or 'False'")
        if not isinstance(row.get("DataName"), str):
            raise ValueError(f"{key}: DataName must be a string")
        active += row["isActive"] == "True"
        for group, names in FIELDS.items():
            for part in ("raw", "spread"):
                values = row.get(group, {}).get(part, {}) if isinstance(row.get(group), dict) else {}
                if not isinstance(values, dict):
                    raise ValueError(f"{key}.{group}.{part} must be an object")
                for name in names:
                    number = finite_number(values.get(name), f"{key}.{group}.{part}.{name}")
                    if group == "speedAndRate" and part == "raw":
                        if (name != "PostDelay" and number <= 0) or (name == "PostDelay" and number < 0):
                            raise ValueError(f"{key}: speed/interval must be positive; PostDelay nonnegative")
    if not active:
        raise ValueError("At least one shot must be active")
    return data


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(payload):
    return validate(json.loads(payload, object_pairs_hook=_unique_object))


def load(path):
    return decode(Path(path).read_bytes())


def encode(data):
    validate(data)
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def save_new(path, payload):
    """Never overwrite a player's source file implicitly."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def build(source, selections=None, phases=(10, 2), interval=None):
    validate(source)
    rows = source["shots"]["data"]
    keys = list(selections) if selections else [key for key, row in rows.items() if row["isActive"] == "True"]
    if not keys or any(key not in rows for key in keys):
        raise ValueError("Selection is empty or contains an unknown shot ID; use 'list'")
    if not phases or any(type(count) is not int or count <= 0 for count in phases):
        raise ValueError("Phase counts must be positive integers")
    if len(keys) * sum(phases) > MAX_ROWS:
        raise ValueError(f"Sequence exceeds local limit of {MAX_ROWS} rows")
    if interval is not None and (not math.isfinite(interval) or interval <= 0):
        raise ValueError("Interval must be positive and finite")
    result = deepcopy(source)
    result["shuffle"] = "False"
    result["shots"]["data"] = {}
    for phase, count in enumerate(phases, 1):
        for step, key in enumerate(keys, 1):
            for repeat in range(1, count + 1):
                row = deepcopy(rows[key])
                row["isActive"] = "True"
                row["DataName"] = f"{phase}.{step:02} {repeat:02}/{count:02} {row['DataName']}"
                if interval is not None:
                    row["speedAndRate"]["raw"]["secondsPerLaunch"] = format(interval, "g")
                    row["speedAndRate"]["spread"]["secondsPerLaunch"] = "0"
                result["shots"]["data"][f"ET{len(result['shots']['data']) + 1:05}"] = row
    return validate(result)


def summary(data):
    rows = list(data["shots"]["data"].values())
    active = [row for row in rows if row["isActive"] == "True"]
    return {"rows": len(rows), "active_rows": len(active), "shuffle": data["shuffle"],
            "nominal_interval_sum_seconds": round(sum(float(row["speedAndRate"]["raw"]["secondsPerLaunch"]) for row in active), 3)}
