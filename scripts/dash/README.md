# DASH Robot Scripts

This directory contains all scripts related to the DASH robot integration with GMR.

## File Organization

### **User Scripts**
- **[test_dash_robot.sh](test_dash_robot.sh)** - Automated testing script
- **[activate_dash_env.sh](activate_dash_env.sh)** - Environment activation script

### **Development Scripts**
- **[optimize_dash_mapping.py](optimize_dash_mapping.py)** - Motion-based configuration optimization
- **[fix_dash_mapping.py](fix_dash_mapping.py)** - Basic configuration fixes
- **[extract_urdf_config.py](extract_urdf_config.py)** - URDF configuration extraction
- **[extract_urdf_config_fixed.py](extract_urdf_config_fixed.py)** - Fixed URDF configuration extraction
- **[compare_configs.py](compare_configs.py)** - Configuration comparison tool

## Quick Start

### **1. Automated Testing**
```bash
# Run comprehensive DASH robot tests
./scripts/dash/test_dash_robot.sh
```

### **2. Environment Activation**
```bash
# Activate DASH environment
./scripts/dash/activate_dash_env.sh
```

### **3. Configuration Optimization**
```bash
# Optimize configuration based on motion analysis
python scripts/dash/optimize_dash_mapping.py
```

## 📋 Script Descriptions

### **test_dash_robot.sh**
**Purpose**: Automated testing of DASH robot integration
**Features**:
- Environment validation
- Motion data verification
- SMPL-X model checking
- Motion retargeting tests
- Performance validation
- Test result summary

**Usage**:
```bash
./scripts/dash/test_dash_robot.sh
```

### **activate_dash_env.sh**
**Purpose**: Activate DASH robot conda environment
**Features**:
- Environment activation
- Status verification
- Error handling

**Usage**:
```bash
./scripts/dash/activate_dash_env.sh
```

### **optimize_dash_mapping.py**
**Purpose**: Create motion-optimized IK configuration
**Features**:
- Human motion analysis
- Scale factor calculation
- Weight optimization
- Joint alignment correction
- Configuration generation

**Usage**:
```bash
python scripts/dash/optimize_dash_mapping.py
```

**Output**: `smplx_to_dash_optimized.json`

### **fix_dash_mapping.py**
**Purpose**: Create basic corrected IK configuration
**Features**:
- Improved scale factors
- Better weight distribution
- Corrected rotation offsets
- Basic configuration fixes

**Usage**:
```bash
python scripts/dash/fix_dash_mapping.py
```

**Output**: `smplx_to_dash_corrected.json`

### **extract_urdf_config.py**
**Purpose**: Extract configuration from URDF file
**Features**:
- URDF parsing
- Body part extraction
- Joint analysis
- Configuration generation

**Usage**:
```bash
python scripts/dash/extract_urdf_config.py
```

**Output**: `smplx_to_dash_from_urdf.json`

### **extract_urdf_config_fixed.py**
**Purpose**: Fixed URDF configuration extraction
**Features**:
- Corrected quaternion parsing
- Proper height calculation
- Fixed configuration generation

**Usage**:
```bash
python scripts/dash/extract_urdf_config_fixed.py
```

**Output**: `smplx_to_dash_from_urdf_fixed.json`

### **compare_configs.py**
**Purpose**: Compare different configurations
**Features**:
- Configuration comparison
- Parameter analysis
- Performance metrics
- Recommendations

**Usage**:
```bash
python scripts/dash/compare_configs.py
```

## Development Workflow

### **1. Configuration Development**
```bash
# Extract from URDF
python scripts/dash/extract_urdf_config_fixed.py

# Create basic corrections
python scripts/dash/fix_dash_mapping.py

# Optimize based on motion
python scripts/dash/optimize_dash_mapping.py

# Compare configurations
python scripts/dash/compare_configs.py
```

### **2. Testing Workflow**
```bash
# Test current configuration
./scripts/dash/test_dash_robot.sh

# Test specific configuration
cp configs/dash/smplx_to_dash_optimized.json general_motion_retargeting/ik_configs/smplx_to_dash.json
./scripts/dash/test_dash_robot.sh
```

### **3. Environment Management**
```bash
# Activate environment
./scripts/dash/activate_dash_env.sh

# Run tests
./scripts/dash/test_dash_robot.sh
```

## Script Outputs

### **Configuration Files**
- `smplx_to_dash_optimized.json` - Motion-optimized configuration
- `smplx_to_dash_corrected.json` - Basic corrected configuration
- `smplx_to_dash_from_urdf.json` - URDF-based configuration
- `smplx_to_dash_from_urdf_fixed.json` - Fixed URDF configuration

### **Test Results**
- `test_stand.pkl` - Standing motion test
- `test_sway.pkl` - Swaying motion test
- `test_arms.pkl` - Arm movement test
- `test_pickup.pkl` - Pickup motion test

## Testing Examples

### **Basic Motion Testing**
```bash
# Test standing motion
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_stand.pkl

# Test arm movement
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz --save_path test_arms.pkl
```

### **Visualization Testing**
```bash
# Visualize standing motion
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl

# Visualize arm movement
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_arms.pkl
```

## Troubleshooting

### **Common Issues**
1. **Environment not activated**: Use `activate_dash_env.sh`
2. **Missing dependencies**: Check conda environment setup
3. **Configuration errors**: Use `compare_configs.py` to diagnose
4. **Motion quality issues**: Try different configurations

### **Debug Commands**
```bash
# Check environment
conda activate daros_dash
python -c "import mujoco, mink, smplx; print('Dependencies OK')"

# Check configuration
python scripts/dash/compare_configs.py

# Test robot initialization
python -c "from general_motion_retargeting.motion_retarget import GeneralMotionRetargeting; retarget = GeneralMotionRetargeting('smplx', 'dash'); print('Robot OK')"
```

## Performance Monitoring

### **FPS Monitoring**
- Target: 29-30 FPS
- Monitor: During motion retargeting
- Tool: Built into retargeting scripts

### **Motion Quality**
- Monitor: Visual inspection
- Tool: `vis_robot_motion.py`
- Criteria: Natural movement, stable balance

### **Configuration Quality**
- Monitor: Configuration comparison
- Tool: `compare_configs.py`
- Criteria: Proper scaling, weight distribution

## Support

For script issues:
1. Check script documentation
2. Review error messages
3. Use debug commands
4. Check configuration files
5. Review test results

---

**Last Updated**: October 21, 2025  
**Status**: Production Ready  
**Quality**: Motion-Optimized
