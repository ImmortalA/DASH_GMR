# How to Create a Robot IK Configuration JSON File

This guide teaches you how to create a JSON configuration file for mapping human motion to robot motion.

## Table of Contents

1. [Overview](#overview)
2. [JSON Structure](#json-structure)
3. [Step-by-Step Process](#step-by-step-process)
4. [Understanding Each Field](#understanding-each-field)
5. [Tools and Scripts](#tools-and-scripts)
6. [Example: Creating a Config from Scratch](#example-creating-a-config-from-scratch)
7. [Common Issues and Solutions](#common-issues-and-solutions)

## Overview

The IK configuration file maps human body parts (from SMPL-X, BVH, or FBX) to robot body parts and defines how motion should be scaled and retargeted. It's a JSON file with the following main components:

- **Basic Settings**: Root names, ground height, human height assumption
- **Scale Table**: How to scale each human body part to match robot dimensions
- **IK Match Tables**: Which human body parts map to which robot body parts, with weights and offsets

## JSON Structure

```json
{
    "robot_root_name": "torso",              // Root body name in robot model
    "human_root_name": "pelvis",             // Root body name in human model
    "ground_height": 0.0,                     // Ground plane height
    "human_height_assumption": 1.8,          // Assumed human height (meters)
    "use_ik_match_table1": true,              // Use primary IK table
    "use_ik_match_table2": true,              // Use secondary IK table (optional)
    "human_scale_table": {                   // Scale factors for each human body part
        "pelvis": 0.55,
        "left_hip": 0.55,
        ...
    },
    "ik_match_table1": {                      // Primary mapping: robot_body -> human_body
        "robot_body_name": [
            "human_body_name",                // Human body part to track
            position_weight,                   // Weight for position tracking (0-100)
            rotation_weight,                   // Weight for rotation tracking (0-100)
            [x_offset, y_offset, z_offset],   // Position offset (meters)
            [w, x, y, z]                       // Rotation quaternion offset (wxyz format)
        ],
        ...
    },
    "ik_match_table2": {                      // Secondary mapping (optional, for fine-tuning)
        "robot_body_name": [
            "human_body_name",                // Human body part to track
            position_weight,                   // Weight for position tracking (0-100)
            rotation_weight,                   // Weight for rotation tracking (0-100)
            [x_offset, y_offset, z_offset],   // Position offset (meters)
            [w, x, y, z]                       // Rotation quaternion offset (wxyz format)
        ],
        ...
    }
}
```

## Step-by-Step Process

### Step 1: Get Robot Body Names

First, you need to know all the body part names in your robot model.

**Method 1: Use the retargeting system**
```bash
python -c "from general_motion_retargeting import GeneralMotionRetargeting; gmr = GeneralMotionRetargeting('smplx', 'dash', verbose=True)"
```

This will print all robot body names, DoF names, and motor names.

**Method 2: Check the robot XML/MJCF file**
Look in `assets/dash/mjmodel.xml` or similar for `<body>` tags.

**Method 3: Use extraction script**
```bash
# Generates configs/dash/smplx_to_dash_from_urdf.json by default
python scripts/dash/extract_urdf_config.py --urdf assets/DASH_URDF/mjmodel.xml
```

### Step 2: Get Human Body Names

The human body names depend on your motion format:

- **SMPL-X**: `pelvis`, `left_hip`, `right_hip`, `spine1`, `spine2`, `spine3`, `neck`, `head`, `left_shoulder`, `right_shoulder`, `left_elbow`, `right_elbow`, `left_wrist`, `right_wrist`, etc.
- **BVH (LAFAN1)**: `Hips`, `Spine1`, `Spine2`, `LeftUpLeg`, `RightUpLeg`, `LeftLeg`, `RightLeg`, `LeftFootMod`, `RightFootMod`, `LeftArm`, `RightArm`, `LeftForeArm`, `RightForeArm`, `LeftHand`, `RightHand`
- **FBX**: `Hips`, `Spine1`, `LeftUpLeg`, `RightUpLeg`, etc.

### Step 3: Map Human to Robot Bodies

Create a mapping table. For each robot body part, decide which human body part it should track.

**Example mapping:**
```python
mapping = {
    "torso": "pelvis",           # Robot torso tracks human pelvis
    "r_hip": "right_hip",         # Robot right hip tracks human right hip
    "r_upper_leg": "right_knee",  # Robot upper leg tracks human knee
    "r_lower_leg": "right_ankle", # Robot lower leg tracks human ankle
    "r_foot": "right_foot",       # Robot foot tracks human foot
    # ... and so on
}
```

### Step 4: Determine Scale Factors

Scale factors determine how much to scale human body parts to match robot dimensions.

**Method 1: Measure robot dimensions**
- Measure your robot's actual dimensions
- Compare with average human dimensions
- Calculate scale ratio

**Method 2: Use URDF analysis**
```bash
python scripts/dash/extract_urdf_config.py --urdf assets/DASH_URDF/mjmodel.xml
```

**Method 3: Motion-based optimization** (Recommended)
```bash
python scripts/dash/optimize_dash_mapping.py
```

This analyzes actual motion data to determine optimal scales.

**Typical scale ranges:**
- Torso/legs: 0.5 - 0.6 (robot is ~50-60% of human size)
- Arms: 0.4 - 0.5 (robot arms are ~40-50% of human arms)
- Head/neck: 0.3 - 0.4 (if robot has head)

### Step 5: Set Weights

Weights determine how important position vs rotation tracking is for each body part.

**Position weight (0-100):**
- **100**: Critical for stability (feet, pelvis)
- **50-80**: Important for balance (torso, knees)
- **0**: Only track rotation, not position (joints, elbows)

**Rotation weight (0-100):**
- **50-100**: Important for orientation (feet, hands, head)
- **10-30**: Basic orientation (joints, limbs)
- **0**: Only track position, not rotation

**Recommended weights:**
```python
# Feet: Critical for stability
"r_foot": [100, 40, ...]  # High position, medium rotation

# Torso: Important for balance
"torso": [100, 25, ...]   # High position, low rotation

# Joints: Only rotations matter
"r_hip": [0, 20, ...]      # No position, rotation only
"r_knee": [0, 20, ...]      # No position, rotation only
```

### Step 6: Calculate Rotation Offsets

Rotation offsets align the coordinate frames between human and robot.

**Common quaternions:**
```python
# Identity (no rotation)
[1.0, 0.0, 0.0, 0.0]

# 180° rotation around X-axis
[0.0, 1.0, 0.0, 0.0]

# 180° rotation around Y-axis
[0.0, 0.0, 1.0, 0.0]

# 180° rotation around Z-axis
[0.0, 0.0, 0.0, 1.0]

# 90° rotation around X-axis (common for torso)
[0.70710678, 0.70710678, 0.0, 0.0]

# 180° rotation (common for coordinate frame alignment)
[0.5, -0.5, -0.5, -0.5]
```

**How to determine:**
1. Visualize robot and human motion side-by-side
2. If robot appears rotated incorrectly, adjust the quaternion
3. Test different rotations until alignment looks correct

### Step 7: Set Position Offsets

Position offsets are usually `[0.0, 0.0, 0.0]` unless you need to shift the tracking point.

**When to use offsets:**
- Robot body part center is different from human body part center
- Need to compensate for different joint locations
- Fine-tuning specific body parts

### Step 8: Create the JSON File

Put it all together in a JSON file:

```json
{
    "robot_root_name": "torso",
    "human_root_name": "pelvis",
    "ground_height": 0.0,
    "human_height_assumption": 1.8,
    "use_ik_match_table1": true,
    "use_ik_match_table2": false,
    "human_scale_table": {
        "pelvis": 0.55,
        "left_hip": 0.55,
        "right_hip": 0.55,
        "spine1": 0.55,
        "left_knee": 0.55,
        "right_knee": 0.55,
        "left_ankle": 0.45,
        "right_ankle": 0.45,
        "left_foot": 0.55,
        "right_foot": 0.55,
        "left_shoulder": 0.45,
        "right_shoulder": 0.45,
        "left_elbow": 0.45,
        "right_elbow": 0.45,
        "left_wrist": 0.45,
        "right_wrist": 0.45,
        "neck": 0.4,
        "head": 0.4
    },
    "ik_match_table1": {
        "torso": ["pelvis", 100, 25, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_hip": ["right_hip", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_upper_leg": ["right_knee", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_lower_leg": ["right_ankle", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_foot": ["right_foot", 100, 40, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_hip": ["left_hip", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_upper_leg": ["left_knee", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_lower_leg": ["left_ankle", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_foot": ["left_foot", 100, 40, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_shoulder": ["right_shoulder", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_upper_arm": ["right_elbow", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "r_lower_arm": ["right_wrist", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_shoulder": ["left_shoulder", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_upper_arm": ["left_elbow", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
        "l_lower_arm": ["left_wrist", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]]
    },
    "ik_match_table2": {}
}
```

## Understanding Each Field

### Basic Settings

**`robot_root_name`**: The name of the root body in your robot model (usually "pelvis", "torso", "base_link", etc.)

**`human_root_name`**: The name of the root body in the human model (usually "pelvis" for SMPL-X, "Hips" for BVH)

**`ground_height`**: Height of the ground plane (usually 0.0)

**`human_height_assumption`**: Assumed height of the human in meters. This is used to scale motion if the actual human height differs. Average is 1.7-1.8m.

**`use_ik_match_table1`**: Whether to use the primary IK mapping table (usually `true`)

**`use_ik_match_table2`**: Whether to use a secondary IK mapping table for fine-tuning (optional, can be `false`)

### Human Scale Table

**`human_scale_table`**: A dictionary mapping each human body part name to a scale factor.

- **Scale factor < 1.0**: Robot is smaller than human (most common)
- **Scale factor = 1.0**: Robot is same size as human
- **Scale factor > 1.0**: Robot is larger than human (rare)

**How to calculate:**
```
scale_factor = robot_dimension / human_dimension
```

For example, if robot pelvis height is 0.5m and human pelvis height is 0.9m:
```
pelvis_scale = 0.5 / 0.9 = 0.55
```

### IK Match Table

**`ik_match_table1`**: Primary mapping from robot body parts to human body parts.

Each entry has 5 components:

1. **Human body name** (string): Which human body part to track
2. **Position weight** (0-100): How important position tracking is
3. **Rotation weight** (0-100): How important rotation tracking is
4. **Position offset** [x, y, z]: Offset in meters
5. **Rotation offset** [w, x, y, z]: Quaternion offset (wxyz format)

**Example:**
```json
"r_foot": [
    "right_foot",        // Track human right foot
    100,                  // High position weight (critical for stability)
    40,                   // Medium rotation weight
    [0.0, 0.0, 0.0],     // No position offset
    [0.5, -0.5, -0.5, -0.5]  // Rotation offset for coordinate alignment
]
```

## Tools and Scripts

### 1. Extract Robot Body Names
```bash
python scripts/dash/extract_urdf_config.py --urdf assets/DASH_URDF/mjmodel.xml
```

### 2. Analyze Motion Data
```bash
python scripts/dash/optimize_dash_mapping.py
```

### 3. Compare Configurations
```bash
# Compare the active DASH config with the optimized reference
python scripts/dash/compare_configs.py

# Compare any two files (optionally include table2)
python scripts/dash/compare_configs.py configs/dash/smplx_to_dash_from_urdf.json configs/dash/smplx_to_dash_optimized.json --include-table2
```

### 4. Test Configuration
```bash
python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz
```

### 5. Visualize Comparison
```bash
./scripts/dash/compare_motion.sh
```

## Example: Working with DASH Robot Configuration

This example shows how to work with the DASH robot configuration. You can use this as a template for other robots.

### Step 1: Get DASH Robot Body Names
```bash
python -c "from general_motion_retargeting import GeneralMotionRetargeting; gmr = GeneralMotionRetargeting('smplx', 'dash', verbose=True)"
```

Output:
```
Body ID 0: world
Body ID 1: torso
Body ID 2: r_hip
Body ID 3: r_upper_leg
Body ID 4: r_foot
Body ID 5: l_hip
Body ID 6: l_upper_leg
Body ID 7: l_foot
Body ID 8: r_prox_shoulder
Body ID 9: r_upper_arm
Body ID 10: r_lower_arm
Body ID 11: l_prox_shoulder
Body ID 12: l_upper_arm
Body ID 13: l_lower_arm
...
```

### Step 2: Create Basic Structure
```json
{
    "robot_root_name": "torso",
    "human_root_name": "pelvis",
    "ground_height": 0.0,
    "human_height_assumption": 1.8,
    "use_ik_match_table1": true,
    "use_ik_match_table2": false,
    "human_scale_table": {},
    "ik_match_table1": {},
    "ik_match_table2": {}
}
```

### Step 3: Fill Scale Table
Measure your robot or use URDF analysis:
```json
"human_scale_table": {
    "pelvis": 0.55,
    "left_hip": 0.55,
    "right_hip": 0.55,
    "spine1": 0.55,
    "left_knee": 0.55,
    "right_knee": 0.55,
    "left_ankle": 0.45,
    "right_ankle": 0.45,
    "left_foot": 0.55,
    "right_foot": 0.55,
    "left_shoulder": 0.45,
    "right_shoulder": 0.45,
    "left_elbow": 0.45,
    "right_elbow": 0.45,
    "left_wrist": 0.45,
    "right_wrist": 0.45,
    "neck": 0.4,
    "head": 0.4
}
```

### Step 4: Create IK Mapping
Map each robot body to a human body:
```json
"ik_match_table1": {
    "torso": ["pelvis", 100, 25, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
    "r_hip": ["right_hip", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
    "r_upper_leg": ["right_knee", 0, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
    "r_foot": ["right_foot", 100, 40, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
    // ... add all robot body parts
}
```

### Step 5: Test and Iterate
1. The DASH config is already saved at `general_motion_retargeting/ik_configs/smplx_to_dash.json`
2. Test with a motion file:
   ```bash
   python scripts/smplx_to_robot.py --robot dash --smplx_file motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz
   ```
3. Visualize and compare:
   ```bash
   ./scripts/dash/compare_motion.sh
   ```
4. Adjust weights, scales, and offsets in the config file as needed
5. Repeat until motion looks good

## Common Issues and Solutions

### Issue 1: Robot appears upside down
**Solution**: Change rotation quaternion in root body mapping
- Try: `[1.0, 0.0, 0.0, 0.0]` (identity)
- Try: `[0.0, 1.0, 0.0, 0.0]` (180° X-axis)
- Try: `[0.0, 0.0, 1.0, 0.0]` (180° Y-axis)

### Issue 2: Robot motion is too small/large
**Solution**: Adjust scale factors in `human_scale_table`
- Increase scale for larger motion
- Decrease scale for smaller motion

### Issue 3: Robot is unstable or falls
**Solution**: Increase position weights for feet and pelvis
- Feet: `[100, 40, ...]` (high position weight)
- Pelvis: `[100, 25, ...]` (high position weight)

### Issue 4: Joints don't align properly
**Solution**: Adjust rotation quaternions for each joint
- Test different quaternions
- Use visualization to check alignment

### Issue 5: Motion is jerky
**Solution**: 
- Reduce position weights for non-critical joints
- Use `ik_match_table2` for fine-tuning
- Check if scale factors are too extreme

## Best Practices

1. **Start with a similar robot's config**: Copy an existing config for a similar robot and modify it
2. **Use motion-based optimization**: Run `optimize_dash_mapping.py` to get optimal scales
3. **Test incrementally**: Add a few body parts at a time and test
4. **Visualize often**: Use comparison tools to see what's working
5. **Document your changes**: Keep notes on what values work best
6. **Backup working configs**: Save good versions before making changes

## Resources

- **Existing configs**: `general_motion_retargeting/ik_configs/`
- **DASH example**: `general_motion_retargeting/ik_configs/smplx_to_dash.json`
- **Documentation**: `DOC.md`, `docs/dash/DASH_IK_CONFIGURATION_GUIDE.md`
- **Tools**: `scripts/dash/extract_urdf_config.py`, `scripts/dash/optimize_dash_mapping.py`

---

## Complete Example: DASH Robot Configuration (Line-by-Line Explanation)

This section explains the complete `smplx_to_dash.json` file line by line, explaining every number and parameter.

### Basic Settings (Lines 1-7)

```json
{
    "robot_root_name": "torso",              // Line 2: Robot's root body name (base of robot)
    "human_root_name": "pelvis",             // Line 3: Human's root body name (SMPL-X format)
    "ground_height": 0.0,                    // Line 4: Ground plane height in meters (0.0 = ground level)
    "human_height_assumption": 1.8319240556762808,  // Line 5: Assumed human height in meters (1.83m ≈ 6 feet)
    "use_ik_match_table1": true,             // Line 6: Enable primary IK mapping table
    "use_ik_match_table2": true,             // Line 7: Enable secondary IK mapping table (for fine-tuning)
```

**Explanation:**
- **Line 2**: `"torso"` - The DASH robot's root body is called "torso" in the robot model
- **Line 3**: `"pelvis"` - SMPL-X human model uses "pelvis" as the root body
- **Line 4**: `0.0` - Ground is at zero height (no offset)
- **Line 5**: `1.8319240556762808` - The assumed human height (1.83 meters). This is used to scale motion if the actual human height differs. The system will automatically adjust: `actual_scale = config_scale * (actual_height / 1.8319240556762808)`
- **Line 6**: `true` - Use the primary IK table (`ik_match_table1`)
- **Line 7**: `true` - Also use secondary IK table (`ik_match_table2`) for additional constraints

### Human Scale Table (Lines 8-64)

```json
    "human_scale_table": {                   // Line 8: Start of scale factors dictionary
        "pelvis": 0.55,                      // Line 9: Pelvis scale = 0.55 (robot pelvis is 55% of human pelvis size)
        "left_hip": 0.55,                    // Line 10: Left hip scale = 0.55
        "right_hip": 0.55,                   // Line 11: Right hip scale = 0.55
        "spine1": 0.55,                      // Line 12: First spine segment scale = 0.55
        "left_knee": 0.55,                   // Line 13: Left knee scale = 0.55
        "right_knee": 0.55,                  // Line 14: Right knee scale = 0.55
        "spine2": 0.55,                      // Line 15: Second spine segment scale = 0.55
        "left_ankle": 0.45,                  // Line 16: Left ankle scale = 0.45 (smaller than hip/knee)
        "right_ankle": 0.45,                 // Line 17: Right ankle scale = 0.45
        "spine3": 0.55,                      // Line 18: Third spine segment scale = 0.55
        "left_foot": 0.55,                   // Line 19: Left foot scale = 0.55
        "right_foot": 0.55,                  // Line 20: Right foot scale = 0.55
        "neck": 0.4,                         // Line 21: Neck scale = 0.4 (robot neck is 40% of human neck)
        "left_collar": 0.4,                  // Line 22: Left collar scale = 0.4
        "right_collar": 0.4,                 // Line 23: Right collar scale = 0.4
        "head": 0.4,                         // Line 24: Head scale = 0.4
        "left_shoulder": 0.45,               // Line 25: Left shoulder scale = 0.45 (arms are smaller)
        "right_shoulder": 0.45,              // Line 26: Right shoulder scale = 0.45
        "left_elbow": 0.45,                  // Line 27: Left elbow scale = 0.45
        "right_elbow": 0.45,                 // Line 28: Right elbow scale = 0.45
        "left_wrist": 0.45,                  // Line 29: Left wrist scale = 0.45
        "right_wrist": 0.45,                 // Line 30: Right wrist scale = 0.45
        "jaw": 0.4,                          // Line 31: Jaw scale = 0.4 (not used by DASH, but required)
        // ... (fingers and eyes - not used by DASH robot but required by SMPL-X)
```

**Scale Factor Meanings:**
- **0.55** (pelvis, hips, knees, spine, feet): Robot torso and legs are 55% of human size
- **0.45** (ankles, shoulders, elbows, wrists): Robot arms and ankles are 45% of human size
- **0.4** (neck, head, collar, jaw, fingers): Robot upper body parts are 40% of human size (DASH doesn't have head/hands, but these are required for SMPL-X)

**How scales work:**
- If human pelvis moves 1.0 meter, robot pelvis moves 0.55 meters (scaled by 0.55)
- If human shoulder moves 1.0 meter, robot shoulder moves 0.45 meters (scaled by 0.45)

### IK Match Table 1 - Primary Mapping (Lines 65-274)

```json
    "ik_match_table1": {                     // Line 65: Start of primary IK mapping table
        "torso": [                           // Line 66: Robot torso mapping
            "pelvis",                        // Line 67: Track human pelvis
            100,                             // Line 68: Position weight = 100 (maximum - critical for stability)
            25,                              // Line 69: Rotation weight = 25 (medium - orientation matters but less than position)
            [0.0, 0.0, 0.0],                 // Line 70-72: Position offset [x, y, z] = [0, 0, 0] meters (no offset)
            [0.5, -0.5, -0.5, -0.5]          // Line 73-76: Rotation quaternion [w, x, y, z] = 180° rotation for coordinate alignment
        ],
        "r_hip": [                           // Line 82: Robot right hip mapping
            "right_hip",                     // Line 83: Track human right hip
            0,                               // Line 84: Position weight = 0 (don't track position, only rotation)
            20,                              // Line 85: Rotation weight = 20 (moderate rotation tracking)
            [0.0, 0.0, 0.0],                 // Line 86-88: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 89-92: Rotation quaternion for alignment
        ],
        "r_upper_leg": [                     // Line 98: Robot right upper leg
            "right_knee",                    // Line 99: Track human right knee (not thigh, but knee position)
            0,                               // Line 100: Position weight = 0 (joints don't need position tracking)
            20,                              // Line 101: Rotation weight = 20
            [0.0, 0.0, 0.0],                 // Line 102-104: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 105-108: Rotation alignment
        ],
        "r_foot": [                          // Line 114: Robot right foot (CRITICAL for stability)
            "right_foot",                    // Line 115: Track human right foot
            100,                             // Line 116: Position weight = 100 (MAXIMUM - feet are critical for balance)
            40,                              // Line 117: Rotation weight = 40 (HIGH - foot orientation is important)
            [0.0, 0.0, 0.0],                 // Line 118-120: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 121-124: Rotation alignment
        ],
        // ... (similar pattern for left side: l_hip, l_upper_leg, l_foot)
        "r_prox_shoulder": [                 // Line 178: Robot right proximal shoulder
            "right_shoulder",                 // Line 179: Track human right shoulder
            0,                               // Line 180: Position weight = 0 (joint, no position tracking)
            15,                              // Line 181: Rotation weight = 15 (lower than legs, arms are less critical)
            [0.0, 0.0, 0.0],                 // Line 182-184: No position offset
            [0.0, 0.707, 0.0, 0.707]         // Line 185-188: Rotation quaternion [w=0, x=0.707, y=0, z=0.707] = 90° rotation around Y-axis
        ],
        "r_upper_arm": [                     // Line 194: Robot right upper arm
            "right_elbow",                    // Line 195: Track human right elbow
            0,                               // Line 196: Position weight = 0
            15,                              // Line 197: Rotation weight = 15
            [0.0, 0.0, 0.0],                 // Line 198-200: No position offset
            [0.0, 0.0, 0.0, -1.0]            // Line 201-204: Rotation quaternion [w=0, x=0, y=0, z=-1] = 180° rotation around Z-axis
        ],
        "r_lower_arm": [                     // Line 210: Robot right lower arm
            "right_wrist",                    // Line 211: Track human right wrist
            0,                               // Line 212: Position weight = 0
            15,                              // Line 213: Rotation weight = 15
            [0.0, 0.0, 0.0],                 // Line 214-216: No position offset
            [0.0, 0.0, 0.0, -1.0]            // Line 217-220: Same rotation as upper arm (180° around Z-axis)
        ],
        "l_prox_shoulder": [                 // Line 226: Robot left proximal shoulder
            "left_shoulder",                  // Line 227: Track human left shoulder
            0,                               // Line 228: Position weight = 0
            15,                              // Line 229: Rotation weight = 15
            [0.0, 0.0, 0.0],                 // Line 230-232: No position offset
            [0.707, 0.0, -0.707, 0.0]        // Line 233-236: Rotation quaternion [w=0.707, x=0, y=-0.707, z=0] = 90° rotation around X-axis (mirror of right)
        ],
        "l_upper_arm": [                     // Line 242: Robot left upper arm
            "left_elbow",                     // Line 243: Track human left elbow
            0,                               // Line 244: Position weight = 0
            15,                              // Line 245: Rotation weight = 15
            [0.0, 0.0, 0.0],                 // Line 246-248: No position offset
            [1.0, 0.0, 0.0, 0.0]             // Line 249-252: Rotation quaternion [w=1, x=0, y=0, z=0] = Identity (no rotation)
        ],
        "l_lower_arm": [                     // Line 258: Robot left lower arm
            "left_wrist",                     // Line 259: Track human left wrist
            0,                               // Line 260: Position weight = 0
            15,                              // Line 261: Rotation weight = 15
            [0.0, 0.0, 0.0],                 // Line 262-264: No position offset
            [1.0, 0.0, 0.0, 0.0]             // Line 265-268: Identity rotation (no rotation needed)
        ]
    },
```

### IK Match Table 2 - Secondary Mapping (Lines 275-484)

```json
    "ik_match_table2": {                     // Line 275: Start of secondary IK mapping table (for fine-tuning)
        "torso": [                           // Line 276: Robot torso (secondary constraint)
            "pelvis",                        // Line 277: Track human pelvis
            100,                             // Line 278: Position weight = 100 (same as table 1)
            15,                              // Line 279: Rotation weight = 15 (LOWER than table 1's 25 - less emphasis)
            [0.0, 0.0, 0.0],                 // Line 280-282: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 283-286: Same rotation as table 1
        ],
        "r_hip": [                           // Line 292: Robot right hip (secondary)
            "right_hip",                     // Line 293: Track human right hip
            15,                              // Line 294: Position weight = 15 (DIFFERENT from table 1's 0 - adds position constraint)
            10,                              // Line 295: Rotation weight = 10 (LOWER than table 1's 20)
            [0.0, 0.0, 0.0],                 // Line 296-298: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 299-302: Same rotation
        ],
        "r_upper_leg": [                     // Line 308: Robot right upper leg (secondary)
            "right_knee",                    // Line 309: Track human right knee
            15,                              // Line 310: Position weight = 15 (adds position constraint, table 1 had 0)
            10,                              // Line 311: Rotation weight = 10 (lower than table 1's 20)
            [0.0, 0.0, 0.0],                 // Line 312-314: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 315-318: Same rotation
        ],
        "r_foot": [                          // Line 324: Robot right foot (secondary)
            "right_foot",                    // Line 325: Track human right foot
            100,                             // Line 326: Position weight = 100 (same as table 1 - critical)
            30,                              // Line 327: Rotation weight = 30 (LOWER than table 1's 40 - less emphasis)
            [0.0, 0.0, 0.0],                 // Line 328-330: No position offset
            [0.5, -0.5, -0.5, -0.5]          // Line 331-334: Same rotation
        ],
        // ... (similar pattern for other body parts)
        "r_prox_shoulder": [                  // Line 388: Robot right shoulder (secondary)
            "right_shoulder",                 // Line 389: Track human right shoulder
            15,                              // Line 390: Position weight = 15 (adds position constraint, table 1 had 0)
            8,                               // Line 391: Rotation weight = 8 (LOWER than table 1's 15)
            [0.0, 0.0, 0.0],                 // Line 392-394: No position offset
            [0.0, 0.707, 0.0, 0.707]         // Line 395-398: Same rotation as table 1
        ],
        // ... (similar for arms)
    }                                         // Line 484: End of ik_match_table2
}                                             // Line 485: End of JSON file
```

### Understanding the Numbers

#### Position Weights (0-100)
- **100**: Maximum priority - Critical for stability (torso, feet)
- **15**: Medium priority - Adds position constraint (used in table 2 for joints)
- **0**: No position tracking - Only track rotation (joints in table 1)

#### Rotation Weights (0-100)
- **40**: High priority - Important orientation (feet in table 1)
- **30**: Medium-high priority - Important but less critical (feet in table 2)
- **25**: Medium priority - Moderate orientation tracking (torso in table 1)
- **20**: Medium-low priority - Basic orientation (hips, legs in table 1)
- **15**: Low-medium priority - Light orientation tracking (torso in table 2, shoulders/arms in table 1)
- **10**: Low priority - Minimal orientation (hips, legs in table 2)
- **8**: Very low priority - Fine-tuning only (shoulders/arms in table 2)

#### Position Offsets [x, y, z]
- **All [0.0, 0.0, 0.0]**: No offset needed - robot and human body part centers align
- **If offset needed**: E.g., `[0.05, 0.0, 0.0]` would shift tracking 5cm in X direction

#### Rotation Quaternions [w, x, y, z] (wxyz format)

**Format**: Quaternions are in **wxyz** order (scalar first, then vector components)

**Common quaternions used in DASH config:**

1. **`[0.5, -0.5, -0.5, -0.5]`** - 180° rotation
   - Used for: Torso, hips, legs, feet
   - Purpose: Coordinate frame alignment between human and robot
   - Effect: Rotates coordinate system 180° to match robot's orientation

2. **`[1.0, 0.0, 0.0, 0.0]`** - Identity (no rotation)
   - Used for: Left upper arm, left lower arm
   - Purpose: No rotation needed - human and robot align naturally
   - Effect: No rotation applied

3. **`[0.0, 0.707, 0.0, 0.707]`** - 90° rotation around Y-axis
   - Used for: Right proximal shoulder
   - Purpose: Aligns right shoulder joint orientation
   - Effect: Rotates 90° around Y-axis (vertical axis)

4. **`[0.707, 0.0, -0.707, 0.0]`** - 90° rotation around X-axis
   - Used for: Left proximal shoulder
   - Purpose: Mirrors right shoulder alignment for left side
   - Effect: Rotates 90° around X-axis (horizontal axis, forward-backward)

5. **`[0.0, 0.0, 0.0, -1.0]`** - 180° rotation around Z-axis
   - Used for: Right upper arm, right lower arm
   - Purpose: Aligns right arm orientation
   - Effect: Rotates 180° around Z-axis (vertical axis, left-right)

**How to determine quaternion values:**
- Start with identity `[1.0, 0.0, 0.0, 0.0]` if unsure
- Test different rotations if robot appears misaligned
- Use visualization to check alignment
- Common patterns: 180° rotations for coordinate alignment, 90° rotations for joint alignment

### Why Two IK Tables?

**Table 1 (Primary)**: Main constraints
- High weights for critical body parts (torso, feet)
- Zero position weights for joints (only rotation matters)
- Defines the primary motion retargeting strategy

**Table 2 (Secondary)**: Fine-tuning
- Lower weights overall (less aggressive)
- Adds position constraints to joints (15 weight) for smoother motion
- Provides additional constraints to improve motion quality
- Helps balance between table 1's constraints

**Combined Effect**: Both tables work together - Table 1 provides strong constraints for stability, Table 2 adds smoothness and fine-tuning.

### Key Insights from DASH Configuration

1. **Feet are critical**: Position weight 100 in both tables (maximum priority)
2. **Torso stability**: Position weight 100, rotation weight 25/15 (high position, moderate rotation)
3. **Joints use rotation only in table 1**: Position weight 0 (joints don't need position tracking)
4. **Table 2 adds position to joints**: Position weight 15 (smoother motion)
5. **Arms have lower priority**: Rotation weights 15/8 (less critical than legs)
6. **Asymmetric rotations**: Left and right arms use different quaternions (mirroring)

### Quick Reference: Number Meanings

| Value | Type | Meaning | Example Usage |
|-------|------|---------|---------------|
| **0.55** | Scale factor | Robot is 55% of human size | Torso, hips, knees, spine, feet |
| **0.45** | Scale factor | Robot is 45% of human size | Ankles, shoulders, elbows, wrists |
| **0.4** | Scale factor | Robot is 40% of human size | Neck, head, collar, fingers |
| **100** | Position weight | Maximum priority (critical) | Torso, feet (stability) |
| **15** | Position weight | Medium priority | Joints in table 2 (smoothness) |
| **0** | Position weight | No position tracking | Joints in table 1 (rotation only) |
| **40** | Rotation weight | High priority | Feet in table 1 (orientation) |
| **30** | Rotation weight | Medium-high priority | Feet in table 2 |
| **25** | Rotation weight | Medium priority | Torso in table 1 |
| **20** | Rotation weight | Medium-low priority | Hips, legs in table 1 |
| **15** | Rotation weight | Low-medium priority | Torso table 2, shoulders/arms table 1 |
| **10** | Rotation weight | Low priority | Hips, legs in table 2 |
| **8** | Rotation weight | Very low priority | Shoulders/arms in table 2 |
| **1.8319240556762808** | Height (meters) | Assumed human height | Used for automatic scaling |
| **0.0** | Offset (meters) | No offset | All position offsets in DASH config |
| **0.707** | Quaternion component | 90° rotation component | Shoulder rotations |
| **0.5** | Quaternion component | 180° rotation component | Coordinate alignment |
| **-0.5** | Quaternion component | 180° rotation component | Coordinate alignment |
| **-1.0** | Quaternion component | 180° rotation component | Arm alignment |
| **1.0** | Quaternion component | Identity (no rotation) | Left arm (no rotation needed) |

---

**Next Steps**: Start with an existing config, modify it for your robot, test with visualization, and iterate until you get good results!

