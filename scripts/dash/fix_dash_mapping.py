#!/usr/bin/env python3
"""
Fix DASH robot IK mapping based on proper human-robot body part correspondence
"""

import json

def create_corrected_dash_config():
    """Create a corrected DASH configuration with proper mappings"""
    
    config = {
        "robot_root_name": "torso",
        "human_root_name": "pelvis",
        "ground_height": 0.0,
        "human_height_assumption": 1.8,
        "use_ik_match_table1": True,
        "use_ik_match_table2": True,
        "human_scale_table": {
            "pelvis": 0.6,
            "spine1": 0.6,
            "spine2": 0.6,
            "spine3": 0.6,
            "neck": 0.5,
            "head": 0.5,
            "left_hip": 0.6,
            "right_hip": 0.6,
            "left_knee": 0.6,
            "right_knee": 0.6,
            "left_ankle": 0.5,
            "right_ankle": 0.5,
            "left_foot": 0.6,
            "right_foot": 0.6,
            "left_shoulder": 0.5,
            "right_shoulder": 0.5,
            "left_elbow": 0.5,
            "right_elbow": 0.5,
            "left_wrist": 0.5,
            "right_wrist": 0.5
        },
        "ik_match_table1": {
            # Torso mapping - most important for stability
            "torso": ["pelvis", 100, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            # Right leg - proper sequence
            "r_hip": ["right_hip", 0, 15, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "r_upper_leg": ["right_knee", 0, 15, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "r_foot": ["right_foot", 100, 30, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            # Left leg - proper sequence
            "l_hip": ["left_hip", 0, 15, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "l_upper_leg": ["left_knee", 0, 15, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "l_foot": ["left_foot", 100, 30, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            # Right arm - proper sequence
            "r_prox_shoulder": ["right_shoulder", 0, 10, [0.0, 0.0, 0.0], [0.0, 0.707, 0.0, 0.707]],
            "r_upper_arm": ["right_elbow", 0, 10, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
            "r_lower_arm": ["right_wrist", 0, 10, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
            
            # Left arm - proper sequence
            "l_prox_shoulder": ["left_shoulder", 0, 10, [0.0, 0.0, 0.0], [0.707, 0.0, -0.707, 0.0]],
            "l_upper_arm": ["left_elbow", 0, 10, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]],
            "l_lower_arm": ["left_wrist", 0, 10, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
        },
        "ik_match_table2": {
            # Secondary table with different weights for fine-tuning
            "torso": ["pelvis", 100, 10, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            "r_hip": ["right_hip", 10, 5, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "r_upper_leg": ["right_knee", 10, 5, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "r_foot": ["right_foot", 100, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            "l_hip": ["left_hip", 10, 5, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "l_upper_leg": ["left_knee", 10, 5, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            "l_foot": ["left_foot", 100, 20, [0.0, 0.0, 0.0], [0.5, -0.5, -0.5, -0.5]],
            
            "r_prox_shoulder": ["right_shoulder", 10, 5, [0.0, 0.0, 0.0], [0.0, 0.707, 0.0, 0.707]],
            "r_upper_arm": ["right_elbow", 10, 5, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
            "r_lower_arm": ["right_wrist", 10, 5, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -1.0]],
            
            "l_prox_shoulder": ["left_shoulder", 10, 5, [0.0, 0.0, 0.0], [0.707, 0.0, -0.707, 0.0]],
            "l_upper_arm": ["left_elbow", 10, 5, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]],
            "l_lower_arm": ["left_wrist", 10, 5, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
        }
    }
    
    return config

def main():
    print("🔧 Creating corrected DASH IK configuration...")
    
    # Create corrected configuration
    config = create_corrected_dash_config()
    
    # Save the corrected configuration
    # Save to configs/dash/ directory
    os.makedirs('../../configs/dash', exist_ok=True)
    with open('../../configs/dash/smplx_to_dash_corrected.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✅ Corrected configuration saved to: configs/dash/smplx_to_dash_corrected.json")
    
    print("\n🔍 Key improvements:")
    print("  1. Better scale factors (0.6 for torso/legs, 0.5 for arms)")
    print("  2. Proper weight distribution (feet: 100/30, torso: 100/20)")
    print("  3. Corrected rotation offsets for better alignment")
    print("  4. Improved arm mapping sequence")
    print("  5. Better balance between position and rotation tracking")
    
    print("\n🎯 Next steps:")
    print("  1. Test the corrected configuration")
    print("  2. Compare with current configuration")
    print("  3. Apply if motion quality improves")

if __name__ == "__main__":
    main()
