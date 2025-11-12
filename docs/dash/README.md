# DASH Robot Documentation

This directory contains all documentation related to the DASH robot integration with the GMR (General Motion Retargeting) system.

## File Organization

### **User Guides**
- **[DASH_ROBOT_INSTRUCTIONS.md](DASH_ROBOT_INSTRUCTIONS.md)** - Complete user guide for using DASH robot with GMR
- **[DASH_IK_CONFIGURATION_GUIDE.md](DASH_IK_CONFIGURATION_GUIDE.md)** - Detailed guide for configuring IK parameters

### **Technical Documentation**
- **[DASH_INTEGRATION_SUMMARY.md](DASH_INTEGRATION_SUMMARY.md)** - Comprehensive integration summary and technical details

## Quick Start

### **1. Basic Usage**
```bash
# Activate environment
conda activate daros_dash
cd /home/anh/daros/GMR

# Test motion retargeting
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_stand.pkl

# Visualize results
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl
```

### **2. Configuration Management**
```bash
# Use optimized configuration (recommended)
cp configs/dash/smplx_to_dash_optimized.json general_motion_retargeting/ik_configs/smplx_to_dash.json

# Use corrected configuration
cp configs/dash/smplx_to_dash_corrected.json general_motion_retargeting/ik_configs/smplx_to_dash.json
```

### **3. Automated Testing**
```bash
# Run comprehensive tests
./scripts/dash/test_dash_robot.sh

# Activate environment
./scripts/dash/activate_dash_env.sh
```

## Configuration Files

### **Active Configuration**
- **Location**: `general_motion_retargeting/ik_configs/smplx_to_dash.json`
- **Type**: URDF-enhanced configuration (recommended)
- **Features**: URDF-derived quaternions, motion-optimized weights, precise joint alignment

### **Alternative Configurations**
- **URDF Baseline**: `configs/dash/smplx_to_dash_from_urdf.json` (Extracted from MJCF/URDF)
- **Backup**: `general_motion_retargeting/ik_configs/smplx_to_dash.json.bak-20251112-2` (Pre-URDF backup)

## Test Results

### **Test Files Location**
- **Directory**: `test_results/dash/`
- **Format**: `.pkl` files containing retargeted motion data
- **Types**: Standing, swaying, arm movement, pickup, sitting, standing up

### **Performance Metrics**
- **FPS**: 29-30 FPS stable rendering
- **Motion Quality**: Excellent (motion-optimized configuration)
- **Balance**: Stable (optimized foot tracking)
- **Joint Alignment**: Accurate (corrected rotation offsets)

## Development Tools

### **Scripts Location**
- **Directory**: `scripts/dash/`
- **Purpose**: Configuration optimization, testing, and analysis

### **Available Scripts**
- `test_dash_robot.sh` - Automated testing
- `activate_dash_env.sh` - Environment activation
- `compare_motion.sh` - Side-by-side NPZ/PKL visualization helper
- `visualize_npz_and_robot.py` - Human vs robot motion viewer
- `optimize_dash_mapping.py` - Motion-based configuration optimization
- `extract_urdf_config.py` - MJCF/URDF configuration extraction
- `compare_configs.py` - Configuration comparison

## Key Features

### **URDF-Enhanced Configuration**
- **Quaternions**: Extracted from robot MJCF/URDF geometry for precise joint alignment
- **Scale factors**: Derived from robot link lengths (0.54 torso/legs, 0.48 arms)
- **Weight distribution**: Motion-optimized weights (Feet 100/40, Torso 100/25, Joints 0/20)
- **Dual IK tables**: Primary for stability, secondary for fine-tuning
- **Hybrid approach**: Combines geometric accuracy with motion-tuned stability

### **Supported Motion Formats**
- **SMPLX**: AMASS dataset, OMOMO dataset
- **BVH**: LAFAN1 dataset, Nokov dataset
- **Real-time**: Compatible with live motion capture

## Next Steps

1. **Read the user guide**: Start with `DASH_ROBOT_INSTRUCTIONS.md`
2. **Test basic motions**: Try the quick start examples
3. **Customize configuration**: Use `DASH_IK_CONFIGURATION_GUIDE.md`
4. **Explore advanced features**: Check the technical documentation

## Support

For questions or issues:
1. Check the documentation in this directory
2. Review the main GMR documentation
3. Check the test results for examples
4. Use the development scripts for troubleshooting

---

**Last Updated**: November 12, 2025  
**Status**: Production Ready  
**Quality**: URDF-Enhanced (Geometric Accuracy + Motion Optimization)
