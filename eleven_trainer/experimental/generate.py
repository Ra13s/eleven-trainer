"""Generate independent, UNCALIBRATED Eleven ball-machine experiment artifacts.

No existing game presets, community packs, or network data are read.
Inputs are this script's declared SI model and an explicit calibration JSON.
Python 3.11+; run: python -m eleven_trainer.experimental.generate
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import uuid
from copy import deepcopy
import hashlib

from ..settings import build as build_cycle, encode, summary

ROOT = Path(__file__).resolve().parent
G = 9.81
TABLE_LENGTH = 2.74
TABLE_WIDTH = 1.525
TABLE_TOP = 0.76
NET_ABOVE_TABLE = 0.1525
BALL_RADIUS = 0.020
LAUNCH = (0.0, 1.18, -1.60)
LANDING_HEIGHT = TABLE_TOP + BALL_RADIUS

# target x/z, chosen apex y, signed top/back and side surface-speed ratios.
# x is the receiver's right, assuming a right-handed receiver for FH/BH labels.
# All targets, apexes, ratios and pacing are new design choices, not game data.
CANDIDATES = [
    ("gentle_fh_short", "Gentle FH, shorter", +0.34, 0.62, 1.34, 0.00, 0.00),
    ("gentle_bh_short", "Gentle BH, shorter", -0.34, 0.62, 1.34, 0.00, 0.00),
    ("gentle_fh_deep", "Gentle FH, deeper", +0.50, 1.08, 1.34, 0.00, 0.00),
    ("gentle_bh_deep", "Gentle BH, deeper", -0.50, 1.08, 1.34, 0.00, 0.00),
    ("top_fh", "Topspin hypothesis, FH", +0.38, 0.88, 1.24, +0.18, 0.00),
    ("top_bh", "Topspin hypothesis, BH", -0.38, 0.88, 1.24, +0.18, 0.00),
    ("back_fh", "Backspin hypothesis, FH", +0.38, 0.88, 1.38, -0.14, 0.00),
    ("back_bh", "Backspin hypothesis, BH", -0.38, 0.88, 1.38, -0.14, 0.00),
    ("side_positive_fh", "Positive side hypothesis, FH", +0.40, 0.85, 1.32, 0.00, +0.12),
    ("side_negative_fh", "Negative side hypothesis, FH", +0.40, 0.85, 1.32, 0.00, -0.12),
    ("side_positive_bh", "Positive side hypothesis, BH", -0.40, 0.85, 1.32, 0.00, +0.12),
    ("side_negative_bh", "Negative side hypothesis, BH", -0.40, 0.85, 1.32, 0.00, -0.12),
]


def numeric(value):
    if not math.isfinite(value):
        raise ValueError("Non-finite serialized number")
    return f"{value:.8f}".rstrip("0").rstrip(".") or "0"


def raw_spread(values):
    return {"raw": {k: numeric(v) for k, v in values.items()},
            "spread": {k: "0" for k in values}}


def mapped_angle(value, mapping):
    return mapping["native_offset"] + mapping["sign"] * mapping["native_units_per_radian"] * value


def position_at(velocity, time):
    return [LAUNCH[0] + velocity[0] * time,
            LAUNCH[1] + velocity[1] * time - 0.5 * G * time * time,
            LAUNCH[2] + velocity[2] * time]


def solve_matrix(matrix, vector):
    augmented = [[float(v) for v in row] + [float(vector[i])] for i, row in enumerate(matrix)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(augmented[i][col]))
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        if abs(divisor) < 1e-12:
            raise ValueError("Position basis must be invertible")
        augmented[col] = [v / divisor for v in augmented[col]]
        for i in range(3):
            if i != col:
                factor = augmented[i][col]
                augmented[i] = [a - factor * b for a, b in zip(augmented[i], augmented[col])]
    return [row[3] for row in augmented]


def audit_serialized(row, calibration, target):
    """Invert the declared native transforms after eight-decimal serialization."""
    pm = calibration["position"]
    position_vector = [(float(row["position"]["raw"][key]) - pm["native_origin"][i]) /
                       pm["native_units_per_metre"] for i, key in enumerate(("x", "y", "z"))]
    launch = solve_matrix(pm["basis_rows"], position_vector)
    angles = []
    for native_key, canonical_key in (("horizontalAngle", "horizontal"), ("verticalAngle", "vertical")):
        m = calibration["direction"][canonical_key]
        angles.append((float(row["direction"]["raw"][native_key]) - m["native_offset"]) /
                      (m["sign"] * m["native_units_per_radian"]))
    sm = calibration["speed"]
    speed = (float(row["speedAndRate"]["raw"]["speed"]) - sm["native_offset"]) / sm["native_units_per_metre_per_second"]
    horizontal, vertical = angles
    velocity = [speed * math.cos(vertical) * math.sin(horizontal), speed * math.sin(vertical),
                speed * math.cos(vertical) * math.cos(horizontal)]
    flight = (velocity[1] + math.sqrt(velocity[1] ** 2 + 2 * G * (launch[1] - LANDING_HEIGHT))) / G

    def at(t):
        return [launch[0] + velocity[0] * t, launch[1] + velocity[1] * t - G * t * t / 2,
                launch[2] + velocity[2] * t]

    landing = at(flight)
    net_time = -launch[2] / velocity[2]
    net_window = [net_time - BALL_RADIUS / velocity[2], net_time + BALL_RADIUS / velocity[2]]
    clearance = min(at(t)[1] for t in net_window) - BALL_RADIUS - TABLE_TOP - NET_ABOVE_TABLE
    error = math.sqrt(sum((a - b) ** 2 for a, b in zip(landing, target)))
    assert 0 < net_time < flight and clearance > 0
    assert abs(landing[0]) + BALL_RADIUS < TABLE_WIDTH / 2
    assert BALL_RADIUS < landing[2] < TABLE_LENGTH / 2 - BALL_RADIUS
    assert error < 0.001, "Serialized mapping loses more than 1 mm of ideal-model target precision"
    return {"launch_xyz_m": launch, "velocity_xyz_m_per_s": velocity,
            "landing_center_xyz_m": landing, "time_of_flight_s": flight,
            "net_crossing_time_s": net_time, "net_crossing_center_height_m": at(net_time)[1],
            "net_conservative_sphere_sweep_clearance_m": clearance,
            "landing_error_from_intended_m": error, "checked_from": "Serialized native numeric strings, inverse declared calibration"}


def build(calibration):
    rows, diagnostics = {}, []
    for slug, name, target_x, target_z, apex_y, top_ratio, side_ratio in CANDIDATES:
        vy = math.sqrt(2 * G * (apex_y - LAUNCH[1]))
        flight = (vy + math.sqrt(vy * vy + 2 * G * (LAUNCH[1] - LANDING_HEIGHT))) / G
        velocity = ((target_x - LAUNCH[0]) / flight, vy, (target_z - LAUNCH[2]) / flight)
        speed = math.sqrt(sum(v * v for v in velocity))
        horizontal = math.atan2(velocity[0], velocity[2])
        vertical = math.atan2(vy, math.hypot(velocity[0], velocity[2]))
        spin_si = {"topBottom": top_ratio * speed / BALL_RADIUS,
                   "leftRight": side_ratio * speed / BALL_RADIUS, "screw": 0.0}
        net_time = -LAUNCH[2] / velocity[2]
        net_position = position_at(velocity, net_time)
        net_top = TABLE_TOP + NET_ABOVE_TABLE
        net_clearance = net_position[1] - BALL_RADIUS - net_top
        # A conservative bound across the interval when the sphere touches the
        # net's z-plane: minimum center height minus its full radius.
        net_window = [net_time - BALL_RADIUS / velocity[2], net_time + BALL_RADIUS / velocity[2]]
        net_sweep_clearance = min(position_at(velocity, t)[1] for t in net_window) - BALL_RADIUS - net_top
        landing = position_at(velocity, flight)
        margins = {"side": TABLE_WIDTH / 2 - abs(target_x) - BALL_RADIUS,
                   "end": TABLE_LENGTH / 2 - target_z - BALL_RADIUS,
                   "net_side": target_z - BALL_RADIUS}
        assert 0 < net_time < flight
        assert net_sweep_clearance > 0
        assert all(v > 0 for v in margins.values())
        assert math.isclose(landing[0], target_x, abs_tol=1e-10)
        assert math.isclose(landing[1], LANDING_HEIGHT, abs_tol=1e-10)
        assert math.isclose(landing[2], target_z, abs_tol=1e-10)
        assert velocity[1] - G * flight < 0

        pm = calibration["position"]
        native_position = [pm["native_origin"][i] + pm["native_units_per_metre"] *
                           sum(pm["basis_rows"][i][j] * LAUNCH[j] for j in range(3)) for i in range(3)]
        sm = calibration["speed"]
        native_spin = {}
        for key, value in spin_si.items():
            m = calibration["spin"][key]
            native_spin[key] = m["native_offset"] + m["sign"] * m["native_units_per_radian_per_second"] * value
        timing = {}
        for key, value in {"secondsPerLaunch": 2.4, "PostDelay": 0.0}.items():
            m = calibration["timing"][key]
            timing[key] = m["native_offset"] + m["native_units_per_second"] * value
        row_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "independent-eleven-experiment/" + slug))
        rows[row_id] = {
            "DataName": "EXPERIMENT - " + name,
            "Description": "UNCALIBRATED independent SI ballistic hypothesis. Target center x=" + numeric(target_x) +
                           "m, z=" + numeric(target_z) + "m. Native units/signs unconfirmed; spin effects not simulated. " +
                           "Single receiver-side machine feed, not a legal two-bounce serve.",
            "isActive": "True", "CanUpdate": "True",
            "position": raw_spread(dict(zip(("x", "y", "z"), native_position))),
            "direction": raw_spread({
                "horizontalAngle": mapped_angle(horizontal, calibration["direction"]["horizontal"]),
                "verticalAngle": mapped_angle(vertical, calibration["direction"]["vertical"])}),
            "spin": raw_spread(native_spin),
            "speedAndRate": raw_spread({"speed": sm["native_offset"] + sm["native_units_per_metre_per_second"] * speed, **timing})
        }
        diagnostics.append({
            "id": row_id, "slug": slug, "name": name,
            "canonical_launch_xyz_m": list(LAUNCH), "initial_velocity_xyz_m_per_s": list(velocity),
            "intended_landing_center_xyz_m": [target_x, LANDING_HEIGHT, target_z],
            "computed_landing_center_xyz_m": landing, "time_of_flight_s": flight,
            "net_crossing_time_s": net_time, "net_crossing_center_xyz_m": net_position,
            "net_crossing_center_height_m": net_position[1],
            "net_ball_bottom_clearance_m": net_clearance,
            "net_conservative_sphere_sweep_clearance_m": net_sweep_clearance,
            "landing_edge_margins_m": margins, "apex_height_m": apex_y,
            "speed_m_per_s": speed,
            "canonical_angles_radians": {"horizontal": horizontal, "vertical": vertical},
            "spin_surface_speed_ratios": {"topBottom": top_ratio, "leftRight": side_ratio, "screw": 0},
            "hypothesized_spin_rad_per_s": spin_si,
            "spin_class": "neutral" if top_ratio == side_ratio == 0 else "spinning_hypothesis",
            "serialized_roundtrip": audit_serialized(rows[row_id], calibration, [target_x, LANDING_HEIGHT, target_z]),
            "trajectory_validity": "Ideal gravity-only reference; drag, Magnus force and game physics are absent."
        })
    pack = {"settingsVersion": "1", "showBallMachineLauncherAlways": "True", "ballCount": "2",
            "timeScale": "1", "shuffle": "False", "shots": {
                "LastModified": "1/1/0001 12:00:00 AM", "Dirty": "False", "Deleted": "False", "data": rows}}
    details = {
        "status": "UNCONFIRMED GAME MAPPING; ANALYTIC MODEL CHECKED ONLY",
        "provenance": "Derived from declared geometry, gravity, new target/apex/spin-ratio choices and supplied schema. No preset source was read.",
        "canonical_coordinates": {
            "units": "metres and seconds", "origin": "floor directly below table-center/net-center",
            "x": "receiver's right", "y": "up", "z": "toward receiver",
            "horizontal_angle": "atan2(vx, vz); zero along +z; positive toward +x",
            "vertical_angle": "atan2(vy, sqrt(vx^2+vz^2)); positive upward",
            "receiver_handedness_for_fh_bh_labels": "right-handed; swap labels for a left-handed receiver"
        },
        "model": {"gravity_m_per_s2": G, "table_length_m": TABLE_LENGTH, "table_width_m": TABLE_WIDTH,
                  "table_top_height_m": TABLE_TOP, "net_height_above_table_m": NET_ABOVE_TABLE,
                  "ball_radius_m": BALL_RADIUS, "net_top_height_m": TABLE_TOP + NET_ABOVE_TABLE,
                  "table_first_contact_ball_center_height_m": LANDING_HEIGHT,
                  "drag": "omitted", "Magnus": "omitted", "post_bounce_physics": "not modeled"},
        "calibration_used": calibration, "candidates": diagnostics
    }
    return pack, details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", type=Path, default=ROOT / "calibration.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
    pack, details = build(calibration)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in (("experimental-presets.json", pack), ("diagnostics.json", details)):
        (args.output_dir / filename).write_text(json.dumps(content, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entries = []
    def register(code, name, data):
        variants = {}
        for pace, interval in [('slow', 3.0), ('normal', 2.4), ('fast', 1.8)]:
            variant = deepcopy(data)
            for row in variant['shots']['data'].values():
                row['speedAndRate']['raw']['secondsPerLaunch'] = numeric(interval)
                row['speedAndRate']['spread']['secondsPerLaunch'] = '0'
            payload = encode(variant)
            filename = f'{code}.json' if pace == 'slow' else f'{code}-{pace}.json'
            (args.output_dir / filename).write_bytes(payload)
            variants[pace] = {'file': filename, 'sha256': hashlib.sha256(payload).hexdigest(),
                              'interval_seconds': interval, **summary(variant)}
        entries.append({'id': code, 'name': name, 'variants': variants})
    for index, (key, row) in enumerate(pack['shots']['data'].items(), 1):
        code = f'I{index:02}'
        single = deepcopy(pack)
        single['shots']['data'] = {key: deepcopy(row)}
        single['shots']['data'][key]['DataName'] = code + ' ' + row['DataName']
        single['shots']['data'][key]['speedAndRate']['raw']['secondsPerLaunch'] = '3'
        register(code, row['DataName'].removeprefix('EXPERIMENT - '), single)
    for code, name, selections in (
            ('N01', 'Neutral feeds: four placements, 10/2 cycle', list(pack['shots']['data'])[:4]),
            ('R01', 'All twelve experimental feeds, 10/2 cycle', list(pack['shots']['data']))):
        cycle = build_cycle(pack, selections, phases=[10, 2], interval=3)
        register(code, name, cycle)
    (args.output_dir / 'catalog.json').write_text(json.dumps({
        'status': 'experimental_uncalibrated',
        'note': 'Independent ballistic derivation; native mapping and spin effects need in-game testing.',
        'entries': entries}, indent=2) + '\n', encoding='utf-8')
    lines = ["# Independent model results", "", "All clearances and landings below apply only to the declared gravity-only model.", "",
             "| Candidate | Target x/z (m) | Speed (m/s) | H/V (degrees) | Flight (s) | Net sweep clearance (m) |",
             "|---|---:|---:|---:|---:|---:|"]
    for d in details["candidates"]:
        p, a = d["intended_landing_center_xyz_m"], d["canonical_angles_radians"]
        lines.append(f'| {d["name"]} | {p[0]:.2f} / {p[2]:.2f} | {d["speed_m_per_s"]:.3f} | '
                     f'{math.degrees(a["horizontal"]):.3f} / {math.degrees(a["vertical"]):.3f} | '
                     f'{d["time_of_flight_s"]:.3f} | {d["net_conservative_sphere_sweep_clearance_m"]:.3f} |')
    (args.output_dir / "model-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(details['candidates'])} candidates; all ideal-model net/landing checks passed.")
    print("Minimum conservative net clearance (m):", min(d["net_conservative_sphere_sweep_clearance_m"] for d in details["candidates"]))
    print("Maximum serialized-rounding target error (m):", max(d["serialized_roundtrip"]["landing_error_from_intended_m"] for d in details["candidates"]))
    print("UNCONFIRMED native mapping: calibration and measured flight checks are still required.")


if __name__ == "__main__":
    main()
