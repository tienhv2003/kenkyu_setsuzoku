#!/usr/bin/env python3
"""
Pipeline Script - Kết nối Step 1 và Step 2
Tự động chạy: Video Detection → Auto-cut → Super Resolution

Usage:
    # Chạy full pipeline
    python run_pipeline.py data/input/road1_can_cao.mp4
    
    # Chạy với config tùy chỉnh
    python run_pipeline.py data/input/video.mp4 --step1-config config/config_polygon_example.yaml
    
    # Chạy với interactive ROI selection
    python run_pipeline.py data/input/video.mp4 --interactive-roi
    
    # Chỉ chạy Step 2 (với output từ Step 1 có sẵn)
    python run_pipeline.py --skip-step1 --step1-output data/output/cropped_plates_polygon
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get project root directory"""
    return Path(__file__).parent.resolve()


def run_command(cmd, description):
    """
    Run a command and handle errors
    
    Args:
        cmd (list): Command and arguments
        description (str): Description of the command
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"   {description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {description} failed with code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Error: Command not found: {cmd[0]}")
        return False


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Pipeline - Kết nối Step 1 (Detection) và Step 2 (Enhancement)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Chạy full pipeline
    python run_pipeline.py data/input/road1_can_cao.mp4
    
    # Với interactive ROI selection
    python run_pipeline.py data/input/video.mp4 --interactive-roi
    
    # Chỉ Step 2 (đã có output Step 1)
    python run_pipeline.py --skip-step1 --step1-output data/output/cropped_plates_polygon
    
    # Custom config và output names
    python run_pipeline.py data/input/video.mp4 --run-name my_test
        """
    )
    
    # Input video (cho Step 1)
    parser.add_argument(
        'input_video',
        nargs='?',
        help='Path to input video file (required unless --skip-step1)'
    )
    
    # Step 1 options
    parser.add_argument(
        '--skip-step1',
        action='store_true',
        help='Bỏ qua Step 1 (detection), chỉ chạy Step 2'
    )
    
    parser.add_argument(
        '--step1-config',
        default='config/config_polygon_example.yaml',
        help='Config file cho Step 1 (default: config/config_polygon_example.yaml)'
    )
    
    parser.add_argument(
        '--step1-output',
        help='Output folder của Step 1 (nếu --skip-step1, dùng folder có sẵn)'
    )
    
    parser.add_argument(
        '--interactive-roi',
        action='store_true',
        help='Enable interactive ROI selection cho Step 1'
    )
    
    parser.add_argument(
        '--roi-frame',
        type=int,
        default=0,
        help='Frame number for ROI selection (default: 0)'
    )
    
    # Step 2 options
    parser.add_argument(
        '--skip-step2',
        action='store_true',
        help='Bỏ qua Step 2 (enhancement)'
    )
    
    parser.add_argument(
        '--step2-config',
        default='step02_use_edge_detection/config.yaml',
        help='Config file cho Step 2 (default: step02_use_edge_detection/config.yaml)'
    )
    
    parser.add_argument(
        '--skip-auto-cut',
        action='store_true',
        help='Bỏ qua auto-cut trong Step 2'
    )
    
    parser.add_argument(
        '--skip-super-resolution',
        action='store_true',
        help='Bỏ qua super resolution trong Step 2'
    )
    
    # General options
    parser.add_argument(
        '--run-name',
        help='Tên cho run này (dùng để đặt tên output folders)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.skip_step1 and not args.input_video:
        parser.error("input_video is required unless --skip-step1 is specified")
    
    if args.skip_step1 and not args.step1_output:
        parser.error("--step1-output is required when --skip-step1 is specified")
    
    project_root = get_project_root()
    
    # Generate run name if not provided
    if not args.run_name:
        if args.input_video:
            video_name = Path(args.input_video).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.run_name = f"{video_name}_{timestamp}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.run_name = f"run_{timestamp}"
    
    print(f"\n{'='*70}")
    print(f"   PIPELINE - TRAFFIC LICENSE PLATE PROCESSING")
    print(f"{'='*70}")
    print(f"Run name: {args.run_name}")
    if not args.skip_step1:
        print(f"Input video: {args.input_video}")
    print(f"Step 1: {'SKIP' if args.skip_step1 else 'RUN'}")
    print(f"Step 2: {'SKIP' if args.skip_step2 else 'RUN'}")
    print(f"{'='*70}\n")
    
    # ============================================
    # STEP 1: License Plate Detection with YOLO
    # ============================================
    
    if not args.skip_step1:
        print("\n🚀 STARTING STEP 1: LICENSE PLATE DETECTION")
        
        # Xác định output folder cho Step 1
        if args.step1_output:
            step1_output = args.step1_output
        else:
            step1_output = f"data/output/cropped_plates_{args.run_name}"
        
        # Build Step 1 command
        step1_cmd = [
            sys.executable,
            "main.py",
            args.input_video,
            "--config", args.step1_config
        ]
        
        if args.interactive_roi:
            step1_cmd.extend(["--interactive-roi"])
            step1_cmd.extend(["--roi-frame", str(args.roi_frame)])
        
        # Run Step 1
        success = run_command(step1_cmd, "STEP 1: YOLO License Plate Detection")
        
        if not success:
            print("\n❌ Pipeline stopped: Step 1 failed")
            sys.exit(1)
        
        print(f"\n✅ Step 1 completed!")
        print(f"   Output: {step1_output}")
        
    else:
        print("\n⏭️  SKIPPING STEP 1")
        step1_output = args.step1_output
        print(f"   Using existing output: {step1_output}")
    
    # Validate Step 1 output exists
    step1_output_path = project_root / step1_output
    if not step1_output_path.exists():
        print(f"\n❌ Error: Step 1 output not found: {step1_output_path}")
        sys.exit(1)
    
    # Count images in Step 1 output
    image_count = len(list(step1_output_path.glob("*.jpg"))) + len(list(step1_output_path.glob("*.png")))
    print(f"\n📊 Step 1 output contains {image_count} images")
    
    if image_count == 0:
        print("\n⚠️  No images found in Step 1 output. Skipping Step 2.")
        sys.exit(0)
    
    # ============================================
    # STEP 2: Image Enhancement
    # ============================================
    
    if not args.skip_step2:
        print("\n🚀 STARTING STEP 2: IMAGE ENHANCEMENT")
        
        # Xác định output folders cho Step 2
        step2_output_cut = f"step02_use_edge_detection/data/plates_after_cut/{args.run_name}"
        step2_output_sr = f"step02_use_edge_detection/data/plates_after_cut_super_resolution/{args.run_name}"
        
        # Build Step 2 command
        step2_cmd = [
            sys.executable,
            "step02_use_edge_detection/main.py",
            "--input", str(step1_output),
            "--output-cut", step2_output_cut,
            "--output-sr", step2_output_sr
        ]
        
        if args.skip_auto_cut:
            step2_cmd.append("--skip-auto-cut")
        
        if args.skip_super_resolution:
            step2_cmd.append("--skip-super-resolution")
        
        # Run Step 2
        success = run_command(step2_cmd, "STEP 2: Auto-cut + Super Resolution")
        
        if not success:
            print("\n❌ Pipeline stopped: Step 2 failed")
            sys.exit(1)
        
        print(f"\n✅ Step 2 completed!")
        print(f"   Output (cut): {step2_output_cut}")
        print(f"   Output (SR):  {step2_output_sr}")
    
    else:
        print("\n⏭️  SKIPPING STEP 2")
    
    # ============================================
    # PIPELINE COMPLETED
    # ============================================
    
    print(f"\n{'='*70}")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*70}")
    print(f"\n📁 Output Summary:")
    print(f"   Run name: {args.run_name}")
    if not args.skip_step1:
        print(f"   Step 1 (Detection):     {step1_output}")
    if not args.skip_step2:
        print(f"   Step 2 (Auto-cut):      {step2_output_cut}")
        print(f"   Step 2 (Super-Res):     {step2_output_sr}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

