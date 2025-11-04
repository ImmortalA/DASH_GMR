# IK Config
In our ik config such as `smplx_to_g1.json` or `smplx_to_dash.json`, you might find following params. I add annotations here for your understanding.

## DASH Robot Configuration

The DASH robot uses an optimized motion-based configuration that provides superior motion retargeting quality:

- **Motion-based scaling**: Scale factors derived from actual human motion analysis
- **Optimized weights**: Feet (100/40), Torso (100/25), Joints (0/20)
- **Proper joint alignment**: Corrected rotation offsets for each robot joint
- **Dual IK tables**: Primary for stability, secondary for fine-tuning

### Key Configuration Files
- `general_motion_retargeting/ik_configs/smplx_to_dash.json` - Active motion-optimized configuration
- `general_motion_retargeting/ik_configs/bvh_lafan1_to_dash.json` - BVH motion support
- `general_motion_retargeting/ik_configs/smplx_to_dash.json.backup` - Original configuration backup
- `configs/dash/smplx_to_dash_optimized.json` - Motion-optimized configuration (recommended)
- `configs/dash/smplx_to_dash_corrected.json` - Basic corrected configuration

### Documentation
- `docs/dash/DASH_IK_CONFIGURATION_GUIDE.md` - Detailed configuration guide
- `docs/dash/DASH_ROBOT_INSTRUCTIONS.md` - Complete user guide
- `docs/dash/README.md` - Documentation index
```json
"ik_match_table1": {
        "pelvis": [ # robot's body name
            "pelvis", # corresponding human body name, here we are using "pelvis" as example
            100, # weight to track 3D positions (xyz)
            10, # weight to track 3D rotations
            [
                0.0, # x offset added to human body "pelvis" x
                0.0, # y offset added to human body "pelvis" y
                0.0 # z offset added to human body "pelvis" z
            ],
            [
                # the rotation (represented as quaternion) applied to human body "pelvis". the order follows scalar first (wxyz)
                0.5,
                -0.5,
                -0.5,
                -0.5
            ]
        ],
      ...
```
