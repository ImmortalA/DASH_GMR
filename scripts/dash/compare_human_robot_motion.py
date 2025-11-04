#!/usr/bin/env python3
"""
Compare Human Motion (NPZ) with Robot Motion (PKL)
This script helps you visualize and compare the original human motion data
with the retargeted robot motion to verify accuracy.
"""

import numpy as np
import pickle
import argparse
import sys
import os
from pathlib import Path

def load_npz_motion(npz_path):
    """Load human motion data from NPZ file"""
    try:
        data = np.load(npz_path)
        print(f"NPZ file contents: {list(data.keys())}")
        
        # Common keys in SMPLX data
        if 'trans' in data:
            trans = data['trans']  # Global translation
            print(f"Translation shape: {trans.shape}")
        else:
            trans = None
            
        if 'global_orient' in data:
            global_orient = data['global_orient']  # Global orientation
            print(f"Global orientation shape: {global_orient.shape}")
        else:
            global_orient = None
            
        if 'body_pose' in data:
            body_pose = data['body_pose']  # Body pose parameters
            print(f"Body pose shape: {body_pose.shape}")
        else:
            body_pose = None
            
        if 'betas' in data:
            betas = data['betas']  # Shape parameters
            print(f"Shape parameters shape: {betas.shape}")
        else:
            betas = None
            
        return {
            'trans': trans,
            'global_orient': global_orient,
            'body_pose': body_pose,
            'betas': betas,
            'frame_count': len(trans) if trans is not None else 0
        }
    except Exception as e:
        print(f"Error loading NPZ file: {e}")
        return None

def load_pkl_motion(pkl_path):
    """Load robot motion data from PKL file"""
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        print(f"PKL file contents: {list(data.keys())}")
        
        # Handle different PKL formats
        if 'qpos' in data:
            qpos = data['qpos']  # Robot joint positions
            print(f"Robot joint positions shape: {qpos.shape}")
        elif 'dof_pos' in data:
            qpos = data['dof_pos']  # Robot DOF positions
            print(f"Robot DOF positions shape: {qpos.shape}")
        else:
            qpos = None
            
        if 'qvel' in data:
            qvel = data['qvel']  # Robot joint velocities
            print(f"Robot joint velocities shape: {qvel.shape}")
        else:
            qvel = None
            
        # Get root position and rotation
        root_pos = data.get('root_pos', None)
        root_rot = data.get('root_rot', None)
        
        if root_pos is not None:
            print(f"Root position shape: {root_pos.shape}")
        if root_rot is not None:
            print(f"Root rotation shape: {root_rot.shape}")
            
        return {
            'qpos': qpos,
            'qvel': qvel,
            'root_pos': root_pos,
            'root_rot': root_rot,
            'frame_count': len(qpos) if qpos is not None else 0
        }
    except Exception as e:
        print(f"Error loading PKL file: {e}")
        return None

def analyze_motion_data(human_data, robot_data):
    """Analyze and compare motion data"""
    print("\n" + "="*60)
    print("MOTION DATA ANALYSIS")
    print("="*60)
    
    if human_data is None or robot_data is None:
        print("Cannot analyze - missing data")
        return
    
    print(f"Human motion frames: {human_data['frame_count']}")
    print(f"Robot motion frames: {robot_data['frame_count']}")
    
    if human_data['frame_count'] != robot_data['frame_count']:
        print("Frame count mismatch - motion may be truncated or padded")
    
    # Analyze human motion
    if human_data['trans'] is not None:
        trans_range = np.ptp(human_data['trans'], axis=0)  # Peak-to-peak range
        print(f"\nHuman motion range:")
        print(f"   X: {trans_range[0]:.3f}m")
        print(f"   Y: {trans_range[1]:.3f}m") 
        print(f"   Z: {trans_range[2]:.3f}m")
        
        # Check for significant movement
        total_movement = np.linalg.norm(trans_range)
        if total_movement > 0.5:
            print(f"   High movement detected: {total_movement:.3f}m total range")
        elif total_movement > 0.1:
            print(f"   Moderate movement: {total_movement:.3f}m total range")
        else:
            print(f"   Low movement: {total_movement:.3f}m total range")
    
    # Analyze robot motion
    if robot_data['qpos'] is not None:
        qpos_range = np.ptp(robot_data['qpos'], axis=0)
        print(f"\nRobot joint ranges:")
        print(f"   Min joint range: {np.min(qpos_range):.3f} rad")
        print(f"   Max joint range: {np.max(qpos_range):.3f} rad")
        print(f"   Average joint range: {np.mean(qpos_range):.3f} rad")
        
        # Check for reasonable joint limits
        reasonable_joints = np.sum((qpos_range > 0.1) & (qpos_range < 3.0))
        total_joints = len(qpos_range)
        print(f"   Reasonable joint movement: {reasonable_joints}/{total_joints} joints")
    
    # Analyze robot root motion
    if robot_data['root_pos'] is not None:
        root_pos_range = np.ptp(robot_data['root_pos'], axis=0)
        print(f"\nRobot root position range:")
        print(f"   X: {root_pos_range[0]:.3f}m")
        print(f"   Y: {root_pos_range[1]:.3f}m")
        print(f"   Z: {root_pos_range[2]:.3f}m")
        
        # Compare with human motion range
        if human_data['trans'] is not None:
            human_trans_range = np.ptp(human_data['trans'], axis=0)
            print(f"\nMotion range comparison:")
            print(f"   Human X range: {human_trans_range[0]:.3f}m")
            print(f"   Robot X range: {root_pos_range[0]:.3f}m")
            print(f"   Human Y range: {human_trans_range[1]:.3f}m")
            print(f"   Robot Y range: {root_pos_range[1]:.3f}m")
            print(f"   Human Z range: {human_trans_range[2]:.3f}m")
            print(f"   Robot Z range: {root_pos_range[2]:.3f}m")
            
            # Calculate scaling factor
            human_total = np.linalg.norm(human_trans_range)
            robot_total = np.linalg.norm(root_pos_range)
            if human_total > 0:
                scale_factor = robot_total / human_total
                print(f"   Estimated scale factor: {scale_factor:.3f}")
                if 0.5 < scale_factor < 2.0:
                    print("   Scale factor looks reasonable")
                else:
                    print("   Scale factor may need adjustment")

def create_comparison_script(human_npz, robot_pkl):
    """Create a script to visualize both motions side by side"""
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated comparison script for:
Human: {human_npz}
Robot: {robot_pkl}
"""

import numpy as np
import pickle
import matplotlib.pyplot as plt

def plot_motion_comparison():
    # Load human motion
    human_data = np.load("{human_npz}")
    if 'trans' in human_data:
        human_trans = human_data['trans']
    else:
        print("No translation data in human motion")
        return
    
    # Load robot motion  
    with open("{robot_pkl}", 'rb') as f:
        robot_data = pickle.load(f)
    robot_qpos = robot_data['qpos']
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Human translation over time
    axes[0,0].plot(human_trans[:, 0], label='X', alpha=0.7)
    axes[0,0].plot(human_trans[:, 1], label='Y', alpha=0.7)
    axes[0,0].plot(human_trans[:, 2], label='Z', alpha=0.7)
    axes[0,0].set_title('Human Motion - Translation')
    axes[0,0].set_xlabel('Frame')
    axes[0,0].set_ylabel('Position (m)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Robot joint positions over time (first 6 DOF - floating base)
    axes[0,1].plot(robot_qpos[:, 0:6])
    axes[0,1].set_title('Robot Motion - Floating Base')
    axes[0,1].set_xlabel('Frame')
    axes[0,1].set_ylabel('Position (m)')
    axes[0,1].grid(True)
    
    # Robot leg joints
    axes[1,0].plot(robot_qpos[:, 6:16])  # Leg joints
    axes[1,0].set_title('Robot Motion - Leg Joints')
    axes[1,0].set_xlabel('Frame')
    axes[1,0].set_ylabel('Joint Angle (rad)')
    axes[1,0].grid(True)
    
    # Robot arm joints
    axes[1,1].plot(robot_qpos[:, 16:24])  # Arm joints
    axes[1,1].set_title('Robot Motion - Arm Joints')
    axes[1,1].set_xlabel('Frame')
    axes[1,1].set_ylabel('Joint Angle (rad)')
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.savefig('motion_comparison.png', dpi=150, bbox_inches='tight')
    print("Comparison plot saved as 'motion_comparison.png'")
    plt.show()

if __name__ == "__main__":
    plot_motion_comparison()
'''
    
    with open('compare_motions.py', 'w') as f:
        f.write(script_content)
    
    print(f"\nCreated comparison script: compare_motions.py")
    print("   Run with: python compare_motions.py")

def main():
    parser = argparse.ArgumentParser(description='Compare human and robot motion data')
    parser.add_argument('--human_npz', required=True, help='Path to human motion NPZ file')
    parser.add_argument('--robot_pkl', required=True, help='Path to robot motion PKL file')
    parser.add_argument('--create_plot', action='store_true', help='Create comparison plot script')
    
    args = parser.parse_args()
    
    print("COMPARING HUMAN AND ROBOT MOTION")
    print("="*50)
    
    # Load data
    print(f"\nLoading human motion: {args.human_npz}")
    human_data = load_npz_motion(args.human_npz)
    
    print(f"\nLoading robot motion: {args.robot_pkl}")
    robot_data = load_pkl_motion(args.robot_pkl)
    
    # Analyze data
    analyze_motion_data(human_data, robot_data)
    
    # Create comparison script if requested
    if args.create_plot:
        create_comparison_script(args.human_npz, args.robot_pkl)
    
    print("\nAnalysis complete!")
    print("\nTips for verification:")
    print("   1. Check if motion ranges are reasonable")
    print("   2. Verify frame counts match")
    print("   3. Look for smooth motion transitions")
    print("   4. Compare human movement with robot joint changes")

if __name__ == "__main__":
    main()
