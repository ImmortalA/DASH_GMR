# GMR Scripts Usage Guide

This guide explains how to use all the scripts in the `scripts/` directory. All scripts now default to the **DASH robot** unless otherwise specified.

---

## Quick Start

### Basic Motion Retargeting (SMPL-X to Robot)

The most common script for retargeting human motion to robot:

```bash
# Basic usage (uses DASH by default)
python scripts/smplx_to_robot.py --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz

# Save the retargeted motion to a file
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --save_path test_results/dash/standing_motion.pkl

# Loop the motion for continuous playback
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --loop

# Record a video of the motion
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --record_video

# Use a different robot (override default)
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --robot unitree_g1
```

---

## Script Descriptions

### 1. `smplx_to_robot.py` - SMPL-X Motion Retargeting

**Purpose**: Retarget SMPL-X human motion data (NPZ files) to robot motion.

**Common Use Cases**:
- Visualize human motion on DASH robot
- Generate robot motion files for testing
- Real-time motion retargeting

**Arguments**:
- `--smplx_file`: Path to SMPL-X NPZ motion file (required, has default)
- `--robot`: Robot type (default: "dash")
- `--save_path`: Save retargeted motion to PKL file
- `--loop`: Loop the motion continuously
- `--record_video`: Record visualization to MP4
- `--rate_limit`: Match human motion playback rate

**Examples**:
```bash
# Simple visualization
python scripts/smplx_to_robot.py --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz

# Save motion for later use
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --save_path test_results/dash/standing.pkl

# Record video
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --record_video \
    --save_path test_results/dash/standing.pkl
```

---

### 2. `bvh_to_robot.py` - BVH Motion Retargeting

**Purpose**: Retarget BVH motion files (LAFAN1, Nokov formats) to robot motion.

**Arguments**:
- `--bvh_file`: Path to BVH file (required)
- `--format`: Format type - "lafan1" or "nokov" (default: "lafan1")
- `--robot`: Robot type (default: "dash")
- `--save_path`: Save retargeted motion
- `--loop`: Loop the motion
- `--record_video`: Record video
- `--motion_fps`: Motion frame rate (default: 30)

**Examples**:
```bash
# LAFAN1 format
python scripts/bvh_to_robot.py \
    --bvh_file motion_data/LAFAN1/subject1/walk1_subject1.bvh \
    --format lafan1 \
    --save_path test_results/dash/walking.pkl

# Nokov format
python scripts/bvh_to_robot.py \
    --bvh_file motion_data/nokov/motion.bvh \
    --format nokov \
    --save_path test_results/dash/motion.pkl
```

---

### 3. `gvhmr_to_robot.py` - GVHMR Motion Retargeting

**Purpose**: Retarget GVHMR prediction files to robot motion.

**Arguments**:
- `--gvhmr_pred_file`: Path to GVHMR prediction file (default: "GVHMR/outputs/demo/tennis/hmr4d_results.pt")
- `--robot`: Robot type (default: "dash")
- `--save_path`: Save retargeted motion
- `--loop`: Loop the motion
- `--record_video`: Record video

**Examples**:
```bash
python scripts/gvhmr_to_robot.py \
    --gvhmr_pred_file GVHMR/outputs/demo/tennis/hmr4d_results.pt \
    --save_path test_results/dash/gvhmr_motion.pkl
```

---

### 4. `fbx_offline_to_robot.py` - FBX/OptiTrack Motion Retargeting

**Purpose**: Retarget offline FBX motion files (from OptiTrack) to robot motion.

**Arguments**:
- `--motion_file`: Path to FBX motion file (required)
- `--robot`: Robot type (default: "dash")
- `--save_path`: Save retargeted motion
- `--record_video`: Record video

**Examples**:
```bash
python scripts/fbx_offline_to_robot.py \
    --motion_file motion_data/optitrack/motion.pkl \
    --save_path test_results/dash/optitrack_motion.pkl
```

---

### 5. `optitrack_to_robot.py` - Real-time OptiTrack Retargeting

**Purpose**: Real-time motion retargeting from OptiTrack motion capture system.

**Arguments**:
- `--server_ip`: OptiTrack server IP (default: "192.168.200.160")
- `--client_ip`: Client IP address (default: "192.168.200.117")
- `--use_multicast`: Use multicast (default: False)
- `--robot`: Robot type (default: "dash")

**Examples**:
```bash
# Connect to OptiTrack system
python scripts/optitrack_to_robot.py \
    --server_ip 192.168.200.160 \
    --client_ip 192.168.200.117 \
    --robot dash
```

**Note**: Make sure firewall is disabled on both machines before running.

---

### 6. `vis_robot_motion.py` - Visualize Saved Robot Motion

**Purpose**: Visualize previously saved robot motion files (PKL format).

**Arguments**:
- `--robot_motion_path`: Path to PKL motion file (required)
- `--robot`: Robot type (default: "dash")
- `--record_video`: Record video
- `--video_path`: Output video path

**Examples**:
```bash
# Visualize saved motion
python scripts/vis_robot_motion.py \
    --robot_motion_path test_results/dash/standing.pkl

# Record video of saved motion
python scripts/vis_robot_motion.py \
    --robot_motion_path test_results/dash/standing.pkl \
    --record_video \
    --video_path videos/dash_standing.mp4
```

---

### 7. `smplx_to_robot_dataset.py` - Batch Process SMPL-X Dataset

**Purpose**: Process entire directories of SMPL-X motion files in batch.

**Arguments**:
- `--src_folder`: Source folder with NPZ files (required)
- `--tgt_folder`: Target folder for output PKL files (required)
- `--robot`: Robot type (default: "dash")
- `--override`: Overwrite existing files
- `--num_cpus`: Number of CPU cores to use (default: 4)

**Examples**:
```bash
# Process entire dataset
python scripts/smplx_to_robot_dataset.py \
    --src_folder motion_data/ACCAD/Male1General_c3d \
    --tgt_folder test_results/dash/ACCAD_dataset \
    --robot dash \
    --num_cpus 8

# Overwrite existing files
python scripts/smplx_to_robot_dataset.py \
    --src_folder motion_data/ACCAD \
    --tgt_folder test_results/dash/ACCAD_full \
    --override
```

---

### 8. `bvh_to_robot_dataset.py` - Batch Process BVH Dataset

**Purpose**: Process entire directories of BVH motion files in batch.

**Arguments**:
- `--src_folder`: Source folder with BVH files (required)
- `--tgt_folder`: Target folder for output PKL files (default: "../../motion_data/LAFAN1_g1_gmr")
- `--robot`: Robot type (default: "dash")
- `--override`: Overwrite existing files

**Examples**:
```bash
python scripts/bvh_to_robot_dataset.py \
    --src_folder motion_data/LAFAN1 \
    --tgt_folder test_results/dash/LAFAN1_dataset \
    --robot dash
```

---

## DASH-Specific Scripts

### DASH Test Script

```bash
# Run comprehensive DASH robot tests
./scripts/dash/test_dash_robot.sh
```

### DASH Motion Comparison

```bash
# Compare human motion (NPZ) with robot motion (PKL)
./scripts/dash/compare_motion.sh
```

### DASH Configuration Tools

```bash
# Compare different IK configurations
python scripts/dash/compare_configs.py

# Extract configuration from URDF
python scripts/dash/extract_urdf_config.py

# Optimize configuration based on motion analysis
python scripts/dash/optimize_dash_mapping.py
```

---

## Common Workflows

### Workflow 1: Test a Single Motion File

```bash
# 1. Retarget and visualize
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz

# 2. Save for later use
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --save_path test_results/dash/standing.pkl

# 3. Visualize saved motion
python scripts/vis_robot_motion.py \
    --robot_motion_path test_results/dash/standing.pkl
```

### Workflow 2: Process Multiple Motions

```bash
# Process entire folder
python scripts/smplx_to_robot_dataset.py \
    --src_folder motion_data/ACCAD/Male1General_c3d \
    --tgt_folder test_results/dash/ACCAD_processed \
    --robot dash
```

### Workflow 3: Compare Human vs Robot Motion

```bash
# 1. Generate robot motion
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --save_path test_results/dash/standing.pkl

# 2. Compare side-by-side
./scripts/dash/compare_motion.sh
```

### Workflow 4: Record Videos

```bash
# Record video of retargeted motion
python scripts/smplx_to_robot.py \
    --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz \
    --record_video \
    --save_path test_results/dash/standing.pkl

# Video will be saved to: videos/dash_General_A1_-_Stand_stageii.mp4
```

---

## File Paths

### Default Motion Data Locations

- **SMPL-X**: `motion_data/ACCAD/`
- **BVH (LAFAN1)**: `motion_data/LAFAN1/`
- **GVHMR**: `GVHMR/outputs/`
- **OptiTrack**: `motion_data/optitrack/`

### Default Output Locations

- **Saved motions**: `test_results/dash/`
- **Videos**: `videos/`
- **Configurations**: `configs/dash/`

---

## Tips and Troubleshooting

### 1. Check Motion File Exists

```bash
# Verify file exists before running
ls -lh motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz
```

### 2. Check SMPL-X Models

```bash
# Verify SMPL-X models are installed
ls -lh assets/body_models/models_smplx_v1_1/models/smplx/SMPLX_NEUTRAL.npz
```

### 3. Environment Setup

```bash
# Activate conda environment (if using)
conda activate daros_dash

# Or use the activation script
./scripts/dash/activate_dash_env.sh
```

### 4. Common Errors

**Error**: `FileNotFoundError: Motion file not found`
- **Solution**: Check the file path is correct relative to the repository root

**Error**: `SMPL-X models not found`
- **Solution**: Download SMPL-X models and place in `assets/body_models/models_smplx_v1_1/models/smplx/`

**Error**: `ModuleNotFoundError`
- **Solution**: Activate the correct conda environment or install dependencies

### 5. Performance Tips

- Use `--save_path` to save motions for faster re-visualization
- Use `--num_cpus` for batch processing to speed up dataset conversion
- Use `--rate_limit` for smoother real-time playback

---

## Getting Help

For more information:
- DASH-specific documentation: `docs/dash/`
- IK configuration guide: `docs/HOW_TO_CREATE_IK_CONFIG.md`
- Main documentation: `DOC.md`

---

**Last Updated**: 2025-01-12  
**Default Robot**: DASH

