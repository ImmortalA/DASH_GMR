# Test Motions

We list some test motions here that are not easy for retargeting (i.e., sometimes giving bad results).
The [x] means the motion is retargeted successfully.

## DASH Robot Test Results

### Test Results Location
- **Directory**: `test_results/dash/`
- **Documentation**: `docs/dash/README.md`
- **Test Scripts**: `scripts/dash/test_dash_robot.sh`

### ACCAD Dataset (Optimized Configuration)
- [x] General_A1_-_Stand_stageii.npz (Standing motion - excellent quality)
  - **Test File**: `test_results/dash/test_stand.pkl`
  - **Performance**: 29-30 FPS, stable balance
- [x] General_A2_-_Sway_stageii.npz (Swaying motion - good balance)
  - **Test File**: `test_results/dash/test_sway.pkl`
  - **Performance**: 29-30 FPS, natural swaying
- [x] General_A3_-_Swing_Arms_While_Stand_stageii.npz (Arm movement - natural motion)
  - **Test File**: `test_results/dash/test_arms.pkl`
  - **Performance**: 29-30 FPS, smooth arm movement
- [x] General_A5_-_Pick_Up_Box_stageii.npz (Pickup motion - stable execution)
  - **Test File**: `test_results/dash/test_pickup.pkl`
  - **Performance**: 29-30 FPS, stable pickup
- [x] General_A7_-_Sit_Down_stageii.npz (Sitting motion - good leg coordination)
  - **Test File**: `test_results/dash/test_sit.pkl`
  - **Performance**: 29-30 FPS, smooth sitting
- [x] General_A8_-_Stand_Up_stageii.npz (Standing up - smooth transition)
  - **Test File**: `test_results/dash/test_stand_up.pkl`
  - **Performance**: 29-30 FPS, natural standing up

### Key Improvements with DASH
- **Motion-based scaling**: Scale factors derived from actual human motion analysis
- **Optimized IK weights**: Feet (100/40), Torso (100/25), Joints (0/20)
- **Proper joint alignment**: Corrected rotation offsets for each robot joint
- **Dual IK tables**: Primary for stability, secondary for fine-tuning

### Configuration Files
- **Active**: `general_motion_retargeting/ik_configs/smplx_to_dash.json`
- **Optimized**: `configs/dash/smplx_to_dash_optimized.json` (recommended)
- **Corrected**: `configs/dash/smplx_to_dash_corrected.json`

# AMASS

- [x] BMLrub_rub081_0031_rom_stageii.npz
- [x] KIT_3_walk_6m_straight_line04_stageii.npz
- [ ] DanceDB/20120807_CliodelaVara/Clio_Maleviziotikos_stageii.npz
- [ ] DanceDB/20130216_AnnaCharalambous/Anna_Curiosity_C3D_stageii.npz (Body jittering)
- [ ] CMU/111/111_21_stageii.npz (Should be laying on the ground facing right. The right arm is wristed on G1)

# LAFAN1

- [x] dance1_subject2.bvh