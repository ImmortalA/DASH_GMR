#!/usr/bin/env python3
"""
DASH Robot Analysis Tool
Analyzes DASH robot URDF structure, kinematics, and motion characteristics
"""

import json
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict

class DASHAnalyzer:
    def __init__(self, urdf_path="assets/DASH_URDF/robot.urdf"):
        self.urdf_path = urdf_path
        self.robot_data = {}
        self.joint_limits = {}
        self.link_masses = {}
        self.joint_hierarchy = {}
        
    def analyze_urdf(self):
        """Analyze DASH robot URDF structure"""
        print("Analyzing DASH robot URDF structure...")
        
        try:
            tree = ET.parse(self.urdf_path)
            root = tree.getroot()
            
            # Extract joint information
            joints = {}
            for joint in root.findall('joint'):
                joint_name = joint.get('name')
                joint_type = joint.get('type')
                
                # Get joint limits
                limits = joint.find('limit')
                if limits is not None:
                    lower = float(limits.get('lower', -np.pi))
                    upper = float(limits.get('upper', np.pi))
                    effort = float(limits.get('effort', 100))
                    velocity = float(limits.get('velocity', 10))
                    
                    self.joint_limits[joint_name] = {
                        'lower': lower,
                        'upper': upper,
                        'effort': effort,
                        'velocity': velocity,
                        'range': upper - lower
                    }
                
                # Get joint hierarchy
                parent = joint.find('parent')
                child = joint.find('child')
                if parent is not None and child is not None:
                    self.joint_hierarchy[child.get('link')] = parent.get('link')
                
                joints[joint_name] = {
                    'type': joint_type,
                    'parent': parent.get('link') if parent is not None else None,
                    'child': child.get('link') if child is not None else None
                }
            
            # Extract link information
            links = {}
            for link in root.findall('link'):
                link_name = link.get('name')
                
                # Get mass and inertia
                inertial = link.find('inertial')
                if inertial is not None:
                    mass_elem = inertial.find('mass')
                    mass = float(mass_elem.get('value', 0)) if mass_elem is not None else 0
                    self.link_masses[link_name] = mass
                
                links[link_name] = {
                    'mass': self.link_masses.get(link_name, 0)
                }
            
            self.robot_data = {
                'joints': joints,
                'links': links,
                'joint_limits': self.joint_limits,
                'link_masses': self.link_masses
            }
            
            print(f"Found {len(joints)} joints and {len(links)} links")
            return True
            
        except Exception as e:
            print(f"Error analyzing URDF: {e}")
            return False
    
    def analyze_joint_characteristics(self):
        """Analyze joint characteristics and ranges"""
        print("\nAnalyzing joint characteristics...")
        
        joint_analysis = {}
        
        for joint_name, limits in self.joint_limits.items():
            range_deg = np.degrees(limits['range'])
            effort = limits['effort']
            velocity = limits['velocity']
            
            # Categorize joints
            if 'hip' in joint_name.lower():
                joint_type = 'hip'
            elif 'knee' in joint_name.lower():
                joint_type = 'knee'
            elif 'ankle' in joint_name.lower():
                joint_type = 'ankle'
            elif 'shoulder' in joint_name.lower():
                joint_type = 'shoulder'
            elif 'elbow' in joint_name.lower():
                joint_type = 'elbow'
            elif 'wrist' in joint_name.lower():
                joint_type = 'wrist'
            elif 'torso' in joint_name.lower():
                joint_type = 'torso'
            else:
                joint_type = 'other'
            
            joint_analysis[joint_name] = {
                'type': joint_type,
                'range_deg': range_deg,
                'effort': effort,
                'velocity': velocity,
                'flexibility': range_deg / 180.0,  # Normalized flexibility
                'power': effort * velocity  # Power rating
            }
        
        return joint_analysis
    
    def analyze_motion_data(self, motion_file):
        """Analyze human motion data characteristics"""
        print(f"\nAnalyzing motion data: {motion_file}")
        
        try:
            data = np.load(motion_file)
            
            motion_analysis = {
                'frames': len(data['trans']),
                'duration': len(data['trans']) / 30.0,  # Assuming 30 FPS
                'translation_range': {
                    'x': [np.min(data['trans'][:, 0]), np.max(data['trans'][:, 0])],
                    'y': [np.min(data['trans'][:, 1]), np.max(data['trans'][:, 1])],
                    'z': [np.min(data['trans'][:, 2]), np.max(data['trans'][:, 2])]
                },
                'pose_variance': np.var(data['body_pose'], axis=0),
                'global_orient_variance': np.var(data['global_orient'], axis=0)
            }
            
            # Calculate motion complexity
            pose_std = np.std(data['body_pose'])
            orient_std = np.std(data['global_orient'])
            trans_std = np.std(data['trans'])
            
            motion_analysis['complexity'] = {
                'pose': pose_std,
                'orientation': orient_std,
                'translation': trans_std,
                'overall': (pose_std + orient_std + trans_std) / 3
            }
            
            return motion_analysis
            
        except Exception as e:
            print(f"Error analyzing motion data: {e}")
            return None
    
    def generate_optimal_weights(self, joint_analysis, motion_analysis):
        """Generate optimal IK weights based on analysis"""
        print("\nGenerating optimal IK weights...")
        
        # Base weights
        base_position_weight = 100
        base_rotation_weight = 20
        
        # Weight adjustments based on joint characteristics
        position_weights = {}
        rotation_weights = {}
        
        for joint_name, analysis in joint_analysis.items():
            joint_type = analysis['type']
            flexibility = analysis['flexibility']
            power = analysis['power']
            
            # Position weights based on joint importance and flexibility
            if joint_type == 'torso':
                pos_weight = base_position_weight * 2.0  # High priority
                rot_weight = base_rotation_weight * 2.0
            elif joint_type in ['hip', 'knee']:
                pos_weight = base_position_weight * 1.5  # High priority for locomotion
                rot_weight = base_rotation_weight * 1.5
            elif joint_type == 'ankle':
                pos_weight = base_position_weight * 2.0  # Critical for balance
                rot_weight = base_rotation_weight * 2.5
            elif joint_type in ['shoulder', 'elbow']:
                pos_weight = base_position_weight * 1.2  # Medium priority
                rot_weight = base_rotation_weight * 1.2
            elif joint_type == 'wrist':
                pos_weight = base_position_weight * 1.0  # Lower priority
                rot_weight = base_rotation_weight * 1.0
            else:
                pos_weight = base_position_weight * 0.8
                rot_weight = base_rotation_weight * 0.8
            
            # Adjust based on flexibility
            pos_weight *= (0.5 + flexibility)
            rot_weight *= (0.5 + flexibility)
            
            position_weights[joint_name] = int(pos_weight)
            rotation_weights[joint_name] = int(rot_weight)
        
        return position_weights, rotation_weights
    
    def generate_optimal_scale_factors(self, motion_analysis):
        """Generate optimal scale factors based on motion analysis"""
        print("\nGenerating optimal scale factors...")
        
        # Base scale factors
        base_scale = 0.6
        
        # Adjust based on motion complexity
        if motion_analysis:
            complexity = motion_analysis['complexity']['overall']
            
            # Higher complexity motions need more conservative scaling
            if complexity > 0.5:
                scale_factor = base_scale * 0.8
            elif complexity > 0.3:
                scale_factor = base_scale * 0.9
            else:
                scale_factor = base_scale * 1.0
        else:
            scale_factor = base_scale
        
        # Different scales for different body parts
        scale_factors = {
            'pelvis': scale_factor * 1.2,
            'spine1': scale_factor * 1.2,
            'spine2': scale_factor * 1.2,
            'spine3': scale_factor * 1.2,
            'neck': scale_factor * 1.0,
            'head': scale_factor * 1.0,
            'left_hip': scale_factor * 1.2,
            'right_hip': scale_factor * 1.2,
            'left_knee': scale_factor * 1.2,
            'right_knee': scale_factor * 1.2,
            'left_ankle': scale_factor * 1.0,
            'right_ankle': scale_factor * 1.0,
            'left_foot': scale_factor * 1.2,
            'right_foot': scale_factor * 1.2,
            'left_shoulder': scale_factor * 1.0,
            'right_shoulder': scale_factor * 1.0,
            'left_elbow': scale_factor * 1.0,
            'right_elbow': scale_factor * 1.0,
            'left_wrist': scale_factor * 1.0,
            'right_wrist': scale_factor * 1.0
        }
        
        return scale_factors
    
    def generate_optimal_config(self, motion_files=None):
        """Generate optimal DASH configuration"""
        print("Generating optimal DASH configuration...")
        
        # Analyze robot structure
        if not self.analyze_urdf():
            return None
        
        # Analyze joint characteristics
        joint_analysis = self.analyze_joint_characteristics()
        
        # Analyze motion data if provided
        motion_analysis = None
        if motion_files:
            for motion_file in motion_files:
                if Path(motion_file).exists():
                    motion_analysis = self.analyze_motion_data(motion_file)
                    break
        
        # Generate optimal parameters
        position_weights, rotation_weights = self.generate_optimal_weights(joint_analysis, motion_analysis)
        scale_factors = self.generate_optimal_scale_factors(motion_analysis)
        
        # Create optimal configuration
        config = {
            "robot_root_name": "torso",
            "human_root_name": "pelvis",
            "ground_height": 0.0,
            "human_height_assumption": 1.8,
            "use_ik_match_table1": True,
            "use_ik_match_table2": True,
            "human_scale_table": scale_factors,
            "ik_match_table1": {},
            "ik_match_table2": {}
        }
        
        # Generate IK match tables
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
        
        for robot_joint, human_joint in joint_mapping.items():
            pos_weight = position_weights.get(robot_joint, 100)
            rot_weight = rotation_weights.get(robot_joint, 20)
            
            # Table 1 (primary)
            config["ik_match_table1"][robot_joint] = [
                human_joint,
                pos_weight,
                rot_weight,
                [0.0, 0.0, 0.0],
                [0.7, -0.3, -0.3, -0.3]
            ]
            
            # Table 2 (secondary) - reduced weights
            config["ik_match_table2"][robot_joint] = [
                human_joint,
                int(pos_weight * 0.7),
                int(rot_weight * 0.7),
                [0.0, 0.0, 0.0],
                [0.7, -0.3, -0.3, -0.3]
            ]
        
        return config
    
    def save_analysis_report(self, output_file="dash_analysis_report.json"):
        """Save analysis report"""
        report = {
            'robot_data': self.robot_data,
            'joint_analysis': self.analyze_joint_characteristics(),
            'timestamp': str(np.datetime64('now'))
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Analysis report saved to: {output_file}")

def main():
    analyzer = DASHAnalyzer()
    
    # Test motion files
    motion_files = [
        "motion_data/ACCAD/ACCAD/Male2General_c3d/A1-_Stand_stageii.npz",
        "motion_data/ACCAD/ACCAD/Male2General_c3d/A5-_Pick_up_box_stageii.npz",
        "motion_data/ACCAD/ACCAD/s007/QkWalk1_stageii.npz"
    ]
    
    # Generate optimal configuration
    optimal_config = analyzer.generate_optimal_config(motion_files)
    
    if optimal_config:
        # Save optimal configuration
        with open("smplx_to_dash_optimal.json", 'w') as f:
            json.dump(optimal_config, f, indent=2)
        
        print("\nOptimal configuration saved to: smplx_to_dash_optimal.json")
        
        # Save analysis report
        analyzer.save_analysis_report()
        
        # Print summary
        print("\n=== OPTIMAL CONFIGURATION SUMMARY ===")
        print(f"Scale factors range: {min(optimal_config['human_scale_table'].values()):.2f} - {max(optimal_config['human_scale_table'].values()):.2f}")
        
        pos_weights = [entry[1] for entry in optimal_config['ik_match_table1'].values()]
        rot_weights = [entry[2] for entry in optimal_config['ik_match_table1'].values()]
        
        print(f"Position weights range: {min(pos_weights)} - {max(pos_weights)}")
        print(f"Rotation weights range: {min(rot_weights)} - {max(rot_weights)}")
        
    else:
        print("Failed to generate optimal configuration")

if __name__ == "__main__":
    main()
