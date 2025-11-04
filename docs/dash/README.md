# DASH Robot Documentation

This directory contains all documentation related to the DASH robot integration with the GMR (General Motion Retargeting) system.

## File Organization

### **User Guides**
- **[DASH_ROBOT_INSTRUCTIONS.md](DASH_ROBOT_INSTRUCTIONS.md)** - Complete user guide for using DASH robot with GMR
- **[DASH_IK_CONFIGURATION_GUIDE.md](DASH_IK_CONFIGURATION_GUIDE.md)** - Detailed guide for configuring IK parameters

### **Technical Documentation**
- **[DASH_INTEGRATION_SUMMARY.md](DASH_INTEGRATION_SUMMARY.md)** - Comprehensive integration summary and technical details
- **[dash_mapping_analysis.md](dash_mapping_analysis.md)** - Technical analysis of motion mapping and optimization

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
- **Type**: Motion-optimized configuration (recommended)
- **Features**: Motion-based scaling, optimized weights, proper joint alignment

### **Alternative Configurations**
- **Optimized**: `configs/dash/smplx_to_dash_optimized.json` (Motion-optimized)
- **Corrected**: `configs/dash/smplx_to_dash_corrected.json` (Basic corrections)
- **Backup**: `general_motion_retargeting/ik_configs/smplx_to_dash.json.backup` (Original)

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
- `optimize_dash_mapping.py` - Motion-based optimization
- `fix_dash_mapping.py` - Basic configuration fixes
- `extract_urdf_config.py` - URDF configuration extraction
- `compare_configs.py` - Configuration comparison

## Key Features

### **Motion-Optimized Configuration**
- **Scale factors**: Derived from actual human motion analysis
- **Weight distribution**: Feet (100/40), Torso (100/25), Joints (0/20)
- **Joint alignment**: Corrected rotation offsets for each robot joint
- **Dual IK tables**: Primary for stability, secondary for fine-tuning

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

**Last Updated**: October 21, 2025  
**Status**: Production Ready  
**Quality**: Motion-Optimized
