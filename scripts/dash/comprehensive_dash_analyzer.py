#!/usr/bin/env python3
"""
Comprehensive DASH Robot Analyzer
Reads actual URDF, analyzes motion data, and creates properly fitted configuration
"""

import json
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict

class ComprehensiveDASHAnalyzer:
    def __init__(self):
        self.urdf_path = "assets/DASH_URDF/robot.urdf"
        self.mjmodel_path = "assets/DASH_URDF/mjmodel.xml"
        
    def analyze_urdf_comprehensive(self):
        """Comprehensive analysis of DASH URDF structure"""
        print("Comprehensive DASH URDF analysis...")
        
        tree = ET.parse(self.urdf_path)
        root = tree.getroot()
        
        # Extract all joint information
        joints = {}
        joint_limits = {}
        joint_origins = {}
        
        for joint in root.findall('joint'):
            joint_name = joint.get('name')
            joint_type = joint.get('type')
            
            # Get joint origin (position and orientation)
            origin = joint.find('origin')
            if origin is not None:
                xyz = [float(x) for x in origin.get('xyz', '0 0 0').split()]
                rpy = [float(x) for x in origin.get('rpy', '0 0 0').split()]
                joint_origins[joint_name] = {'xyz': xyz, 'rpy': rpy}
            
            # Get joint limits
            limits = joint.find('limit')
            if limits is not None:
                effort = float(limits.get('effort', 10))
                velocity = float(limits.get('velocity', 10))
                lower = float(limits.get('lower', -np.pi))
                upper = float(limits.get('upper', np.pi))
                
                joint_limits[joint_name] = {
                    'effort': effort,
                    'velocity': velocity,
                    'lower': lower,
                    'upper': upper,
                    'range': upper - lower,
                    'range_deg': np.degrees(upper - lower)
                }
            
            # Get parent and child links
            parent = joint.find('parent')
            child = joint.find('child')
            
            joints[joint_name] = {
                'type': joint_type,
                'parent': parent.get('link') if parent is not None else None,
                'child': child.get('link') if child is not None else None,
                'origin': joint_origins.get(joint_name, {'xyz': [0,0,0], 'rpy': [0,0,0]})
            }
        
        # Extract link information
        links = {}
        link_masses = {}
        link_inertias = {}
        
        for link in root.findall('link'):
            link_name = link.get('name')
            
            # Get inertial properties
            inertial = link.find('inertial')
            if inertial is not None:
                # Mass
                mass_elem = inertial.find('mass')
                mass = float(mass_elem.get('value', 0)) if mass_elem is not None else 0
                link_masses[link_name] = mass
                
                # Inertia
                inertia_elem = inertial.find('inertia')
                if inertia_elem is not None:
                    inertia = {
                        'ixx': float(inertia_elem.get('ixx', 0)),
                        'iyy': float(inertia_elem.get('iyy', 0)),
                        'izz': float(inertia_elem.get('izz', 0)),
                        'ixy': float(inertia_elem.get('ixy', 0)),
                        'ixz': float(inertia_elem.get('ixz', 0)),
                        'iyz': float(inertia_elem.get('iyz', 0))
                    }
                    link_inertias[link_name] = inertia
            
            links[link_name] = {
                'mass': link_masses.get(link_name, 0),
                'inertia': link_inertias.get(link_name, {})
            }
        
        print(f"Found {len(joints)} joints, {len(links)} links")
        print(f"Joint limits: {len(joint_limits)}")
        print(f"Link masses: {len(link_masses)}")
        
        return {
            'joints': joints,
            'links': links,
            'joint_limits': joint_limits,
            'link_masses': link_masses,
            'link_inertias': link_inertias,
            'joint_origins': joint_origins
        }
    
    def analyze_motion_data_comprehensive(self, motion_files):
        """Comprehensive analysis of motion data"""
        print("Comprehensive motion data analysis...")
        
        all_analyses = []
        
        for motion_file in motion_files:
            if not Path(motion_file).exists():
                print(f"Motion file not found: {motion_file}")
                continue
                
            try:
                data = np.load(motion_file, allow_pickle=True)
                
                # Extract motion data
                trans = data['trans']  # Root translation
                root_orient = data['root_orient']  # Root orientation
                pose_body = data['pose_body']  # Body pose (63 DOF)
                
                # Calculate motion statistics
                analysis = {
                    'file': motion_file,
                    'frames': len(trans),
                    'duration': len(trans) / data['mocap_frame_rate'],
                    'fps': data['mocap_frame_rate'],
                    
                    # Translation analysis
                    'trans_stats': {
                        'mean': np.mean(trans, axis=0),
                        'std': np.std(trans, axis=0),
                        'min': np.min(trans, axis=0),
                        'max': np.max(trans, axis=0),
                        'range': np.max(trans, axis=0) - np.min(trans, axis=0)
                    },
                    
                    # Root orientation analysis
                    'root_orient_stats': {
                        'mean': np.mean(root_orient, axis=0),
                        'std': np.std(root_orient, axis=0),
                        'min': np.min(root_orient, axis=0),
                        'max': np.max(root_orient, axis=0),
                        'range': np.max(root_orient, axis=0) - np.min(root_orient, axis=0)
                    },
                    
                    # Body pose analysis
                    'pose_body_stats': {
                        'mean': np.mean(pose_body, axis=0),
                        'std': np.std(pose_body, axis=0),
                        'min': np.min(pose_body, axis=0),
                        'max': np.max(pose_body, axis=0),
                        'range': np.max(pose_body, axis=0) - np.min(pose_body, axis=0)
                    },
                    
                    # Motion complexity metrics
                    'complexity': {
                        'translation_variance': np.var(trans),
                        'orientation_variance': np.var(root_orient),
                        'pose_variance': np.var(pose_body),
                        'overall_variance': (np.var(trans) + np.var(root_orient) + np.var(pose_body)) / 3,
                        'motion_range': np.linalg.norm(np.max(trans, axis=0) - np.min(trans, axis=0)),
                        'pose_range': np.linalg.norm(np.max(pose_body, axis=0) - np.min(pose_body, axis=0))
                    }
                }
                
                all_analyses.append(analysis)
                print(f"Analyzed {motion_file}: {analysis['frames']} frames, complexity: {analysis['complexity']['overall_variance']:.4f}")
                
            except Exception as e:
                print(f"Error analyzing {motion_file}: {e}")
        
        return all_analyses
    
    def calculate_optimal_scale_factors(self, motion_analyses):
        """Calculate optimal scale factors based on motion analysis"""
        print("Calculating optimal scale factors...")
        
        if not motion_analyses:
            # Default scale factors if no motion data
            return {
                'pelvis': 0.7, 'spine1': 0.7, 'spine2': 0.7, 'spine3': 0.7,
                'neck': 0.6, 'head': 0.6,
                'left_hip': 0.7, 'right_hip': 0.7,
                'left_knee': 0.7, 'right_knee': 0.7,
                'left_ankle': 0.6, 'right_ankle': 0.6,
                'left_foot': 0.7, 'right_foot': 0.7,
                'left_shoulder': 0.6, 'right_shoulder': 0.6,
                'left_elbow': 0.6, 'right_elbow': 0.6,
                'left_wrist': 0.5, 'right_wrist': 0.5
            }
        
        # Calculate average motion characteristics
        avg_complexity = np.mean([a['complexity']['overall_variance'] for a in motion_analyses])
        avg_motion_range = np.mean([a['complexity']['motion_range'] for a in motion_analyses])
        avg_pose_range = np.mean([a['complexity']['pose_range'] for a in motion_analyses])
        
        print(f"Average complexity: {avg_complexity:.4f}")
        print(f"Average motion range: {avg_motion_range:.4f}")
        print(f"Average pose range: {avg_pose_range:.4f}")
        
        # Base scale factor based on motion characteristics
        base_scale = 0.5 + min(avg_complexity * 0.5, 0.3)  # Scale between 0.5-0.8
        
        # Different scales for different body parts based on importance
        scale_factors = {
            # Core body (highest scale for stability)
            'pelvis': base_scale * 1.2,
            'spine1': base_scale * 1.2,
            'spine2': base_scale * 1.2,
            'spine3': base_scale * 1.2,
            
            # Head/neck (medium scale)
            'neck': base_scale * 1.0,
            'head': base_scale * 1.0,
            
            # Legs (high scale for locomotion)
            'left_hip': base_scale * 1.1,
            'right_hip': base_scale * 1.1,
            'left_knee': base_scale * 1.1,
            'right_knee': base_scale * 1.1,
            'left_ankle': base_scale * 1.0,
            'right_ankle': base_scale * 1.0,
            
            # Feet (highest scale for balance)
            'left_foot': base_scale * 1.2,
            'right_foot': base_scale * 1.2,
            
            # Arms (medium scale for manipulation)
            'left_shoulder': base_scale * 1.0,
            'right_shoulder': base_scale * 1.0,
            'left_elbow': base_scale * 1.0,
            'right_elbow': base_scale * 1.0,
            
            # Hands (lower scale for fine control)
            'left_wrist': base_scale * 0.9,
            'right_wrist': base_scale * 0.9
        }
        
        return scale_factors
    
    def calculate_optimal_weights(self, urdf_data, motion_analyses):
        """Calculate optimal IK weights based on URDF and motion analysis"""
        print("Calculating optimal IK weights...")
        
        # Get joint limits for weight calculation
        joint_limits = urdf_data['joint_limits']
        
        # Base weights
        base_pos_weight = 100
        base_rot_weight = 20
        
        # Weight adjustments based on joint characteristics and motion analysis
        weight_configs = {}
        
        # Joint mapping from robot to human
        joint_mapping = {
            'torso': 'pelvis',
            'r_foot': 'right_foot',
            'l_foot': 'left_foot',
            'r_upper_leg': 'right_knee',
            'l_upper_leg': 'left_knee',
            'r_hip': 'right_hip',
            'l_hip': 'left_hip',
            'r_upper_arm': 'right_elbow',
            'l_upper_arm': 'left_elbow',
            'r_prox_shoulder': 'right_shoulder',
            'l_prox_shoulder': 'left_shoulder',
            'r_lower_arm': 'right_wrist',
            'l_lower_arm': 'left_wrist'
        }
        
        for robot_joint, human_joint in joint_mapping.items():
            # Determine joint importance based on robot structure
            if robot_joint in ['torso', 'r_foot', 'l_foot']:
                # Critical joints for stability
                pos_weight = base_pos_weight * 3.0
                rot_weight = base_rot_weight * 2.5
                importance = 'critical'
            elif robot_joint in ['r_upper_leg', 'l_upper_leg']:
                # High importance for locomotion
                pos_weight = base_pos_weight * 2.0
                rot_weight = base_rot_weight * 2.0
                importance = 'high'
            elif robot_joint in ['r_hip', 'l_hip']:
                # Medium-high importance
                pos_weight = base_pos_weight * 1.5
                rot_weight = base_rot_weight * 1.5
                importance = 'medium-high'
            elif robot_joint in ['r_upper_arm', 'l_upper_arm']:
                # Medium importance for manipulation
                pos_weight = base_pos_weight * 1.2
                rot_weight = base_rot_weight * 1.2
                importance = 'medium'
            elif robot_joint in ['r_prox_shoulder', 'l_prox_shoulder']:
                # Lower importance
                pos_weight = base_pos_weight * 1.0
                rot_weight = base_rot_weight * 1.0
                importance = 'low'
            else:  # r_lower_arm, l_lower_arm
                # Lowest importance for fine manipulation
                pos_weight = base_pos_weight * 0.8
                rot_weight = base_rot_weight * 0.8
                importance = 'lowest'
            
            # Adjust based on motion complexity if available
            if motion_analyses:
                avg_complexity = np.mean([a['complexity']['overall_variance'] for a in motion_analyses])
                # Higher complexity motions need more conservative weights
                complexity_factor = 1.0 + min(avg_complexity * 0.5, 0.5)
                pos_weight *= complexity_factor
                rot_weight *= complexity_factor
            
            weight_configs[robot_joint] = {
                'human_joint': human_joint,
                'position_weight': int(pos_weight),
                'rotation_weight': int(rot_weight),
                'importance': importance
            }
        
        return weight_configs
    
    def create_comprehensive_config(self, urdf_data, motion_analyses):
        """Create comprehensive optimal configuration"""
        print("Creating comprehensive optimal configuration...")
        
        # Calculate optimal parameters
        scale_factors = self.calculate_optimal_scale_factors(motion_analyses)
        weight_configs = self.calculate_optimal_weights(urdf_data, motion_analyses)
        
        # Create configuration
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
        
        # Generate IK tables
        for robot_joint, weight_config in weight_configs.items():
            # Table 1 (primary) - higher weights
            config['ik_match_table1'][robot_joint] = [
                weight_config['human_joint'],
                weight_config['position_weight'],
                weight_config['rotation_weight'],
                [0.0, 0.0, 0.0],
                [0.7, -0.3, -0.3, -0.3]  # Conservative rotation offsets
            ]
            
            # Table 2 (secondary) - reduced weights for fine-tuning
            config['ik_match_table2'][robot_joint] = [
                weight_config['human_joint'],
                int(weight_config['position_weight'] * 0.6),
                int(weight_config['rotation_weight'] * 0.6),
                [0.0, 0.0, 0.0],
                [0.7, -0.3, -0.3, -0.3]
            ]
        
        return config
    
    def save_analysis_report(self, urdf_data, motion_analyses, config, output_file="dash_comprehensive_analysis.json"):
        """Save comprehensive analysis report"""
        report = {
            'urdf_analysis': {
                'joint_count': len(urdf_data['joints']),
                'link_count': len(urdf_data['links']),
                'joint_limits': urdf_data['joint_limits'],
                'link_masses': urdf_data['link_masses']
            },
            'motion_analysis': motion_analyses,
            'configuration': config,
            'timestamp': str(np.datetime64('now'))
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Comprehensive analysis report saved to: {output_file}")

def main():
    analyzer = ComprehensiveDASHAnalyzer()
    
    # Analyze URDF
    urdf_data = analyzer.analyze_urdf_comprehensive()
    
    # Analyze motion data
    motion_files = [
        "motion_data/ACCAD/Male2General_c3d/A1-_Stand_stageii.npz",
        "motion_data/ACCAD/Male2General_c3d/A5-_Pick_up_box_stageii.npz",
        "motion_data/ACCAD/s007/QkWalk1_stageii.npz"
    ]
    
    motion_analyses = analyzer.analyze_motion_data_comprehensive(motion_files)
    
    # Create comprehensive configuration
    config = analyzer.create_comprehensive_config(urdf_data, motion_analyses)
    
    # Save configuration
    with open("smplx_to_dash_comprehensive.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n=== COMPREHENSIVE DASH CONFIGURATION ===")
    print("Configuration saved to: smplx_to_dash_comprehensive.json")
    
    # Print summary
    scale_factors = config['human_scale_table']
    print(f"Scale factors range: {min(scale_factors.values()):.2f} - {max(scale_factors.values()):.2f}")
    
    pos_weights = [entry[1] for entry in config['ik_match_table1'].values()]
    rot_weights = [entry[2] for entry in config['ik_match_table1'].values()]
    
    print(f"Position weights range: {min(pos_weights)} - {max(pos_weights)}")
    print(f"Rotation weights range: {min(rot_weights)} - {max(rot_weights)}")
    
    # Save analysis report
    analyzer.save_analysis_report(urdf_data, motion_analyses, config)
    
    return config

if __name__ == "__main__":
    config = main()
