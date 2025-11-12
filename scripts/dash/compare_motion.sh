#!/bin/bash

# DASH Robot Motion Comparison Script
# This script compares original human motion (NPZ) with retargeted robot motion (PKL)
# Supports multiple motion types with interactive selection

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

# Define available motions
declare -A MOTIONS
MOTIONS[1]="motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz|test_results/dash/standing.pkl|Standing"
MOTIONS[2]="motion_data/ACCAD/Male1General_c3d/General_A2_-_Sway_stageii.npz|test_results/dash/swaying.pkl|Swaying"
MOTIONS[3]="motion_data/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz|test_results/dash/arm_swing.pkl|Arm Swing"
MOTIONS[4]="motion_data/ACCAD/Male1General_c3d/General_A5_-_Pick_Up_Box_stageii.npz|test_results/dash/pickup.pkl|Pick Up Box"
MOTIONS[5]="motion_data/ACCAD/Male1General_c3d/General_A7_-_Sit_Down_stageii.npz|test_results/dash/sit_down.pkl|Sit Down"
MOTIONS[6]="motion_data/ACCAD/Male1General_c3d/General_A8_-_Stand_Up_stageii.npz|test_results/dash/stand_up.pkl|Stand Up"
MOTIONS[7]="motion_data/ACCAD/Male1Running_c3d/Run_C24_-_quick_side_step_left_stageii.npz|test_results/dash/running.pkl|Running"
MOTIONS[8]="motion_data/ACCAD/Male2MartialArtsKicks_c3d/G8_-__roundhouse_left_stageii.npz|test_results/dash/kick.pkl|Kick"
MOTIONS[9]="motion_data/ACCAD/Male2MartialArtsPunches_c3d/E1_-__Jab_left_stageii.npz|test_results/dash/punch.pkl|Punch"

# Check if motion file argument is provided
if [ -n "$1" ]; then
    SELECTION=$1
else
    # Display menu
    echo "Available Motions:"
    echo "=================="
    for i in {1..9}; do
        IFS='|' read -r npz_file pkl_file description <<< "${MOTIONS[$i]}"
        if [ -f "$npz_file" ]; then
            echo "  $i) $description"
        fi
    done
    echo "  a) All motions (cycle through)"
    echo ""
    read -p "Select motion (1-9, a for all, or press Enter for default): " SELECTION
fi

# Handle selection
if [ -z "$SELECTION" ]; then
    SELECTION=1
fi

# Create output directory
mkdir -p test_results/dash

# Function to process a single motion
process_motion() {
    local motion_key=$1
    IFS='|' read -r NPZ_FILE PKL_FILE DESCRIPTION <<< "${MOTIONS[$motion_key]}"
    
    if [ -z "$NPZ_FILE" ]; then
        echo "Error: Invalid motion selection"
        return 1
    fi
    
    if [ ! -f "$NPZ_FILE" ]; then
        echo "Warning: Motion file not found: $NPZ_FILE"
        echo "Skipping..."
        return 1
    fi
    
    echo ""
    echo "========================================="
    echo "Processing: $DESCRIPTION"
    echo "========================================="
    echo "NPZ File: $NPZ_FILE"
    echo "PKL File: $PKL_FILE"
    echo ""
    
    # Check if robot motion file exists, if not generate it
    if [ ! -f "$PKL_FILE" ]; then
        echo "Generating robot motion from NPZ file..."
        python scripts/smplx_to_robot.py --robot dash --smplx_file "$NPZ_FILE" --save_path "$PKL_FILE" 2>&1 | grep -E "(Error|Warning|Saved|Actual rendering)" || true
        
        if [ $? -ne 0 ] || [ ! -f "$PKL_FILE" ]; then
            echo "Error: Failed to generate robot motion file"
            return 1
        fi
        
        echo "Robot motion file generated: $PKL_FILE"
        echo ""
    else
        echo "Robot motion file already exists: $PKL_FILE"
        echo ""
    fi
    
    # Start comparison visualization
    echo "Starting motion comparison..."
    echo "-----------------------------------"
    echo "Visualization Controls:"
    echo "  - Human motion (NPZ): Shown as colored coordinate frames"
    echo "  - Robot motion (PKL): Shown as full robot model"
    echo "  - Press Ctrl+C to exit and continue to next motion"
    echo ""
    
    python scripts/dash/visualize_npz_and_robot.py \
        --npz_file "$NPZ_FILE" \
        --pkl_file "$PKL_FILE" \
        --robot dash \
        --human_offset 0.0 1.0 0.0 \
        --loop
    
    return $?
}

# Process based on selection
if [ "$SELECTION" = "a" ] || [ "$SELECTION" = "A" ] || [ "$SELECTION" = "all" ]; then
    # Process all motions
    echo "Processing all available motions..."
    echo "Press Ctrl+C to skip to next motion"
    echo ""
    
    for i in {1..9}; do
        IFS='|' read -r npz_file pkl_file description <<< "${MOTIONS[$i]}"
        if [ -f "$npz_file" ]; then
            process_motion $i
            echo ""
            echo "Press Enter to continue to next motion, or Ctrl+C to exit..."
            read
        fi
    done
    
    echo ""
    echo "All motions processed!"
else
    # Process single motion
    if [[ "$SELECTION" =~ ^[1-9]$ ]]; then
        process_motion $SELECTION
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "Comparison completed successfully"
        else
            echo ""
            echo "Comparison failed"
            exit 1
        fi
    else
        echo "Error: Invalid selection. Please choose 1-9 or 'a' for all"
        exit 1
    fi
fi

echo ""
echo "Comparison Summary"
echo "=================="
echo ""
echo "To compare different motions:"
echo "  1. Run this script: ./scripts/dash/compare_motion.sh"
echo "  2. Or specify motion number: ./scripts/dash/compare_motion.sh 1"
echo "  3. Or process all: ./scripts/dash/compare_motion.sh a"
echo ""
echo "To manually compare:"
echo "  python scripts/dash/visualize_npz_and_robot.py --npz_file <npz_file> --pkl_file <pkl_file> --robot dash --loop"

