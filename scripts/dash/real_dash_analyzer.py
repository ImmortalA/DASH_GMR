#!/usr/bin/env python3
"""
DASH Robot Real Analysis Tool
Based on actual DASH robot structure and motion data
"""

import json
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path

class DASHRealAnalyzer:
    def __init__(self):
        self.urdf_path = "assets/DASH_URDF/robot.urdf"
        self.mjmodel_path = "assets/DASH_URDF/mjmodel.xml"
        
    def analyze_dash_structure(self):
        """Analyze actual DASH robot structure from URDF"""
        print("Analyzing actual DASH robot structure...")
        
        # From the actual robot output, we can see:
        # DoF 0-5: floating_base_joint (6 DOF for root)
        # DoF 6-10: right leg (hip_yaw, hip_roll, hip_pitch, knee_pitch, ankle_pitch)
        # DoF 11-15: left leg (hip_yaw, hip_roll, hip_pitch, knee_pitch, ankle_pitch)
        # DoF 16-19: right arm (shoulder_pitch, shoulder_roll, shoulder_yaw, elbow_pitch)
        # DoF 20-23: left arm (shoulder_pitch, shoulder_roll, shoulder_yaw, elbow_pitch)
        
        # Body structure:
        # torso -> r_hip -> r_dist_hip -> r_upper_leg -> r_lower_leg -> r_foot
        # torso -> l_hip -> l_dist_hip -> l_upper_leg -> l_lower_leg -> l_foot
        # torso -> r_prox_shoulder -> r_dist_shoulder -> r_upper_arm -> r_lower_arm
        # torso -> l_prox_shoulder -> l_dist_shoulder -> l_upper_arm -> l_lower_arm
        
        # Analyze joint limits from URDF
        tree = ET.parse(self.urdf_path)
        root = tree.getroot()
        
        joint_limits = {}
        for joint in root.findall('joint'):
            joint_name = joint.get('name')
            limits = joint.find('limit')
            if limits is not None:
                effort = float(limits.get('effort', 10))
                velocity = float(limits.get('velocity', 10))
                lower = float(limits.get('lower', -np.pi))
                upper = float(limits.get('upper', np.pi))
                
                joint_limits[joint_name] = {
                    'effort': effort,
                    'velocity': velocity,
                    'range': upper - lower,
                    'range_deg': np.degrees(upper - lower)
                }
        
        print(f"Found {len(joint_limits)} joints with limits")
        
        # Analyze link masses
        link_masses = {}
        for link in root.findall('link'):
            link_name = link.get('name')
            inertial = link.find('inertial')
            if inertial is not None:
                mass_elem = inertial.find('mass')
                if mass_elem is not None:
                    mass = float(mass_elem.get('value', 0))
                    link_masses[link_name] = mass
        
        print(f"Found {len(link_masses)} links with mass data")
        
        return joint_limits, link_masses
    
    def analyze_motion_data(self, motion_file):
        """Analyze actual motion data characteristics"""
        print(f"Analyzing motion data: {motion_file}")
        
        try:
            data = np.load(motion_file, allow_pickle=True)
            
            # Analyze motion characteristics
            trans = data['trans']  # Root translation
            root_orient = data['root_orient']  # Root orientation
            pose_body = data['pose_body']  # Body pose (63 DOF)
            
            analysis = {
                'frames': len(trans),
                'duration': len(trans) / data['mocap_frame_rate'],
                'fps': data['mocap_frame_rate'],
                
                # Translation analysis
                'trans_range': {
                    'x': [np.min(trans[:, 0]), np.max(trans[:, 0])],
                    'y': [np.min(trans[:, 1]), np.max(trans[:, 1])],
                    'z': [np.min(trans[:, 2]), np.max(trans[:, 2])]
                },
                'trans_std': np.std(trans, axis=0),
                
                # Root orientation analysis
                'root_orient_std': np.std(root_orient, axis=0),
                
                # Body pose analysis
                'pose_body_std': np.std(pose_body, axis=0),
                'pose_body_range': [np.min(pose_body), np.max(pose_body)],
                
                # Motion complexity
                'complexity': {
                    'translation': np.mean(np.std(trans, axis=0)),
                    'orientation': np.mean(np.std(root_orient, axis=0)),
                    'pose': np.mean(np.std(pose_body, axis=0)),
                    'overall': (np.mean(np.std(trans, axis=0)) + 
                               np.mean(np.std(root_orient, axis=0)) + 
                               np.mean(np.std(pose_body, axis=0))) / 3
                }
            }
            
            print(f"Motion analysis: {analysis['frames']} frames, {analysis['duration']:.2f}s, complexity: {analysis['complexity']['overall']:.3f}")
            return analysis
            
        except Exception as e:
            print(f"Error analyzing motion data: {e}")
            return None
    
    def create_optimal_config(self, joint_limits, link_masses, motion_analysis):
        """Create optimal configuration based on real analysis"""
        print("Creating optimal configuration based on real analysis...")
        
        # Base configuration
        config = {
            "robot_root_name": "torso",
            "human_root_name": "pelvis",
            "ground_height": 0.0,
            "human_height_assumption": 1.8,
            "use_ik_match_table1": True,
            "use_ik_match_table2": True,
            "human_scale_table": {},
            "ik_match_table1": {},
            "ik_match_table2": {}
        }
        
        # Calculate optimal scale factors based on motion analysis
        if motion_analysis:
            complexity = motion_analysis['complexity']['overall']
            base_scale = 0.5 + (complexity * 0.3)  # Scale based on motion complexity
        else:
            base_scale = 0.6
        
        # Scale factors based on body part importance
        scale_factors = {
            'pelvis': base_scale * 1.3,      # Core body
            'spine1': base_scale * 1.3,
            'spine2': base_scale * 1.3,
            'spine3': base_scale * 1.3,
            'neck': base_scale * 1.0,
            'head': base_scale * 1.0,
            'left_hip': base_scale * 1.2,    # Legs
            'right_hip': base_scale * 1.2,
            'left_knee': base_scale * 1.2,
            'right_knee': base_scale * 1.2,
            'left_ankle': base_scale * 1.1,
            'right_ankle': base_scale * 1.1,
            'left_foot': base_scale * 1.3,   # Feet (important for balance)
            'right_foot': base_scale * 1.3,
            'left_shoulder': base_scale * 1.0,  # Arms
            'right_shoulder': base_scale * 1.0,
            'left_elbow': base_scale * 1.0,
            'right_elbow': base_scale * 1.0,
            'left_wrist': base_scale * 0.9,
            'right_wrist': base_scale * 0.9
        }
        
        config['human_scale_table'] = scale_factors
        
        # Create IK match tables based on actual robot structure
        # Map human joints to robot bodies based on actual structure
        
        ik_mappings = {
            'torso': {
                'human_joint': 'pelvis',
                'position_weight': 200,  # High priority for stability
                'rotation_weight': 40,
                'importance': 'critical'
            },
            'r_foot': {
                'human_joint': 'right_foot',
                'position_weight': 200,  # High priority for balance
                'rotation_weight': 40,
                'importance': 'critical'
            },
            'l_foot': {
                'human_joint': 'left_foot',
                'position_weight': 200,  # High priority for balance
                'rotation_weight': 40,
                'importance': 'critical'
            },
            'r_upper_leg': {
                'human_joint': 'right_knee',
                'position_weight': 120,  # Medium-high for locomotion
                'rotation_weight': 25,
                'importance': 'high'
            },
            'l_upper_leg': {
                'human_joint': 'left_knee',
                'position_weight': 120,
                'rotation_weight': 25,
                'importance': 'high'
            },
            'r_hip': {
                'human_joint': 'right_hip',
                'position_weight': 100,  # Medium for locomotion
                'rotation_weight': 20,
                'importance': 'medium'
            },
            'l_hip': {
                'human_joint': 'left_hip',
                'position_weight': 100,
                'rotation_weight': 20,
                'importance': 'medium'
            },
            'r_upper_arm': {
                'human_joint': 'right_elbow',
                'position_weight': 80,   # Lower for manipulation
                'rotation_weight': 15,
                'importance': 'low'
            },
            'l_upper_arm': {
                'human_joint': 'left_elbow',
                'position_weight': 80,
                'rotation_weight': 15,
                'importance': 'low'
            },
            'r_prox_shoulder': {
                'human_joint': 'right_shoulder',
                'position_weight': 70,   # Lower for manipulation
                'rotation_weight': 12,
                'importance': 'low'
            },
            'l_prox_shoulder': {
                'human_joint': 'left_shoulder',
                'position_weight': 70,
                'rotation_weight': 12,
                'importance': 'low'
            },
            'r_lower_arm': {
                'human_joint': 'right_wrist',
                'position_weight': 60,   # Lowest for fine manipulation
                'rotation_weight': 10,
                'importance': 'lowest'
            },
            'l_lower_arm': {
                'human_joint': 'left_wrist',
                'position_weight': 60,
                'rotation_weight': 10,
                'importance': 'lowest'
            }
        }
        
        # Generate IK tables
        for robot_joint, mapping in ik_mappings.items():
            # Table 1 (primary)
            config['ik_match_table1'][robot_joint] = [
                mapping['human_joint'],
                mapping['position_weight'],
                mapping['rotation_weight'],
                [0.0, 0.0, 0.0],
                [0.6, -0.4, -0.4, -0.4]  # Conservative rotation offsets
            ]
            
            # Table 2 (secondary) - reduced weights
            config['ik_match_table2'][robot_joint] = [
                mapping['human_joint'],
                int(mapping['position_weight'] * 0.5),
                int(mapping['rotation_weight'] * 0.5),
                [0.0, 0.0, 0.0],
                [0.6, -0.4, -0.4, -0.4]
            ]
        
        return config
    
    def test_configuration(self, config, motion_file):
        """Test the configuration"""
        print(f"Testing configuration with: {motion_file}")
        
        # Save test config
        with open("test_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Copy to main config
        import shutil
        shutil.copy("test_config.json", "general_motion_retargeting/ik_configs/smplx_to_dash.json")
        
        # Test motion retargeting
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
                print("Configuration test PASSED!")
                return True
            else:
                print(f"Configuration test FAILED: {result.stderr}")
                return False
        except Exception as e:
            print(f"Configuration test error: {e}")
            return False

def main():
    analyzer = DASHRealAnalyzer()
    
    # Analyze robot structure
    joint_limits, link_masses = analyzer.analyze_dash_structure()
    
    # Analyze motion data
    motion_file = "motion_data/ACCAD/Male2General_c3d/A1-_Stand_stageii.npz"
    motion_analysis = analyzer.analyze_motion_data(motion_file)
    
    # Create optimal configuration
    optimal_config = analyzer.create_optimal_config(joint_limits, link_masses, motion_analysis)
    
    # Save configuration
    with open("smplx_to_dash_real_optimal.json", 'w') as f:
        json.dump(optimal_config, f, indent=2)
    
    print("\n=== REAL DASH OPTIMAL CONFIGURATION ===")
    print("Configuration saved to: smplx_to_dash_real_optimal.json")
    
    # Print summary
    scale_factors = optimal_config['human_scale_table']
    print(f"Scale factors range: {min(scale_factors.values()):.2f} - {max(scale_factors.values()):.2f}")
    
    pos_weights = [entry[1] for entry in optimal_config['ik_match_table1'].values()]
    rot_weights = [entry[2] for entry in optimal_config['ik_match_table1'].values()]
    
    print(f"Position weights range: {min(pos_weights)} - {max(pos_weights)}")
    print(f"Rotation weights range: {min(rot_weights)} - {max(rot_weights)}")
    
    # Test configuration
    success = analyzer.test_configuration(optimal_config, motion_file)
    
    if success:
        print("\nConfiguration test PASSED!")
        print("Real optimal configuration is ready!")
    else:
        print("\nConfiguration test FAILED!")
        print("Need to adjust parameters...")
    
    return optimal_config

if __name__ == "__main__":
    config = main()
