#!/bin/bash

# DASH Robot Motion Comparison Script
# This script compares original human motion (NPZ) with retargeted robot motion (PKL)

echo "DASH Robot Motion Comparison Script"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/smplx_to_robot.py" ]; then
    echo "Error: Please run this script from the GMR root directory"
    echo "   Expected: /home/anh/daros/GMR"
    echo "   Current: $(pwd)"
    exit 1
fi

# Activate conda environment
echo "Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate daros_dash

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate daros_dash environment"
    echo "   Please make sure the environment exists: conda env list"
    exit 1
fi

echo "Environment activated: daros_dash"
echo ""

# Check if motion data exists
echo "Checking motion data..."
if [ ! -d "motion_data/ACCAD/Male1General_c3d" ]; then
    echo "Error: Motion data not found"
    echo "   Expected: motion_data/ACCAD/Male1General_c3d/"
    echo "   Please extract the ACCAD dataset first"
    exit 1
fi

echo "Motion data found"
echo ""

# Check if SMPL-X models exist
echo "Checking SMPL-X models..."
if [ ! -f "assets/body_models/models_smplx_v1_1/models/smplx/SMPLX_NEUTRAL.npz" ] && [ ! -f "assets/body_models/models_smplx_v1_1/models/smplx/SMPLX_NEUTRAL.pkl" ]; then
    echo "Warning: SMPL-X models not found"
    echo "   Expected: assets/body_models/models_smplx_v1_1/models/smplx/SMPLX_NEUTRAL.npz (or .pkl)"
    echo "   The comparison will continue but may fail if models are not installed"
    echo "   To install SMPL-X models:"
    echo "   1. Download from https://smpl-x.is.tue.mpg.de/"
    echo "   2. Extract to assets/body_models/models_smplx_v1_1/models/smplx/"
    echo "   3. Place files: SMPLX_NEUTRAL.npz, SMPLX_FEMALE.npz, SMPLX_MALE.npz"
else
    echo "SMPL-X models found"
fi
echo ""

# Set default motion file and robot motion file
NPZ_FILE="motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz"
PKL_FILE="test_stand.pkl"

# Check if robot motion file exists, if not generate it
if [ ! -f "$PKL_FILE" ]; then
    echo "Robot motion file not found: $PKL_FILE"
    echo "Generating robot motion from NPZ file..."
    python scripts/smplx_to_robot.py --robot dash --smplx_file "$NPZ_FILE" --save_path "$PKL_FILE"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to generate robot motion file"
        exit 1
    fi
    
    echo "Robot motion file generated: $PKL_FILE"
    echo ""
fi

# Start comparison visualization
echo "Starting motion comparison..."
echo "-----------------------------------"
echo "Visualization Controls:"
echo "  - Human motion (NPZ): Shown as colored coordinate frames"
echo "  - Robot motion (PKL): Shown as full robot model"
echo "  - Press Ctrl+C to exit"
echo ""

python scripts/dash/visualize_npz_and_robot.py \
    --npz_file "$NPZ_FILE" \
    --pkl_file "$PKL_FILE" \
    --robot dash \
    --human_offset 0.0 1.0 0.0 \
    --loop

if [ $? -eq 0 ]; then
    echo ""
    echo "Comparison completed successfully"
else
    echo ""
    echo "Comparison failed"
    exit 1
fi

echo ""
echo "Comparison Summary"
echo "=================="
echo "Original human motion: $NPZ_FILE"
echo "Robot motion: $PKL_FILE"
echo ""
echo "To compare different motions:"
echo "  1. Generate robot motion: python scripts/smplx_to_robot.py --robot dash --smplx_file <npz_file> --save_path <pkl_file>"
echo "  2. Run comparison: python scripts/dash/visualize_npz_and_robot.py --npz_file <npz_file> --pkl_file <pkl_file> --robot dash --loop"

