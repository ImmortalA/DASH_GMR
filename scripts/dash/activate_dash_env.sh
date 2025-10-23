#!/bin/bash
# DASH Robot Environment Activation Script
# This script activates the daros_dash conda environment and sets up the GMR environment

echo "🤖 Activating DASH Robot Environment..."
echo ""

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate daros_dash

# Check if activation was successful
if [[ "$CONDA_DEFAULT_ENV" == "daros_dash" ]]; then
    echo "✓ Conda environment 'daros_dash' activated successfully"
    echo "✓ Python version: $(python --version)"
    echo "✓ Environment ready for DASH robot motion retargeting!"
    echo ""
    echo "Available commands:"
    echo "  python scripts/smplx_to_robot.py --robot dash --smplx_file <motion_file>"
    echo "  python scripts/bvh_to_robot.py --robot dash --bvh_file <motion_file>"
    echo "  python scripts/vis_robot_motion.py --robot dash --robot_motion_path <motion_file>"
    echo ""
    echo "To deactivate: conda deactivate"
else
    echo "✗ Failed to activate conda environment"
    exit 1
fi

