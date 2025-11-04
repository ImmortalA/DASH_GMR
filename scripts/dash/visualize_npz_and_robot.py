#!/usr/bin/env python3
"""
Visualize Original Human Motion (NPZ) and Compare with Robot Motion (PKL)
This script loads an NPZ file and a PKL file and visualizes them together
so you can compare the original human postures with the robot's retargeted motion.
"""

import argparse
import pathlib
import numpy as np
import pickle

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting import RobotMotionViewer
from general_motion_retargeting import load_robot_motion
from general_motion_retargeting.utils.smpl import load_smplx_file, get_smplx_data_offline_fast

HERE = pathlib.Path(__file__).parent

def main():
    parser = argparse.ArgumentParser(
        description="Visualize NPZ human motion and compare with robot PKL motion"
    )
    parser.add_argument(
        "--npz_file",
        type=str,
        required=True,
        help="Path to the original NPZ motion file (human motion)"
    )
    parser.add_argument(
        "--pkl_file",
        type=str,
        required=True,
        help="Path to the robot motion PKL file to compare"
    )
    parser.add_argument(
        "--robot",
        type=str,
        default="dash",
        choices=["unitree_g1", "unitree_g1_with_hands", "unitree_h1", "unitree_h1_2",
                 "booster_t1", "booster_t1_29dof","stanford_toddy", "fourier_n1", 
                "engineai_pm01", "kuavo_s45", "hightorque_hi", "galaxea_r1pro", 
                "berkeley_humanoid_lite", "booster_k1", "pnd_adam_lite", "openloong", 
                "tienkung", "dash"],
        help="Robot type"
    )
    parser.add_argument(
        "--human_offset",
        type=float,
        nargs=3,
        default=[0.0, 1.0, 0.0],
        help="Offset for human motion visualization (x, y, z) to separate from robot"
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Loop the motion"
    )
    parser.add_argument(
        "--record_video",
        action="store_true",
        help="Record video of the visualization"
    )
    parser.add_argument(
        "--video_path",
        type=str,
        default="videos/npz_robot_comparison.mp4",
        help="Path to save video"
    )
    parser.add_argument(
        "--show_human_labels",
        action="store_true",
        help="Show human body part names"
    )
    
    args = parser.parse_args()
    
    # Load SMPL-X models
    SMPLX_FOLDER = HERE / ".." / ".." / "assets" / "body_models" / "models_smplx_v1_1" / "models"
    
    print(f"Loading human motion from: {args.npz_file}")
    smplx_data, body_model, smplx_output, actual_human_height = load_smplx_file(
        args.npz_file, SMPLX_FOLDER
    )
    
    # Process SMPL-X data to get frame-by-frame motion
    print("Processing human motion data...")
    tgt_fps = 30
    smplx_data_frames, aligned_fps = get_smplx_data_offline_fast(
        smplx_data, body_model, smplx_output, tgt_fps=tgt_fps
    )
    print(f"Loaded {len(smplx_data_frames)} frames of human motion")
    
    # Load robot motion
    print(f"Loading robot motion from: {args.pkl_file}")
    robot_motion_data, robot_fps, robot_root_pos, robot_root_rot, robot_dof_pos, \
        robot_local_body_pos, robot_link_body_list = load_robot_motion(args.pkl_file)
    print(f"Loaded {len(robot_root_pos)} frames of robot motion")
    
    # Initialize retargeting system to get scaled human data
    print("Initializing retargeting system...")
    retarget = GMR(
        actual_human_height=actual_human_height,
        src_human="smplx",
        tgt_robot=args.robot,
    )
    
    # Initialize viewer
    print("Initializing viewer...")
    robot_motion_viewer = RobotMotionViewer(
        robot_type=args.robot,
        motion_fps=aligned_fps,
        transparent_robot=0,
        record_video=args.record_video,
        video_path=args.video_path,
    )
    
    print("\n" + "="*60)
    print("Visualization Controls:")
    print("  - Close window or press Ctrl+C to exit")
    print("  - Human motion shown as colored frames/points")
    print("  - Robot motion shown as full robot model")
    print("="*60 + "\n")
    
    # Synchronize frame counts
    num_frames = min(len(smplx_data_frames), len(robot_root_pos))
    print(f"Visualizing {num_frames} frames...")
    
    human_pos_offset = np.array(args.human_offset)
    
    frame_idx = 0
    try:
        while True:
            # Get human motion data for this frame
            human_frame = smplx_data_frames[frame_idx]
            
            # Retarget to get scaled human data (for visualization)
            _ = retarget.retarget(human_frame)
            scaled_human_data = retarget.scaled_human_data
            
            # Get robot motion data for this frame
            robot_root_p = robot_root_pos[frame_idx]
            robot_root_r = robot_root_rot[frame_idx]
            robot_dof_p = robot_dof_pos[frame_idx]
            
            # Visualize both
            robot_motion_viewer.step(
                root_pos=robot_root_p,
                root_rot=robot_root_r,
                dof_pos=robot_dof_p,
                human_motion_data=scaled_human_data,
                human_pos_offset=human_pos_offset,
                show_human_body_name=args.show_human_labels,
                rate_limit=True,
                follow_camera=True,
            )
            
            if args.loop:
                frame_idx = (frame_idx + 1) % num_frames
            else:
                frame_idx += 1
                if frame_idx >= num_frames:
                    print(f"\nReached end of motion ({num_frames} frames)")
                    break
                    
    except KeyboardInterrupt:
        print("\nVisualization interrupted by user")
    
    robot_motion_viewer.close()
    print("Visualization closed")

if __name__ == "__main__":
    main()

