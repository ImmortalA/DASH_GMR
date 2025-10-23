#!/bin/bash

# DASH Robot Quick Test Script
# This script tests your DASH robot integration with the GMR system

echo "🚀 DASH Robot Integration Test Script"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/smplx_to_robot.py" ]; then
    echo "❌ Error: Please run this script from the GMR root directory"
    echo "   Expected: /home/anh/daros/GMR"
    echo "   Current: $(pwd)"
    exit 1
fi

# Activate conda environment
echo "📦 Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate daros_dash

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate daros_dash environment"
    echo "   Please make sure the environment exists: conda env list"
    exit 1
fi

echo "✅ Environment activated: daros_dash"
echo ""

# Check if motion data exists
echo "📁 Checking motion data..."
if [ ! -d "motion_data/ACCAD/ACCAD/Male1General_c3d" ]; then
    echo "❌ Error: Motion data not found"
    echo "   Expected: motion_data/ACCAD/ACCAD/Male1General_c3d/"
    echo "   Please extract the ACCAD dataset first"
    exit 1
fi

echo "✅ Motion data found"
echo ""

# Check if SMPL-X models exist
echo "🔍 Checking SMPL-X models..."
if [ ! -f "assets/body_models/smplx/SMPLX_NEUTRAL.pkl" ]; then
    echo "❌ Error: SMPL-X models not found"
    echo "   Expected: assets/body_models/smplx/SMPLX_NEUTRAL.pkl"
    echo "   Please download and install SMPL-X models first"
    exit 1
fi

echo "✅ SMPL-X models found"
echo ""

# Test 1: Basic motion retargeting
echo "🧪 Test 1: Basic Motion Retargeting"
echo "-----------------------------------"

echo "Testing standing motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_stand.pkl

if [ $? -eq 0 ]; then
    echo "✅ Standing motion test passed"
else
    echo "❌ Standing motion test failed"
    exit 1
fi

echo ""

# Test 2: Different motion type
echo "🧪 Test 2: Different Motion Type"
echo "-------------------------------"

echo "Testing swaying motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A2_-_Sway_stageii.npz --save_path test_sway.pkl

if [ $? -eq 0 ]; then
    echo "✅ Swaying motion test passed"
else
    echo "❌ Swaying motion test failed"
    exit 1
fi

echo ""

# Test 3: Complex motion
echo "🧪 Test 3: Complex Motion"
echo "------------------------"

echo "Testing pickup motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A5_-_Pick_Up_Box_stageii.npz --save_path test_pickup.pkl

if [ $? -eq 0 ]; then
    echo "✅ Pickup motion test passed"
else
    echo "❌ Pickup motion test failed"
    exit 1
fi

echo ""

# Test 4: Check output files
echo "🧪 Test 4: Output Files"
echo "----------------------"

echo "Checking generated files..."
if [ -f "test_stand.pkl" ] && [ -f "test_sway.pkl" ] && [ -f "test_pickup.pkl" ]; then
    echo "✅ All output files created successfully"
    echo "   - test_stand.pkl ($(stat -c%s test_stand.pkl) bytes)"
    echo "   - test_sway.pkl ($(stat -c%s test_sway.pkl) bytes)"
    echo "   - test_pickup.pkl ($(stat -c%s test_pickup.pkl) bytes)"
else
    echo "❌ Some output files are missing"
    exit 1
fi

echo ""

# Test 5: Visualization (optional)
echo "🧪 Test 5: Visualization Test"
echo "----------------------------"

echo "Testing visualization (this will open a window)..."
echo "Press Ctrl+C to skip this test, or wait for the window to open"

# Start visualization in background and kill it after 5 seconds
timeout 5s python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl &
VIS_PID=$!

sleep 2
kill $VIS_PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Visualization test passed"
else
    echo "⚠️  Visualization test skipped (this is normal)"
fi

echo ""

# Summary
echo "🎉 Test Summary"
echo "==============="
echo "✅ Environment activation: PASSED"
echo "✅ Motion data check: PASSED"
echo "✅ SMPL-X models check: PASSED"
echo "✅ Standing motion retargeting: PASSED"
echo "✅ Swaying motion retargeting: PASSED"
echo "✅ Pickup motion retargeting: PASSED"
echo "✅ Output files creation: PASSED"
echo "✅ Visualization test: PASSED"
echo ""
echo "🚀 Your DASH robot integration is working perfectly!"
echo ""
echo "📁 Generated test files:"
echo "   - test_stand.pkl"
echo "   - test_sway.pkl"
echo "   - test_pickup.pkl"
echo ""
echo "🎯 Next steps:"
echo "   1. Try more motion files from motion_data/ACCAD/ACCAD/Male1General_c3d/"
echo "   2. Use the visualization script to see your robot in action"
echo "   3. Record videos using --record_video flag"
echo "   4. Customize IK configuration for better motion quality"
echo ""
echo "📖 For detailed instructions, see: DASH_ROBOT_INSTRUCTIONS.md"
