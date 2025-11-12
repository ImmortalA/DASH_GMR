import os
import pickle
from pathlib import Path

import joblib
import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# these paths are from the OMOMO dataset (relative to the repo root)
motion_path1 = REPO_ROOT / "motion_data" / "omomo_data" / "train_diffusion_manip_seq_joints24.p"
motion_path2 = REPO_ROOT / "motion_data" / "omomo_data" / "test_diffusion_manip_seq_joints24.p"

if not motion_path1.exists() or not motion_path2.exists():
    raise FileNotFoundError(
        "OMOMO dataset files not found. Expected paths:\n"
        f"  {motion_path1}\n"
        f"  {motion_path2}\n"
        "Please download/extract the dataset under motion_data/omomo_data/."
    )

all_motion_data1 = joblib.load(motion_path1)
all_motion_data2 = joblib.load(motion_path2)

# save as individual files
target_dir = REPO_ROOT / "motion_data" / "OMOMO_smplx"
os.makedirs(target_dir, exist_ok=True)
for motion_data in [all_motion_data1, all_motion_data2]:
    for data_name in motion_data.keys():
        
        smpl_data = motion_data[data_name]
        seq_name = smpl_data['seq_name']
        # save as npz
        num_frames = smpl_data["pose_body"].shape[0]
        mocap_frame_rate = 30
        poses = np.concatenate([smpl_data["pose_body"], 
                                np.zeros((num_frames, 102))],
                                axis=1)
        smpl_data["poses"] = poses
        smpl_data["mocap_frame_rate"] = np.array(mocap_frame_rate)
        # use pickle to save
        with open(f"{target_dir}/{seq_name}.pkl", "wb") as f:
            pickle.dump(smpl_data, f)
        print(f"saved {seq_name}")