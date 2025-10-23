# DASH Robot IK Configuration Guide

## Overview
The `smplx_to_dash.json` file controls how human motion data is mapped to your DASH robot. This guide explains each parameter and how to optimize them for better motion retargeting.

## File Structure

### 1. Basic Settings
```json
{
    "robot_root_name": "torso",           // DASH robot's root body name
    "human_root_name": "pelvis",          // Human's root body name (SMPLX)
    "ground_height": 0.0,                 // Ground level offset
    "human_height_assumption": 1.8,       // Assumed human height in meters
    "use_ik_match_table1": true,          // Use primary IK mapping
    "use_ik_match_table2": true           // Use secondary IK mapping
}
```

### 2. Human Scale Table
Controls how much each human body part is scaled:
```json
"human_scale_table": {
    "pelvis": 0.8,        // Torso scaling (0.8 = 80% of original size)
    "spine1": 0.8,        // Upper spine scaling
    "spine2": 0.8,        // Middle spine scaling
    "spine3": 0.8,        // Lower spine scaling
    "left_hip": 0.8,      // Left hip scaling
    "right_hip": 0.8,     // Right hip scaling
    "left_knee": 0.8,     // Left knee scaling
    "right_knee": 0.8,    // Right knee scaling
    "left_foot": 0.8,     // Left foot scaling
    "right_foot": 0.8,    // Right foot scaling
    "left_shoulder": 0.7, // Left shoulder scaling
    "right_shoulder": 0.7,// Right shoulder scaling
    "left_elbow": 0.7,    // Left elbow scaling
    "right_elbow": 0.7,   // Right elbow scaling
    "left_wrist": 0.7,    // Left wrist scaling
    "right_wrist": 0.7    // Right wrist scaling
}
```

### 3. IK Match Tables
Each entry maps a robot body part to a human body part with weights and offsets:

```json
"ik_match_table1": {
    "ROBOT_BODY_PART": [
        "HUMAN_BODY_PART",    // Human body part to track
        POSITION_WEIGHT,      // Position tracking weight (0-100)
        ROTATION_WEIGHT,      // Rotation tracking weight (0-100)
        [X_OFFSET, Y_OFFSET, Z_OFFSET],  // Position offset
        [QW, QX, QY, QZ]      // Rotation offset (quaternion)
    ]
}
```

## Configuration Parameters Explained

### Position Weights (0-100)
- **100**: Critical tracking (e.g., feet for balance)
- **50-99**: Important tracking (e.g., hands for manipulation)
- **1-49**: Moderate tracking (e.g., arms for posture)
- **0**: No position tracking (rotation only)

### Rotation Weights (0-100)
- **100**: Critical rotation tracking
- **50-99**: Important rotation tracking
- **1-49**: Moderate rotation tracking
- **0**: No rotation tracking

### Position Offsets [X, Y, Z]
- **X**: Forward/backward offset
- **Y**: Left/right offset  
- **Z**: Up/down offset
- Units: meters

### Rotation Offsets [QW, QX, QY, QZ]
- Quaternion format (W, X, Y, Z)
- Controls orientation alignment between human and robot

## DASH Robot Body Parts

Your DASH robot has these body parts available for mapping:

### Torso
- `torso` - Main body/torso

### Legs
- `r_hip` - Right hip joint
- `r_upper_leg` - Right upper leg (thigh)
- `r_lower_leg` - Right lower leg (shin)
- `r_foot` - Right foot
- `l_hip` - Left hip joint
- `l_upper_leg` - Left upper leg (thigh)
- `l_lower_leg` - Left lower leg (shin)
- `l_foot` - Left foot

### Arms
- `r_prox_shoulder` - Right proximal shoulder
- `r_upper_arm` - Right upper arm
- `r_lower_arm` - Right lower arm
- `l_prox_shoulder` - Left proximal shoulder
- `l_upper_arm` - Left upper arm
- `l_lower_arm` - Left lower arm

## SMPLX Human Body Parts

Available human body parts from SMPLX data:

### Torso
- `pelvis` - Pelvis/hip area
- `spine1` - Upper spine
- `spine2` - Middle spine
- `spine3` - Lower spine
- `neck` - Neck
- `head` - Head

### Legs
- `left_hip` - Left hip
- `right_hip` - Right hip
- `left_knee` - Left knee
- `right_knee` - Right knee
- `left_ankle` - Left ankle
- `right_ankle` - Right ankle
- `left_foot` - Left foot
- `right_foot` - Right foot

### Arms
- `left_shoulder` - Left shoulder
- `right_shoulder` - Right shoulder
- `left_elbow` - Left elbow
- `right_elbow` - Right elbow
- `left_wrist` - Left wrist
- `right_wrist` - Right wrist

## Common Configuration Adjustments

### 1. Improve Balance
```json
// Increase foot tracking weights
"r_foot": ["right_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
"l_foot": ["left_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]]
```

### 2. Better Arm Movement
```json
// Increase arm tracking weights
"r_upper_arm": ["right_elbow", 50, 30, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
"l_upper_arm": ["left_elbow", 50, 30, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
```

### 3. Adjust for Robot Size
```json
// Scale down for smaller robot
"human_scale_table": {
    "pelvis": 0.7,        // Smaller torso
    "left_hip": 0.7,      // Shorter legs
    "right_hip": 0.7,
    "left_shoulder": 0.6, // Shorter arms
    "right_shoulder": 0.6
}
```

### 4. Fix Orientation Issues
```json
// Adjust rotation offsets for better alignment
"torso": ["pelvis", 100, 10, [0.0, 0.0, 0.0], [0.707, 0.0, 0.0, 0.707]]  // 90° rotation
```

## Testing Your Configuration

### 1. Test Different Motion Types
```bash
# Test standing motion
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz --save_path test_stand.pkl

# Test arm movement
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A3_-_Swing_Arms_While_Stand_stageii.npz --save_path test_arms.pkl

# Test leg movement
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/ACCAD/Male1General_c3d/General_A7_-_Sit_Down_stageii.npz --save_path test_legs.pkl
```

### 2. Visualize Results
```bash
# Compare different configurations
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl
```

### 3. Record Videos for Comparison
```bash
# Record videos to compare configurations
python scripts/vis_robot_motion.py --robot dash --robot_motion_path test_stand.pkl --record_video --video_path config1_stand.mp4
```

## Common Issues and Solutions

### Issue 1: Robot Falls Over
**Solution**: Increase foot tracking weights
```json
"r_foot": ["right_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
"l_foot": ["left_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]]
```

### Issue 2: Arms Don't Move Naturally
**Solution**: Adjust arm mapping and weights
```json
"r_upper_arm": ["right_elbow", 30, 20, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
"l_upper_arm": ["left_elbow", 30, 20, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
```

### Issue 3: Robot Too Big/Small
**Solution**: Adjust scale table
```json
"human_scale_table": {
    "pelvis": 0.6,        // Smaller
    "left_hip": 0.6,
    "right_hip": 0.6
}
```

### Issue 4: Wrong Orientation
**Solution**: Adjust rotation offsets
```json
"torso": ["pelvis", 100, 10, [0.0, 0.0, 0.0], [0.707, 0.0, 0.0, 0.707]]  // 90° rotation
```

## Advanced Configuration Tips

### 1. Use Two IK Tables
- **Table 1**: Primary mapping with high weights
- **Table 2**: Secondary mapping with different weights for fine-tuning

### 2. Gradual Adjustment
- Start with basic configuration
- Test with simple motions (standing, swaying)
- Gradually adjust weights and offsets
- Test with complex motions (walking, manipulation)

### 3. Motion-Specific Tuning
- Create different configurations for different motion types
- Use higher weights for critical body parts
- Adjust offsets based on robot's physical constraints

### 4. Performance Optimization
- Lower weights for less critical body parts
- Use position-only tracking where rotation isn't needed
- Balance between accuracy and computational efficiency

## Example Configurations

### Conservative Configuration (Stable)
```json
{
    "ik_match_table1": {
        "torso": ["pelvis", 100, 10, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_foot": ["right_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_foot": ["left_foot", 100, 50, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_upper_arm": ["right_elbow", 20, 10, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
        "l_upper_arm": ["left_elbow", 20, 10, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
    }
}
```

### Aggressive Configuration (More Human-like)
```json
{
    "ik_match_table1": {
        "torso": ["pelvis", 100, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_foot": ["right_foot", 100, 30, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_foot": ["left_foot", 100, 30, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_upper_arm": ["right_elbow", 60, 40, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
        "l_upper_arm": ["left_elbow", 60, 40, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
    }
}
```

## Quick Reference

### Weight Guidelines
- **Feet**: 100 (critical for balance)
- **Torso**: 100 (critical for stability)
- **Hips**: 50-80 (important for leg movement)
- **Knees**: 30-60 (moderate for leg movement)
- **Shoulders**: 20-50 (moderate for arm movement)
- **Elbows**: 10-30 (low for arm movement)
- **Wrists**: 5-20 (very low for hand movement)

### Scale Guidelines
- **Torso**: 0.6-0.9 (adjust for robot size)
- **Legs**: 0.6-0.9 (adjust for leg length)
- **Arms**: 0.5-0.8 (adjust for arm length)

### Offset Guidelines
- **Position**: Usually [0.0, 0.0, 0.0] unless specific alignment needed
- **Rotation**: Use quaternions to align human and robot orientations

Remember to test your changes with different motion types and adjust gradually for the best results!
