#!/usr/bin/env python3
"""
Test multiple hybrid motion configurations for DASH robot
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_hybrid_motions(config_file=None, target_config="smplx_to_dash_hybrid.json"):
    """Test various motion types with hybrid IK configuration"""
    
    # If config_file is specified, copy it to the target location
    if config_file:
        import shutil
        target_path = f"general_motion_retargeting/ik_configs/{target_config}"
        shutil.copy(config_file, target_path)
        print(f"Using custom configuration: {config_file}")
        print(f"Copied to: {target_path}")
    
    # Motion files to test (you'll need to provide these)
    test_motions = [
        {
            "name": "standing",
            "file": "motion_data/ACCAD/ACCAD/Male2General_c3d/A1-_Stand_stageii.npz",
            "description": "Basic standing motion"
        },
        {
            "name": "walking", 
            "file": "motion_data/ACCAD/ACCAD/s007/QkWalk1_stageii.npz",
            "description": "Walking motion"
        },
        {
            "name": "pickup",
            "file": "motion_data/ACCAD/ACCAD/Male2General_c3d/A5-_Pick_up_box_stageii.npz", 
            "description": "Pick up box motion"
        },
        {
            "name": "advance",
            "file": "motion_data/ACCAD/ACCAD/MartialArtsWalksTurns_c3d/E4_-_quick_advance_stageii.npz",
            "description": "Quick advance motion"
        },
        {
            "name": "side_step",
            "file": "motion_data/ACCAD/ACCAD/MartialArtsWalksTurns_c3d/E9_-_side_step_left_stageii.npz",
            "description": "Side step motion"
        }
    ]
    
    # Output directory
    output_dir = Path("test_results/dash/hybrid_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Testing hybrid IK configuration with multiple motions...")
    print(f"Output directory: {output_dir}")
    print()
    
    results = []
    
    for motion in test_motions:
        print(f"Testing: {motion['name']} - {motion['description']}")
        
        # Check if motion file exists
        if not os.path.exists(motion['file']):
            print(f"  Warning: Motion file not found: {motion['file']}")
            continue
            
        # Output file path
        output_file = output_dir / f"test_{motion['name']}_hybrid.pkl"
        
        # Run motion retargeting
        cmd = [
            "python", "scripts/smplx_to_robot.py",
            "--robot", "dash",
            "--smplx_file", motion['file'],
            "--save_path", str(output_file)
        ]
        
        try:
            print(f"  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  Success: {output_file}")
                results.append({
                    "name": motion['name'],
                    "file": motion['file'],
                    "output": str(output_file),
                    "status": "success"
                })
            else:
                print(f"  Error: {result.stderr}")
                results.append({
                    "name": motion['name'],
                    "file": motion['file'],
                    "output": str(output_file),
                    "status": "error",
                    "error": result.stderr
                })
                
        except subprocess.TimeoutExpired:
            print(f"  Timeout: Motion took too long to process")
            results.append({
                "name": motion['name'],
                "file": motion['file'],
                "output": str(output_file),
                "status": "timeout"
            })
        except Exception as e:
            print(f"  Exception: {str(e)}")
            results.append({
                "name": motion['name'],
                "file": motion['file'],
                "output": str(output_file),
                "status": "exception",
                "error": str(e)
            })
        
        print()
    
    # Save results summary
    results_file = output_dir / "test_results_summary.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Test Summary:")
    print("=" * 50)
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Successful: {success_count}/{len(results)}")
    
    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['name']}: {result['status']}")
    
    print(f"\nResults saved to: {results_file}")
    print(f"Motion files saved to: {output_dir}")
    
    return results

def visualize_results():
    """Visualize the test results"""
    output_dir = Path("test_results/dash/hybrid_tests")
    
    if not output_dir.exists():
        print("No test results found. Run test_hybrid_motions() first.")
        return
    
    print("Visualizing hybrid test results...")
    
    # Find all PKL files
    pkl_files = list(output_dir.glob("*.pkl"))
    
    if not pkl_files:
        print("No PKL files found in test results.")
        return
    
    for pkl_file in pkl_files:
        print(f"Visualizing: {pkl_file.name}")
        
        cmd = [
            "python", "scripts/vis_robot_motion.py",
            "--robot", "dash",
            "--robot_motion_path", str(pkl_file)
        ]
        
        try:
            subprocess.run(cmd, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"  Visualization timeout for {pkl_file.name}")
        except Exception as e:
            print(f"  Visualization error for {pkl_file.name}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "visualize":
        visualize_results()
    elif len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
        # Use custom configuration file
        if len(sys.argv) > 2 and sys.argv[2].endswith('.json'):
            # Specify both source and target config files
            test_hybrid_motions(sys.argv[1], sys.argv[2])
        else:
            # Use default target (smplx_to_dash.json)
            test_hybrid_motions(sys.argv[1])
    else:
        test_hybrid_motions()
