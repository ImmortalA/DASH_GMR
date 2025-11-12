#!/usr/bin/env python3
"""
Compare two robot IK configuration files and highlight differences.

By default this script compares the active DASH configuration with the
optimized reference configuration. You can override the inputs to compare
any two JSON files that follow the IK config schema.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_A = REPO_ROOT / "general_motion_retargeting" / "ik_configs" / "smplx_to_dash.json"
DEFAULT_CONFIG_B = REPO_ROOT / "configs" / "dash" / "smplx_to_dash_optimized.json"


@dataclass
class ConfigSummary:
    path: Path
    data: Dict


def resolve_config_path(path_str: str) -> Path:
    """
    Resolve a configuration path.

    The lookup order is:
    1. Exact path (absolute or relative to the current working directory)
    2. Path relative to the repository root
    """
    candidate = Path(path_str)
    if candidate.exists():
        return candidate.resolve()

    repo_candidate = (REPO_ROOT / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate

    raise FileNotFoundError(f"Configuration file not found: {path_str}")


def load_config(path: Path) -> ConfigSummary:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return ConfigSummary(path=path, data=data)


def sorted_keys(*dicts: Dict) -> List[str]:
    keys = set()
    for dictionary in dicts:
        keys.update(dictionary.keys())
    return sorted(keys)


def format_optional(value: Optional[float]) -> str:
    return f"{value:6.2f}" if value is not None else "   -- "


def format_vector(vector: Optional[Iterable[float]]) -> str:
    if not vector:
        return "[--]"
    return "[" + ", ".join(f"{v:+.2f}" for v in vector) + "]"


def compare_scale_tables(config_a: ConfigSummary, config_b: ConfigSummary) -> None:
    table_a = config_a.data.get("human_scale_table", {})
    table_b = config_b.data.get("human_scale_table", {})

    print("\nHuman Scale Table")
    print("-" * 72)
    print(f"{'Body Part':<18}{'Config A':>10}{'Config B':>10}{'Δ (B - A)':>12}")
    print("-" * 72)

    for key in sorted_keys(table_a, table_b):
        val_a = table_a.get(key)
        val_b = table_b.get(key)
        diff = (val_b - val_a) if (val_a is not None and val_b is not None) else None
        print(f"{key:<18}{format_optional(val_a)}{format_optional(val_b)}{format_optional(diff)}")


def unpack_ik_entry(entry: List) -> Tuple[Optional[str], Optional[float], Optional[float], List[float], List[float]]:
    if not entry:
        return None, None, None, [], []
    human_body = entry[0] if len(entry) > 0 else None
    pos_weight = entry[1] if len(entry) > 1 else None
    rot_weight = entry[2] if len(entry) > 2 else None
    pos_offset = entry[3] if len(entry) > 3 else []
    rot_offset = entry[4] if len(entry) > 4 else []
    return human_body, pos_weight, rot_weight, pos_offset, rot_offset


def compare_ik_table(table_name: str, config_a: ConfigSummary, config_b: ConfigSummary) -> None:
    table_a = config_a.data.get(table_name, {})
    table_b = config_b.data.get(table_name, {})

    print(f"\n{table_name} differences")
    print("-" * 110)
    header = (
        f"{'Robot Part':<18}"
        f"{'Human (A)':<14}{'Human (B)':<14}"
        f"{'Pos A':>7}{'Pos B':>7}{'ΔP':>7}"
        f"{'Rot A':>7}{'Rot B':>7}{'ΔR':>7}"
        f"{'Quat A':>18}{'Quat B':>18}"
    )
    print(header)
    print("-" * 110)

    for robot_part in sorted_keys(table_a, table_b):
        entry_a = table_a.get(robot_part, [])
        entry_b = table_b.get(robot_part, [])
        human_a, pos_a, rot_a, pos_offset_a, quat_a = unpack_ik_entry(entry_a)
        human_b, pos_b, rot_b, pos_offset_b, quat_b = unpack_ik_entry(entry_b)

        pos_diff = (pos_b - pos_a) if (pos_a is not None and pos_b is not None) else None
        rot_diff = (rot_b - rot_a) if (rot_a is not None and rot_b is not None) else None

        print(
            f"{robot_part:<18}"
            f"{(human_a or '--'):<14}{(human_b or '--'):<14}"
            f"{format_optional(pos_a)}{format_optional(pos_b)}{format_optional(pos_diff)}"
            f"{format_optional(rot_a)}{format_optional(rot_b)}{format_optional(rot_diff)}"
            f"{format_vector(quat_a):>18}{format_vector(quat_b):>18}"
        )


def summarize(config_a: ConfigSummary, config_b: ConfigSummary) -> None:
    print("=" * 110)
    print("IK Configuration Comparison")
    print("=" * 110)
    print(f"Config A: {config_a.path}")
    print(f"Config B: {config_b.path}")
    print("-" * 110)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two IK configuration JSON files."
    )
    parser.add_argument(
        "config_a",
        nargs="?",
        default=str(DEFAULT_CONFIG_A),
        help="Path to the baseline configuration (default: active DASH config).",
    )
    parser.add_argument(
        "config_b",
        nargs="?",
        default=str(DEFAULT_CONFIG_B),
        help="Path to the configuration to compare against (default: optimized DASH config).",
    )
    parser.add_argument(
        "--include-table2",
        action="store_true",
        help="Also compare ik_match_table2 (default: only table1).",
    )

    args = parser.parse_args()

    config_a = load_config(resolve_config_path(args.config_a))
    config_b = load_config(resolve_config_path(args.config_b))

    summarize(config_a, config_b)
    compare_scale_tables(config_a, config_b)
    compare_ik_table("ik_match_table1", config_a, config_b)

    if args.include_table2:
        compare_ik_table("ik_match_table2", config_a, config_b)

    print("\nComparison complete.")


if __name__ == "__main__":
    main()
