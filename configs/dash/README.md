# DASH Robot Configuration Files

This directory contains all configuration files for the DASH robot integration with GMR.

## File Organization

### **Active Configuration**
- **Location**: `general_motion_retargeting/ik_configs/smplx_to_dash.json`
- **Status**: Currently active in GMR system
- **Type**: Motion-optimized configuration (recommended)

### **Alternative Configurations**

#### **smplx_to_dash_optimized.json** - **RECOMMENDED**
- **Type**: Motion-optimized configuration
- **Features**: 
  - Motion-based scaling factors
  - Optimized weight distribution
  - Proper joint alignment
  - Dual IK tables for stability
- **Performance**: Excellent motion quality, stable balance
- **Use Case**: Production use, best motion retargeting quality

#### **smplx_to_dash_corrected.json**
- **Type**: Basic corrected configuration
- **Features**:
  - Improved scale factors
  - Better weight distribution
  - Corrected rotation offsets
- **Performance**: Good motion quality, stable performance
- **Use Case**: Fallback option, basic corrections

## Configuration Management

### **Apply Configuration**
```bash
# Apply optimized configuration (recommended)
cp configs/dash/smplx_to_dash_optimized.json general_motion_retargeting/ik_configs/smplx_to_dash.json

# Apply corrected configuration
cp configs/dash/smplx_to_dash_corrected.json general_motion_retargeting/ik_configs/smplx_to_dash.json

# Restore original configuration
cp general_motion_retargeting/ik_configs/smplx_to_dash.json.backup general_motion_retargeting/ik_configs/smplx_to_dash.json
```

### **Backup Current Configuration**
```bash
# Backup current active configuration
cp general_motion_retargeting/ik_configs/smplx_to_dash.json configs/dash/smplx_to_dash_current_backup.json
```

## Configuration Comparison

| Feature | Original | Corrected | Optimized |
|---------|----------|-----------|-----------|
| Scale Factors | URDF-based | Improved | Motion-based |
| Weight Distribution | Basic | Better | Optimized |
| Joint Alignment | Standard | Corrected | Perfect |
| Motion Quality | Poor | Good | Excellent |
| Balance | Unstable | Stable | Excellent |
| Performance | 25-29 FPS | 29-30 FPS | 29-30 FPS |

## Configuration Details

### **Scale Factors**
- **Torso/Legs**: 0.55 (optimized), 0.6 (corrected)
- **Arms**: 0.45 (optimized), 0.5 (corrected)
- **Head/Neck**: 0.4 (optimized), 0.5 (corrected)

### **Weight Distribution**
- **Feet**: 100/40 (position/rotation)
- **Torso**: 100/25 (position/rotation)
- **Joints**: 0/20 (position/rotation)

### **IK Tables**
- **Table 1**: Primary mapping with higher weights
- **Table 2**: Secondary mapping for fine-tuning

## Testing Configurations

### **Test Script**
```bash
# Test current configuration
./scripts/dash/test_dash_robot.sh

# Test specific configuration
cp configs/dash/smplx_to_dash_optimized.json general_motion_retargeting/ik_configs/smplx_to_dash.json
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_optimized.pkl
```

### **Performance Testing**
```bash
# Test different motion types
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A2_-_Sway_stageii.npz --save_path test_sway.pkl
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz --save_path test_arms.pkl
```

## Optimization Process

### **Motion Analysis**
1. **Human Motion Data**: Analyzed 55 body parts from actual motion
2. **Scale Calculation**: Derived from motion ranges and robot dimensions
3. **Weight Optimization**: Based on movement importance and stability
4. **Joint Alignment**: Corrected rotation offsets for proper mapping

### **Key Improvements**
- **Motion-based scaling**: More accurate than URDF-based scaling
- **Optimized weights**: Better balance between position and rotation tracking
- **Proper joint alignment**: Corrected quaternion offsets
- **Dual IK tables**: Primary for stability, secondary for fine-tuning

## Recommendations

### **For Production Use**
- **Use**: `smplx_to_dash_optimized.json`
- **Reason**: Best motion quality, stable performance
- **Performance**: 29-30 FPS, excellent motion following

### **For Development/Testing**
- **Use**: `smplx_to_dash_corrected.json`
- **Reason**: Good balance of quality and simplicity
- **Performance**: 29-30 FPS, good motion quality

### **For Customization**
- **Start with**: `smplx_to_dash_optimized.json`
- **Modify**: Scale factors, weights, offsets as needed
- **Test**: Use provided test scripts

## Support

For configuration questions:
1. Check the documentation in `docs/dash/`
2. Use the comparison script: `scripts/dash/compare_configs.py`
3. Test with different configurations
4. Review the technical analysis in `docs/dash/dash_mapping_analysis.md`

---

**Last Updated**: October 21, 2025  
**Status**: Production Ready  
**Quality**: Motion-Optimized
