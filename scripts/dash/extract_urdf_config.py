#!/usr/bin/env python3
"""
Extract configuration values from DASH URDF file for smplx_to_dash.json
This script analyzes the URDF file to get body names, positions, and orientations
"""

import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation as R
import json

def extract_urdf_config(urdf_file):
    """Extract configuration values from URDF file"""
    
    print("🔍 Analyzing DASH URDF file...")
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    # Extract body information
    bodies = {}
    joints = {}
    
    def parse_body(body_elem, parent_pos=[0,0,0], parent_quat=[1,0,0,0]):
        """Recursively parse body elements"""
        body_name = body_elem.get('name')
        if body_name is None:
            return
            
        # Get position and orientation
        pos = [float(x) for x in body_elem.get('pos', '0 0 0').split()]
        quat = [float(x) for x in body_elem.get('quat', '1 0 0 0').split()]
        
        # Convert to global coordinates
        global_pos = np.array(parent_pos) + np.array(pos)
        
        # Handle quaternion conversion (URDF uses w,x,y,z, scipy uses x,y,z,w)
        if len(quat) == 4:
            quat_xyzw = [quat[1], quat[2], quat[3], quat[0]]  # Convert w,x,y,z to x,y,z,w
        else:
            quat_xyzw = [0, 0, 0, 1]  # Default identity quaternion
            
        if len(parent_quat) == 4:
            parent_quat_xyzw = [parent_quat[1], parent_quat[2], parent_quat[3], parent_quat[0]]
        else:
            parent_quat_xyzw = [0, 0, 0, 1]
            
        global_quat = R.from_quat(quat_xyzw) * R.from_quat(parent_quat_xyzw)
        
        bodies[body_name] = {
            'pos': global_pos.tolist(),
            'quat': global_quat.as_quat().tolist(),  # [x, y, z, w]
            'quat_wxyz': [global_quat.as_quat()[3]] + global_quat.as_quat()[:3].tolist()  # [w, x, y, z]
        }
        
        # Parse joints
        for joint in body_elem.findall('joint'):
            joint_name = joint.get('name')
            joint_type = joint.get('type')
            axis = [float(x) for x in joint.get('axis', '0 0 1').split()]
            range_vals = joint.get('range', '').split()
            
            joints[joint_name] = {
                'type': joint_type,
                'axis': axis,
                'range': range_vals
            }
        
        # Parse child bodies
        for child_body in body_elem.findall('body'):
            parse_body(child_body, global_pos, global_quat.as_quat())
    
    # Start parsing from worldbody
    worldbody = root.find('worldbody')
    if worldbody is not None:
        for body in worldbody.findall('body'):
            parse_body(body)
    
    return bodies, joints

def generate_ik_config(bodies, joints):
    """Generate IK configuration based on URDF analysis"""
    
    print("📊 Generating IK configuration...")
    
    # Robot body parts available in URDF
    robot_bodies = list(bodies.keys())
    print(f"Found {len(robot_bodies)} robot bodies: {robot_bodies}")
    
    # SMPLX human body parts (standard)
    human_bodies = [
        'pelvis', 'spine1', 'spine2', 'spine3', 'neck', 'head',
        'left_hip', 'right_hip', 'left_knee', 'right_knee',
        'left_ankle', 'right_ankle', 'left_foot', 'right_foot',
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist'
    ]
    
    # Calculate robot dimensions
    torso_pos = bodies.get('torso', {}).get('pos', [0, 0, 0])
    foot_positions = []
    
    for body_name in robot_bodies:
        if 'foot' in body_name.lower():
            foot_positions.append(bodies[body_name]['pos'])
    
    if foot_positions:
        robot_height = max([pos[2] for pos in foot_positions]) - torso_pos[2]
        print(f"Estimated robot height: {robot_height:.3f}m")
    else:
        robot_height = 1.0  # Default assumption
        print(f"Could not determine robot height, using default: {robot_height}m")
    
    # Calculate scale factors based on robot size
    human_height = 1.8  # Standard human height
    scale_factor = robot_height / human_height
    
    print(f"Scale factor (robot/human): {scale_factor:.3f}")
    
    # Generate configuration
    config = {
        "robot_root_name": "torso",
        "human_root_name": "pelvis",
        "ground_height": 0.0,
        "human_height_assumption": human_height,
        "use_ik_match_table1": True,
        "use_ik_match_table2": True,
        "human_scale_table": {},
        "ik_match_table1": {},
        "ik_match_table2": {}
    }
    
    # Generate scale table
    for human_body in human_bodies:
        if 'pelvis' in human_body or 'spine' in human_body:
            config["human_scale_table"][human_body] = round(scale_factor, 2)
        elif 'hip' in human_body or 'knee' in human_body or 'foot' in human_body:
            config["human_scale_table"][human_body] = round(scale_factor, 2)
        elif 'shoulder' in human_body or 'elbow' in human_body or 'wrist' in human_body:
            config["human_scale_table"][human_body] = round(scale_factor * 0.9, 2)  # Arms slightly smaller
        else:
            config["human_scale_table"][human_body] = round(scale_factor * 0.8, 2)  # Head/neck smaller
    
    # Generate IK mapping based on body names
    ik_mapping = {
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
    
    # Generate IK match tables
    for robot_body, human_body in ik_mapping.items():
        if robot_body in bodies:
            # Get position offset from URDF
            pos = bodies[robot_body]['pos']
            quat = bodies[robot_body]['quat_wxyz']  # [w, x, y, z]
            
            # Determine weights based on body part importance
            if 'foot' in robot_body:
                pos_weight, rot_weight = 100, 50  # Critical for balance
            elif 'torso' in robot_body:
                pos_weight, rot_weight = 100, 10  # Critical for stability
            elif 'hip' in robot_body:
                pos_weight, rot_weight = 0, 10    # Rotation only
            elif 'upper_leg' in robot_body:
                pos_weight, rot_weight = 0, 10    # Rotation only
            elif 'shoulder' in robot_body:
                pos_weight, rot_weight = 0, 10    # Rotation only
            elif 'upper_arm' in robot_body:
                pos_weight, rot_weight = 0, 10    # Rotation only
            elif 'lower_arm' in robot_body:
                pos_weight, rot_weight = 0, 10    # Rotation only
            else:
                pos_weight, rot_weight = 0, 10    # Default
            
            # Create IK entry
            ik_entry = [
                human_body,
                pos_weight,
                rot_weight,
                [0.0, 0.0, 0.0],  # Position offset (can be adjusted)
                quat  # Rotation offset from URDF
            ]
            
            config["ik_match_table1"][robot_body] = ik_entry
            config["ik_match_table2"][robot_body] = ik_entry  # Same for now
    
    return config

def main():
    urdf_file = "assets/DASH_URDF/mjmodel.xml"
    
    try:
        # Extract information from URDF
        bodies, joints = extract_urdf_config(urdf_file)
        
        print(f"\n📋 Found {len(bodies)} bodies and {len(joints)} joints")
        
        # Generate configuration
        config = generate_ik_config(bodies, joints)
        
        # Save configuration
        output_file = "../../configs/dash/smplx_to_dash_from_urdf.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"\n✅ Configuration saved to: {output_file}")
        
        # Print summary
        print(f"\n📊 Configuration Summary:")
        print(f"  - Robot height: {config['human_height_assumption'] * config['human_scale_table']['pelvis']:.2f}m")
        print(f"  - Scale factor: {config['human_scale_table']['pelvis']:.2f}")
        print(f"  - IK mappings: {len(config['ik_match_table1'])}")
        
        # Print body positions
        print(f"\n📍 Robot Body Positions:")
        for body_name, body_info in bodies.items():
            pos = body_info['pos']
            print(f"  {body_name}: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
        
        # Print joint information
        print(f"\n🔗 Joint Information:")
        for joint_name, joint_info in joints.items():
            if joint_info['type'] != 'free':
                print(f"  {joint_name}: {joint_info['type']}, axis: {joint_info['axis']}")
        
        print(f"\n🎯 Next steps:")
        print(f"  1. Review the generated configuration: {output_file}")
        print(f"  2. Compare with current config: general_motion_retargeting/ik_configs/smplx_to_dash.json")
        print(f"  3. Test the new configuration with your robot")
        print(f"  4. Adjust weights and offsets as needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
