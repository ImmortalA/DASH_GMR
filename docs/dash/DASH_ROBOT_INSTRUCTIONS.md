# DASH Robot Integration Instructions

## Overview
This guide provides step-by-step instructions for using your DASH robot with the General Motion Retargeting (GMR) system. Your DASH robot is now fully integrated with **optimized motion-based configuration** and ready for high-quality motion retargeting from human motion data.

## Prerequisites
- Conda environment `daros_dash` is created and configured
- SMPL-X body models are downloaded and installed
- AMASS motion data is available in `motion_data/` directory
- **Optimized IK configuration** based on motion analysis

## Quick Start

### 1. Activate Environment
```bash
# Option 1: Manual activation
conda activate daros_dash
cd /home/anh/daros/GMR

# Option 2: Use convenience script
./scripts/dash/activate_dash_env.sh
```

### 2. Test Optimized Motion Retargeting
```bash
# Test standing motion (optimized configuration)
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_results/dash/dash_stand_optimized.pkl

# Test swaying motion
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A2_-_Sway_stageii.npz --save_path test_results/dash/dash_sway_optimized.pkl

# Test arm movement
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz --save_path test_results/dash/dash_arms_optimized.pkl

# Test pickup motion
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A5_-_Pick_Up_Box_stageii.npz --save_path test_results/dash/dash_pickup_optimized.pkl
```

### 3. Visualize Results
```bash
# Visualize optimized standing motion
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/dash_stand_optimized.pkl

# Visualize optimized swaying motion
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/dash_sway_optimized.pkl

# Visualize optimized arm movement
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/dash_arms_optimized.pkl

# Visualize optimized pickup motion
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/dash_pickup_optimized.pkl
```

## Available Motion Files

### ACCAD Dataset (Currently Available)
```bash
# List all available motions
ls motion_data/ACCAD/Male1General_c3d/

# Some example motions you can test:
# - General_A1_-_Stand_stageii.npz (Standing)
# - General_A2_-_Sway_stageii.npz (Swaying)
# - General_A3_-_Swing_Arms_While_Stand_stageii.npz (Arm swinging)
# - General_A4_-_Look_Around_stageii.npz (Looking around)
# - General_A5_-_Pick_Up_Box_stageii.npz (Pick up box)
# - General_A6_-_Put_Down_Box_stageii.npz (Put down box)
# - General_A7_-_Sit_Down_stageii.npz (Sitting down)
# - General_A8_-_Stand_Up_stageii.npz (Standing up)
# - General_A9_-_Lie_Down_stageii.npz (Lying down)
# - General_A10_-__Lie_Down_to_Crouch_stageii.npz (Lie to crouch)
# - General_A11_-___Military_Crawl_Forward_stageii.npz (Crawling forward)
# - General_A12_-___Military_Crawl_Backwards_stageii.npz (Crawling backward)
```

## Complete Test Suite

### Test 1: Basic Motions
```bash
conda activate daros_dash
cd /home/anh/daros/GMR

echo "=== Test 1: Basic Motions ==="

# Standing motion
echo "Testing standing motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_stand.pkl

# Swaying motion
echo "Testing swaying motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A2_-_Sway_stageii.npz --save_path test_sway.pkl

# Arm swinging motion
echo "Testing arm swinging motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz --save_path test_arms.pkl

echo "Basic motion tests completed!"
```

### Test 2: Complex Motions
```bash
echo "=== Test 2: Complex Motions ==="

# Pick up box motion
echo "Testing pickup motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A5_-_Pick_Up_Box_stageii.npz --save_path test_pickup.pkl

# Sit down motion
echo "Testing sit down motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A7_-_Sit_Down_stageii.npz --save_path test_sit.pkl

# Stand up motion
echo "Testing stand up motion..."
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A8_-_Stand_Up_stageii.npz --save_path test_standup.pkl

echo "Complex motion tests completed!"
```

### Test 3: Visualization
```bash
echo "=== Test 3: Visualization ==="

# Visualize all test motions
echo "Visualizing standing motion..."
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl

echo "Visualizing swaying motion..."
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_sway.pkl

echo "Visualizing pickup motion..."
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_pickup.pkl

echo "Visualization tests completed!"
```

### Test 4: Video Recording
```bash
echo "=== Test 4: Video Recording ==="

# Record videos of motions
echo "Recording standing motion video..."
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/test_stand.pkl --record_video --video_path dash_stand_video.mp4

echo "Recording pickup motion video..."
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_results/dash/test_pickup.pkl --record_video --video_path dash_pickup_video.mp4

echo "Video recording tests completed!"
```

## Automated Testing

### Run Comprehensive Tests
```bash
# Run all DASH robot tests
./scripts/dash/test_dash_robot.sh
```

This automated test script will:
- Verify environment setup
- Check motion data availability
- Test motion retargeting
- Validate performance
- Generate test results

### Test Results
- **Location**: `test_results/dash/`
- **Format**: `.pkl` files containing retargeted motion data
- **Documentation**: `test_results/dash/README.md`

## Advanced Usage

### Custom Motion Retargeting
```bash
# Retarget any SMPLX motion file
python scripts/smplx_to_robot.py --robot dash --smplx_file YOUR_MOTION_FILE.npz --save_path YOUR_OUTPUT.pkl

# With custom parameters
python scripts/smplx_to_robot.py --robot dash --smplx_file YOUR_MOTION_FILE.npz --save_path YOUR_OUTPUT.pkl --rate_limit --verbose
```

### Batch Processing
```bash
# Process multiple motions at once
for motion_file in motion_data/ACCAD/Male1General_c3d/*.npz; do
    filename=$(basename "$motion_file" .npz)
    echo "Processing $filename..."
    python scripts/smplx_to_robot.py --robot dash --smplx_file "$motion_file" --save_path "batch_${filename}.pkl"
done
```

### BVH Motion Support
```bash
# If you have BVH files, you can use:
python scripts/bvh_to_robot.py --robot dash --bvh_file YOUR_BVH_FILE.bvh --save_path YOUR_OUTPUT.pkl
```

## Configuration Files

### IK Configuration (Optimized)
- **SMPLX to DASH**: `general_motion_retargeting/ik_configs/smplx_to_dash.json` (Motion-optimized)
- **BVH to DASH**: `general_motion_retargeting/ik_configs/bvh_lafan1_to_dash.json`
- **Backup Configs**: 
  - `smplx_to_dash.json.backup` (Original)
  - `configs/dash/smplx_to_dash_corrected.json` (Corrected)
  - `configs/dash/smplx_to_dash_optimized.json` (Motion-optimized)

### Robot Model
- **DASH XML**: `assets/DASH_URDF/mjmodel.xml`
- **DASH Meshes**: `assets/DASH_URDF/mesh/`

### Key Configuration Features
- **Motion-based scaling**: Scale factors derived from actual human motion analysis
- **Optimized weights**: Feet (100/40), Torso (100/25), Joints (0/20)
- **Proper joint alignment**: Corrected rotation offsets for each robot joint
- **Dual IK tables**: Primary for stability, secondary for fine-tuning

## Troubleshooting

### Common Issues

1. **Environment not activated**
   ```bash
   conda activate daros_dash
   ```

2. **Missing SMPL-X models**
   ```bash
   # Check if models exist
   ls assets/body_models/models_smplx_v1_1/models/smplx/*.pkl
   ls assets/body_models/models_smplx_v1_1/models/smplx/*.npz
   ```

3. **Motion file not found**
   ```bash
   # Check available motions
   ls motion_data/ACCAD/Male1General_c3d/
   ```

4. **Permission issues**
   ```bash
   # Make sure you have write permissions
   chmod 755 .
   ```

### Debug Commands
```bash
# Check robot configuration
python -c "from general_motion_retargeting.params import ROBOT_XML_DICT, IK_CONFIG_DICT; print('DASH XML:', ROBOT_XML_DICT['dash']); print('DASH IK:', IK_CONFIG_DICT['smplx']['dash'])"

# Test robot initialization
python -c "from general_motion_retargeting.motion_retarget import GeneralMotionRetargeting; retarget = GeneralMotionRetargeting('smplx', 'dash'); print('DASH robot initialized successfully!')"
```

## File Structure
```
/home/anh/daros/GMR/
├── assets/
│   ├── DASH_URDF/
│   │   ├── mjmodel.xml          # DASH robot model
│   │   └── mesh/                # DASH robot meshes
│   └── body_models/
│       └── smplx/               # SMPL-X body models
├── general_motion_retargeting/
│   └── ik_configs/
│       ├── smplx_to_dash.json   # SMPLX to DASH mapping
│       └── bvh_lafan1_to_dash.json # BVH to DASH mapping
├── motion_data/
│   └── ACCAD/                   # Motion data
├── scripts/
│   ├── smplx_to_robot.py        # Main retargeting script
│   ├── vis_robot_motion.py      # Visualization script
│   └── bvh_to_robot.py          # BVH retargeting script
└── DASH_ROBOT_INSTRUCTIONS.md   # This file
```

## Quick Reference Commands

### Essential Commands
```bash
# Activate environment
conda activate daros_dash

# Basic retargeting
python scripts/smplx_to_robot.py --robot dash --smplx_file MOTION_FILE.npz --save_path OUTPUT.pkl

# Visualize motion
python scripts/vis_robot_motion.py --robot dash --robot_motion_path OUTPUT.pkl

# Record video
python scripts/vis_robot_motion.py --robot dash --robot_motion_path OUTPUT.pkl --record_video --video_path video.mp4
```

### Available Robots
- `dash` - Your DASH robot
- `g1` - Unitree G1
- `h1` - Unitree H1
- `talos` - PAL TALOS
- And many more...

### Available Motion Formats
- `smplx` - SMPL-X format (recommended)
- `bvh` - BVH format
- `fbx` - FBX format

## Support
If you encounter any issues:
1. Check that the conda environment is activated
2. Verify that all required files exist
3. Check the file permissions
4. Review the error messages for specific issues

Your DASH robot is now fully integrated and ready for motion retargeting.
