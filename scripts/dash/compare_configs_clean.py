#!/usr/bin/env python3
"""
Compare different DASH robot IK configurations
"""

import json
import os

def main():
    # Load current configuration
    with open('general_motion_retargeting/ik_configs/smplx_to_dash.json', 'r') as f:
        current_config = json.load(f)
    
    # Load URDF-generated configuration
    with open('../../configs/dash/smplx_to_dash_from_urdf_fixed.json', 'r') as f:
        urdf_config = json.load(f)
    
    print("Configuration Comparison")
    print("=" * 50)
    
    # Compare basic settings
    print("\nBasic Settings:")
    print(f"  Current scale factor: {current_config['human_scale_table']['pelvis']:.2f}")
    print(f"  URDF scale factor:    {urdf_config['human_scale_table']['pelvis']:.2f}")
    print(f"  Difference:           {urdf_config['human_scale_table']['pelvis'] - current_config['human_scale_table']['pelvis']:.2f}")
    
    # Compare scale tables
    print("\nScale Table Comparison:")
    print("  Body Part          Current    URDF      Difference")
    print("  " + "-" * 50)
    
    for body_part in current_config['human_scale_table']:
        if body_part in urdf_config['human_scale_table']:
            current_scale = current_config['human_scale_table'][body_part]
            urdf_scale = urdf_config['human_scale_table'][body_part]
            diff = urdf_scale - current_scale
            print(f"  {body_part:<15} {current_scale:>8.2f}  {urdf_scale:>8.2f}  {diff:>8.2f}")
    
    # Compare IK weights
    print("\nIK Weight Comparison:")
    print("  Robot Part          Current Pos/Rot    URDF Pos/Rot")
    print("  " + "-" * 50)
    
    for robot_part in current_config['ik_match_table1']:
        if robot_part in urdf_config['ik_match_table1']:
            current_entry = current_config['ik_match_table1'][robot_part]
            urdf_entry = urdf_config['ik_match_table1'][robot_part]
            
            current_pos = current_entry[2]
            current_rot = current_entry[3]
            urdf_pos = urdf_entry[2]
            urdf_rot = urdf_entry[3]
            
            print(f"  {robot_part:<15} {current_pos:>8.1f}/{current_rot:>8.1f}  {urdf_pos:>8.1f}/{urdf_rot:>8.1f}")
    
    # Analysis
    print("\nAnalysis:")
    print("  1. The URDF configuration is based on your robot's actual dimensions")
    print("  2. Your current configuration uses 0.8 (80% of human size)")
    print("  3. The URDF configuration is more accurate to your robot's actual dimensions")
    print("  4. Consider testing the URDF configuration for better motion scaling")
    
    print("\nNext Steps:")
    print("  1. Test the URDF configuration: cp configs/dash/smplx_to_dash_from_urdf_fixed.json general_motion_retargeting/ik_configs/smplx_to_dash.json")
    print("  2. Run motion retargeting tests with the new configuration")
    print("  3. Compare motion quality between the two configurations")
    print("  4. Adjust weights and offsets based on your robot's performance")

if __name__ == "__main__":
    main()
