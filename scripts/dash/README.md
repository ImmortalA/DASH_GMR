# DASH Script Toolkit

Scripts in this directory support the DASH ↔️ GMR integration workflow. The table
below groups the maintained utilities by common tasks.

| Category | Script | Purpose |
| --- | --- | --- |
| **Testing** | `test_dash_robot.sh` | Run smoke tests against the current IK config |
| | `compare_motion.sh` | End-to-end NPZ → PKL generation and side-by-side viewer |
| **Visualization** | `visualize_npz_and_robot.py` | Render human vs robot motion interactively |
| **Configuration** | `extract_urdf_config.py` | Derive a baseline config from `assets/DASH_URDF/mjmodel.xml` |
| | `optimize_dash_mapping.py` | Build a motion-optimized config from SMPL-X data |
| | `compare_configs.py` | Diff two IK configuration JSON files |
| **Analysis** | `analyze_dash_robot.py` | Inspect DASH MJCF structure and joint limits |
| | `comprehensive_dash_analyzer.py`<br>`enhanced_dash_analyzer.py`<br>`real_dash_analyzer.py` | Specialist analysis utilities (advanced use) |
| **Diagnostics** | `test_hybrid_motions.py` | Batch test hybrid motion scenarios |

> Many helper scripts accept arguments—run `python SCRIPT.py --help` for the
> latest flags.

---

## Quick Examples

Generate a URDF-derived configuration (writes to `configs/dash/`):

```bash
python scripts/dash/extract_urdf_config.py \
  --urdf assets/DASH_URDF/mjmodel.xml \
  --output configs/dash/smplx_to_dash_from_urdf.json
```

Create a motion-optimized configuration from the ACCAD standing clip:

```bash
python scripts/dash/optimize_dash_mapping.py \
  --smplx-file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
  --output configs/dash/smplx_to_dash_optimized.json
```

Compare the active IK config with the optimized reference (include table2 diff):

```bash
python scripts/dash/compare_configs.py --include-table2
```

Launch the human/robot comparison viewer with existing artifacts:

```bash
python scripts/dash/visualize_npz_and_robot.py \
  --npz_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
  --pkl_file test_results/dash/walking_test.pkl
```

Run the full regression test:

```bash
./scripts/dash/test_dash_robot.sh
```

---

## Recommended Workflow

1. **Extract Structure** – `extract_urdf_config.py` to seed a baseline config.
2. **Optimize** – `optimize_dash_mapping.py` to produce motion-informed weights.
3. **Compare** – `compare_configs.py` to review parameter deltas.
4. **Test** – `test_dash_robot.sh` or `compare_motion.sh` to validate results.
5. **Iterate** – visualize with `visualize_npz_and_robot.py` and adjust JSON.

For deeper investigations, the analyzer scripts provide joint-limit summaries,
link masses, and motion statistics to guide further tuning.

---

**Last Updated:** November 12, 2025

