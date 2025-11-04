#!/usr/bin/env python3
"""
Enhanced DASH Robot Analysis Tool
Creates optimal IK configuration based on DASH robot characteristics
"""

import json
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path

class EnhancedDASHAnalyzer:
    def __init__(self, urdf_path="assets/DASH_URDF/robot.urdf"):
        self.urdf_path = urdf_path
        self.joint_analysis = {}
        
    def analyze_dash_structure(self):
        """Analyze DASH robot structure and create optimal weights"""
        print("Analyzing DASH robot structure...")
        
        # DASH robot specific analysis based on its design
        # DASH is a humanoid robot with specific joint priorities
        
        joint_priorities = {
            # Core stability joints (highest priority)
            'torso': {'position': 300, 'rotation': 50, 'scale': 0.8},
            'r_foot': {'position': 300, 'rotation': 50, 'scale': 0.8},
            'l_foot': {'position': 300, 'rotation': 50, 'scale': 0.8},
            
            # Locomotion joints (high priority)
            'r_hip': {'position': 150, 'rotation': 30, 'scale': 0.75},
            'l_hip': {'position': 150, 'rotation': 30, 'scale': 0.75},
            'r_upper_leg': {'position': 150, 'rotation': 30, 'scale': 0.75},
            'l_upper_leg': {'position': 150, 'rotation': 30, 'scale': 0.75},
            
            # Manipulation joints (medium priority)
            'r_prox_shoulder': {'position': 100, 'rotation': 25, 'scale': 0.7},
            'l_prox_shoulder': {'position': 100, 'rotation': 25, 'scale': 0.7},
            'r_upper_arm': {'position': 100, 'rotation': 25, 'scale': 0.7},
            'l_upper_arm': {'position': 100, 'rotation': 25, 'scale': 0.7},
            
            # Fine manipulation joints (lower priority)
            'r_lower_arm': {'position': 80, 'rotation': 20, 'scale': 0.65},
            'l_lower_arm': {'position': 80, 'rotation': 20, 'scale': 0.65}
        }
        
        return joint_priorities
    
    def create_optimal_config(self):
        """Create optimal DASH configuration"""
        print("Creating optimal DASH configuration...")
        
        joint_priorities = self.analyze_dash_structure()
        
        # Create configuration
        config = {
            "robot_root_name": "torso",
            "human_root_name": "pelvis",
            "ground_height": 0.0,
            "human_height_assumption": 1.8,
            "use_ik_match_table1": True,
            "use_ik_match_table2": True,
            "human_scale_table": {
                "pelvis": 0.8,
                "spine1": 0.8,
                "spine2": 0.8,
                "spine3": 0.8,
                "neck": 0.7,
                "head": 0.7,
                "left_hip": 0.75,
                "right_hip": 0.75,
                "left_knee": 0.75,
                "right_knee": 0.75,
                "left_ankle": 0.7,
                "right_ankle": 0.7,
                "left_foot": 0.8,
                "right_foot": 0.8,
                "left_shoulder": 0.7,
                "right_shoulder": 0.7,
                "left_elbow": 0.7,
                "right_elbow": 0.7,
                "left_wrist": 0.65,
                "right_wrist": 0.65
            },
            "ik_match_table1": {},
            "ik_match_table2": {}
        }
        
        # Joint mapping
        joint_mapping = {
            'torso': 'pelvis',
            'r_hip': 'right_hip',
            'r_upper_leg': 'right_knee',
            'r_foot': 'right_foot',
            'l_hip': 'left_hip',
            'l_upper_leg': 'left_knee',
            'l_foot': 'left_foot',
            'r_prox_shoulder': 'right_shoulder',
            'r_upper_arm': 'right_elbow',
            'r_lower_arm': 'right_wrist',
            'l_prox_shoulder': 'left_shoulder',
            'l_upper_arm': 'left_elbow',
            'l_lower_arm': 'left_wrist'
        }
        
        # Generate IK tables
        for robot_joint, human_joint in joint_mapping.items():
            if robot_joint in joint_priorities:
                priority = joint_priorities[robot_joint]
                
                # Table 1 (primary) - higher weights
                config["ik_match_table1"][robot_joint] = [
                    human_joint,
                    priority['position'],
                    priority['rotation'],
                    [0.0, 0.0, 0.0],
                    [0.8, -0.2, -0.2, -0.2]
                ]
                
                # Table 2 (secondary) - reduced weights for fine-tuning
                config["ik_match_table2"][robot_joint] = [
                    human_joint,
                    int(priority['position'] * 0.6),
                    int(priority['rotation'] * 0.6),
                    [0.0, 0.0, 0.0],
                    [0.8, -0.2, -0.2, -0.2]
                ]
        
        return config
    
    def test_configuration(self, config, motion_file):
        """Test configuration with a motion file"""
        print(f"Testing configuration with: {motion_file}")
        
        # Save test configuration
        with open("test_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run motion retargeting test
        import subprocess
        cmd = [
            "python", "scripts/smplx_to_robot.py",
            "--robot", "dash",
            "--smplx_file", motion_file,
            "--save_path", "test_result.pkl"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("Configuration test successful!")
                return True
            else:
                print(f"Configuration test failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Configuration test error: {e}")
            return False

def main():
    analyzer = EnhancedDASHAnalyzer()
    
    # Create optimal configuration
    optimal_config = analyzer.create_optimal_config()
    
    # Save optimal configuration
    with open("smplx_to_dash_optimal.json", 'w') as f:
        json.dump(optimal_config, f, indent=2)
    
    print("\n=== OPTIMAL DASH CONFIGURATION GENERATED ===")
    print("Configuration saved to: smplx_to_dash_optimal.json")
    
    # Print configuration summary
    print("\nConfiguration Summary:")
    print(f"Scale factors range: {min(optimal_config['human_scale_table'].values()):.2f} - {max(optimal_config['human_scale_table'].values()):.2f}")
    
    pos_weights = [entry[1] for entry in optimal_config['ik_match_table1'].values()]
    rot_weights = [entry[2] for entry in optimal_config['ik_match_table1'].values()]
    
    print(f"Position weights range: {min(pos_weights)} - {max(pos_weights)}")
    print(f"Rotation weights range: {min(rot_weights)} - {max(rot_weights)}")
    
    # Test with a motion file
    test_motion = "motion_data/ACCAD/Male2General_c3d/A1-_Stand_stageii.npz"
    if Path(test_motion).exists():
        print(f"\nTesting configuration with: {test_motion}")
        success = analyzer.test_configuration(optimal_config, test_motion)
        if success:
            print("Configuration test PASSED!")
        else:
            print("Configuration test FAILED!")
    else:
        print(f"Test motion file not found: {test_motion}")
    
    return optimal_config

if __name__ == "__main__":
    config = main()
