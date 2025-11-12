#!/usr/bin/env python3
"""
Extract IK configuration hints from a MuJoCo (MJCF) robot description.

This script walks the DASH MJCF model, records link transforms, and produces a
baseline IK configuration JSON file that you can further refine manually.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import xml.etree.ElementTree as ET

import numpy as np
from scipy.spatial.transform import Rotation as R

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URDF = REPO_ROOT / "assets" / "DASH_URDF" / "mjmodel.xml"
DEFAULT_OUTPUT = REPO_ROOT / "configs" / "dash" / "smplx_to_dash_from_urdf.json"


@dataclass
class BodyInfo:
    name: str
    pos: np.ndarray
    quat_xyzw: np.ndarray  # Quaternion in [x, y, z, w]

    @property
    def quat_wxyz(self) -> List[float]:
        return [float(self.quat_xyzw[3])] + self.quat_xyzw[:3].tolist()


def parse_body(
    element: ET.Element,
    parent_pos: np.ndarray,
    parent_quat: np.ndarray,
    bodies: Dict[str, BodyInfo],
) -> None:
    """Recursively parse MuJoCo body elements."""
    name = element.get("name")
    if not name:
        return

    pos = np.fromstring(element.get("pos", "0 0 0"), sep=" ")
    quat_wxyz = np.fromstring(element.get("quat", "1 0 0 0"), sep=" ")

    if quat_wxyz.size != 4:
        quat_wxyz = np.array([1.0, 0.0, 0.0, 0.0])

    local_quat = R.from_quat([quat_wxyz[1], quat_wxyz[2], quat_wxyz[3], quat_wxyz[0]])
    parent_rot = R.from_quat(parent_quat)
    world_quat = parent_rot * local_quat

    world_pos = parent_pos + parent_rot.apply(pos)
    quat_xyzw = world_quat.as_quat()

    bodies[name] = BodyInfo(name=name, pos=world_pos, quat_xyzw=quat_xyzw)

    for child in element.findall("body"):
        parse_body(child, world_pos, quat_xyzw, bodies)


def load_bodies(urdf_path: Path) -> Dict[str, BodyInfo]:
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    worldbody = root.find("worldbody")
    if worldbody is None:
        raise ValueError("The MJCF file does not contain a <worldbody> element.")

    bodies: Dict[str, BodyInfo] = {}
    identity_quat = np.array([0.0, 0.0, 0.0, 1.0], dtype=float)
    for body in worldbody.findall("body"):
        parse_body(body, np.zeros(3), identity_quat, bodies)

    return bodies


def estimate_scale(bodies: Dict[str, BodyInfo]) -> float:
    """Estimate a scale factor from feet to shoulders height."""
    if not bodies:
        return 0.5

    foot_heights = []
    shoulder_heights = []
    for info in bodies.values():
        lname = info.name.lower()
        if "foot" in lname:
            foot_heights.append(info.pos[2])
        if "shoulder" in lname:
            shoulder_heights.append(info.pos[2])

    if foot_heights and shoulder_heights:
        return abs(max(shoulder_heights) - min(foot_heights)) / 1.8  # human height

    # Fallback: use torso height if available
    torso = bodies.get("torso")
    if torso is not None:
        return abs(torso.pos[2]) / 1.8

    return 0.5


def build_config(bodies: Dict[str, BodyInfo], scale_factor: float) -> Dict:
    human_scale_table = {}
    for body in [
        "pelvis",
        "spine1",
        "spine2",
        "spine3",
        "neck",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_foot",
        "right_foot",
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist",
        "right_wrist",
    ]:
        if "shoulder" in body or "elbow" in body or "wrist" in body:
            human_scale_table[body] = round(scale_factor * 0.9, 3)
        elif "neck" in body:
            human_scale_table[body] = round(scale_factor * 0.8, 3)
        else:
            human_scale_table[body] = round(scale_factor, 3)

    ik_pairs = {
        "torso": "pelvis",
        "r_hip": "right_hip",
        "r_upper_leg": "right_knee",
        "r_lower_leg": "right_ankle",
        "r_foot": "right_foot",
        "l_hip": "left_hip",
        "l_upper_leg": "left_knee",
        "l_lower_leg": "left_ankle",
        "l_foot": "left_foot",
        "r_prox_shoulder": "right_shoulder",
        "r_upper_arm": "right_elbow",
        "r_lower_arm": "right_wrist",
        "l_prox_shoulder": "left_shoulder",
        "l_upper_arm": "left_elbow",
        "l_lower_arm": "left_wrist",
    }

    def default_weights(robot_part: str) -> Tuple[int, int]:
        if "foot" in robot_part:
            return 100, 40
        if "torso" == robot_part:
            return 100, 25
        if "lower_leg" in robot_part or "upper_leg" in robot_part or "hip" in robot_part:
            return 0, 20
        if "shoulder" in robot_part:
            return 0, 15
        if "upper_arm" in robot_part or "lower_arm" in robot_part:
            return 0, 15
        return 0, 10

    ik_table = {}
    for robot_part, human_part in ik_pairs.items():
        body_info = bodies.get(robot_part)
        if not body_info:
            continue
        pos_weight, rot_weight = default_weights(robot_part)
        ik_table[robot_part] = [
            human_part,
            pos_weight,
            rot_weight,
            [0.0, 0.0, 0.0],
            body_info.quat_wxyz,
        ]

    config = {
        "robot_root_name": "torso",
        "human_root_name": "pelvis",
        "ground_height": 0.0,
        "human_height_assumption": 1.8,
        "use_ik_match_table1": True,
        "use_ik_match_table2": True,
        "human_scale_table": human_scale_table,
        "ik_match_table1": ik_table,
        "ik_match_table2": ik_table,  # Duplicate for manual tuning later
    }

    return config


def write_config(config: Dict, output_path: Path, pretty: bool = True) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4 if pretty else None)
    print(f"\nConfiguration written to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract a baseline IK configuration from a MuJoCo robot model."
    )
    parser.add_argument(
        "--urdf",
        default=str(DEFAULT_URDF),
        help="Path to the DASH MJCF file (default: assets/DASH_URDF/mjmodel.xml).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Where to save the generated configuration JSON.",
    )
    parser.add_argument(
        "--no-pretty",
        action="store_true",
        help="Disable pretty printing (writes minified JSON).",
    )

    args = parser.parse_args()

    urdf_path = Path(args.urdf)
    if not urdf_path.is_absolute():
        urdf_path = (REPO_ROOT / urdf_path).resolve()
    if not urdf_path.exists():
        raise FileNotFoundError(f"MJCF file not found: {urdf_path}")

    print(f"Loading robot description from: {urdf_path}")
    bodies = load_bodies(urdf_path)
    print(f"Discovered {len(bodies)} bodies.")

    scale = estimate_scale(bodies)
    print(f"Estimated scale factor (robot / human): {scale:.3f}")

    config = build_config(bodies, scale)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (REPO_ROOT / output_path).resolve()

    write_config(config, output_path, pretty=not args.no_pretty)

    print("\nSummary:")
    print(f"  Robot root     : {config['robot_root_name']}")
    print(f"  Human root     : {config['human_root_name']}")
    print(f"  # scale entries: {len(config['human_scale_table'])}")
    print(f"  # IK entries   : {len(config['ik_match_table1'])}")
    missing = sorted(set(config["human_scale_table"]) - {v[0] for v in config["ik_match_table1"].values()})
    if missing:
        print(f"  Warning: human bodies without IK mapping: {', '.join(missing)}")


if __name__ == "__main__":
    main()

