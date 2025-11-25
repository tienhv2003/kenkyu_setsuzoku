#!/usr/bin/env python3
"""
Pipeline Script - Kết nối Step 1, Step 2 và Step 3 (Cấu trúc ngang hàng)
Tự động chạy: Video Detection → Auto-cut → Super Resolution → Feature Extraction

Cấu trúc thư mục:
connecting/
├── step01_use_model_train20251007/
├── step02_use_edge_detection/
├── step03_feature_extractor_matcher/
└── run_pipeline.py (file này)

Usage:
    # Chạy full pipeline
    python run_pipeline.py data/input/road1_can_cao.mp4
    
    # Test nhanh với video dài (giới hạn số frames)
    python run_pipeline.py data/input/video.mp4 --max-frames 100
    
    # Chạy với config tùy chỉnh
    python run_pipeline.py data/input/video.mp4 --step1-config config/config_polygon_example.yaml
    
    # Chạy với interactive ROI selection (4 điểm mặc định)
    python run_pipeline.py data/input/video.mp4 --interactive-roi
    
    # Chạy với interactive ROI selection (6 điểm polygon)
    python run_pipeline.py data/input/video.mp4 --interactive-roi --max-points 6
    
    # Chỉ chạy Step 2 (với output từ Step 1 có sẵn)
    python run_pipeline.py --skip-step1 --step1-output step01_use_model_train20251007/data/output/cropped_plates_polygon
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get connecting directory (project root)"""
    return Path(__file__).parent.resolve()


def get_step1_dir():
    """Get step01 directory"""
    return get_project_root() / "step01_use_model_train20251007"


def get_step2_dir():
    """Get step02 directory"""
    return get_project_root() / "step02_use_edge_detection"


def get_step3_dir():
    """Get step03 directory"""
    return get_project_root() / "step03_feature_extractor_matcher"


def run_command(cmd, description, cwd=None):
    """
    Run a command and handle errors
    
    Args:
        cmd (list): Command and arguments
        description (str): Description of the command
        cwd (str): Working directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"   {description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}")
    if cwd:
        print(f"Working directory: {cwd}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=cwd)
        return result.returncode == 0
    except KeyboardInterrupt:
        print(f"\n[!] Interrupted by user (Ctrl+C)")
        print(f"   {description} was stopped.")
        raise  # Re-raise to allow main() to handle
    except subprocess.CalledProcessError as e:
        print(f"\n[X] Error: {description} failed with code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n[X] Error: Command not found: {cmd[0]}")
        return False


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Pipeline - Kết nối Step 1 (Detection), Step 2 (Enhancement) và Step 3 (Feature Extraction)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Chạy full pipeline
    python run_pipeline.py step01_use_model_train20251007/data/input/road1_can_cao.mp4
    
    # Với interactive ROI selection (4 điểm)
    python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4 --interactive-roi
    
    # Với interactive ROI selection (6 điểm polygon)
    python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4 --interactive-roi --max-points 6
    
    # Test nhanh với video dài (chỉ xử lý 100 frames đầu)
    python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4 --max-frames 100
    
    # Chỉ Step 2 (đã có output Step 1)
    python run_pipeline.py --skip-step1 --step1-output step01_use_model_train20251007/data/output/cropped_plates_polygon
    
    # Chỉ chạy Step 3 (đã có output Step 2)
    python run_pipeline.py --skip-step1 --skip-step2 --step3-input step02_use_edge_detection/data/plates_after_cut_super_resolution/run_name
    
    # Custom output names
    python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4 --run-name my_test
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
    
    parser.add_argument(
        '--max-points',
        type=int,
        default=4,
        help='Maximum points for polygon ROI (default: 4)'
    )
    
    parser.add_argument(
        '--max-frames',
        type=int,
        help='Maximum number of frames to process (useful for testing with long videos)'
    )
    
    # Step 2 options
    parser.add_argument(
        '--skip-step2',
        action='store_true',
        help='Bỏ qua Step 2 (enhancement)'
    )
    
    parser.add_argument(
        '--step2-config',
        default='config.yaml',
        help='Config file cho Step 2 (default: config.yaml)'
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
    
    # Step 3 options
    parser.add_argument(
        '--skip-step3',
        action='store_true',
        help='Bỏ qua Step 3 (feature extraction)'
    )
    
    parser.add_argument(
        '--step3-input',
        help='Input folder cho Step 3 (nếu không chỉ định, dùng output Step 2 SR)'
    )
    
    parser.add_argument(
        '--step3-output',
        help='Output folder cho Step 3 (default: step03_feature_extractor_matcher/output/{run_name})'
    )
    
    parser.add_argument(
        '--step3-scale-factor',
        type=float,
        default=1.0,
        help='Scale factor cho Step 3 (default: 1.0)'
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
    step1_dir = get_step1_dir()
    step2_dir = get_step2_dir()
    step3_dir = get_step3_dir()
    
    # Validate directories exist
    if not step1_dir.exists():
        print(f"[X] Error: Step 1 directory not found: {step1_dir}")
        sys.exit(1)
    
    if not step2_dir.exists():
        print(f"[X] Error: Step 2 directory not found: {step2_dir}")
        print("[!] Hint: Có thể bạn cần chạy script tái cấu trúc:")
        print("   python restructure_project.py")
        sys.exit(1)
    
    if not step3_dir.exists():
        print(f"[X] Error: Step 3 directory not found: {step3_dir}")
        sys.exit(1)
    
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
    print(f"Project root: {project_root}")
    print(f"Step 1 dir:   {step1_dir}")
    print(f"Step 2 dir:   {step2_dir}")
    print(f"Run name:     {args.run_name}")
    if not args.skip_step1:
        print(f"Input video:  {args.input_video}")
    print(f"Step 1:       {'SKIP' if args.skip_step1 else 'RUN'}")
    print(f"Step 2:       {'SKIP' if args.skip_step2 else 'RUN'}")
    print(f"Step 3:       {'SKIP' if args.skip_step3 else 'RUN'}")
    print(f"{'='*70}\n")
    
    # ============================================
    # STEP 1: License Plate Detection with YOLO
    # ============================================
    
    if not args.skip_step1:
        print("\n>> STARTING STEP 1: LICENSE PLATE DETECTION")
        
        # Xác định output folder cho Step 1
        if args.step1_output:
            step1_output = args.step1_output
        else:
            step1_output = f"data/output/cropped_plates_{args.run_name}"
        
        # Convert input video path to relative from step1_dir or absolute
        input_video_path = Path(args.input_video)
        if input_video_path.is_absolute():
            video_path_for_cmd = str(input_video_path)
        else:
            # Convert to absolute then back to relative from step1_dir
            abs_video_path = (project_root / input_video_path).resolve()
            try:
                video_path_for_cmd = str(abs_video_path.relative_to(step1_dir))
            except ValueError:
                # If cannot make relative, use absolute
                video_path_for_cmd = str(abs_video_path)
        
        # Build Step 1 command
        step1_cmd = [
            sys.executable,
            "main.py",
            video_path_for_cmd,
            "--config", args.step1_config,
            "--output-dir", step1_output  # Pass output directory to Step 1
        ]
        
        if args.interactive_roi:
            step1_cmd.extend(["--interactive-roi"])
            step1_cmd.extend(["--roi-frame", str(args.roi_frame)])
            step1_cmd.extend(["--max-points", str(args.max_points)])
        
        if args.max_frames:
            step1_cmd.extend(["--max-frames", str(args.max_frames)])
        
        # Run Step 1 from step01 directory
        success = run_command(
            step1_cmd, 
            "STEP 1: YOLO License Plate Detection",
            cwd=str(step1_dir)
        )
        
        if not success:
            print("\n[X] Pipeline stopped: Step 1 failed")
            sys.exit(1)
        
        print(f"\n[OK] Step 1 completed!")
        print(f"   Output: {step1_output}")
        
    else:
        print("\n[SKIP] SKIPPING STEP 1")
        step1_output = args.step1_output
        print(f"   Using existing output: {step1_output}")
    
    # Resolve Step 1 output path (có thể relative hoặc absolute)
    if Path(step1_output).is_absolute():
        step1_output_path = Path(step1_output)
    else:
        # Nếu relative, resolve từ step1_dir hoặc project_root
        step1_output_path = step1_dir / step1_output
        if not step1_output_path.exists():
            step1_output_path = project_root / step1_output
    
    # Validate Step 1 output exists
    if not step1_output_path.exists():
        print(f"\n[X] Error: Step 1 output not found: {step1_output_path}")
        sys.exit(1)
    
    # Count images in Step 1 output
    image_count = len(list(step1_output_path.glob("*.jpg"))) + len(list(step1_output_path.glob("*.png")))
    print(f"\n[INFO] Step 1 output contains {image_count} images")
    print(f"   Path: {step1_output_path}")
    
    if image_count == 0:
        print("\n[!] No images found in Step 1 output. Skipping Step 2.")
        sys.exit(0)
    
    # ============================================
    # STEP 2: Image Enhancement
    # ============================================
    
    if not args.skip_step2:
        print("\n>> STARTING STEP 2: IMAGE ENHANCEMENT")
        
        # Xác định output folders cho Step 2 (relative to step2_dir)
        step2_output_cut = f"data/plates_after_cut/{args.run_name}"
        step2_output_sr = f"data/plates_after_cut_super_resolution/{args.run_name}"
        
        # Build Step 2 command (input path phải absolute hoặc relative từ step2_dir)
        step2_cmd = [
            sys.executable,
            "main.py",
            "--input", str(step1_output_path.resolve()),
            "--output-cut", step2_output_cut,
            "--output-sr", step2_output_sr
        ]
        
        if args.skip_auto_cut:
            step2_cmd.append("--skip-auto-cut")
        
        if args.skip_super_resolution:
            step2_cmd.append("--skip-super-resolution")
        
        # Run Step 2 from step02 directory
        success = run_command(
            step2_cmd, 
            "STEP 2: Auto-cut + Super Resolution",
            cwd=str(step2_dir)
        )
        
        if not success:
            print("\n[X] Pipeline stopped: Step 2 failed")
            sys.exit(1)
        
        # Absolute paths for display
        step2_output_cut_abs = step2_dir / step2_output_cut
        step2_output_sr_abs = step2_dir / step2_output_sr
        
        print(f"\n[OK] Step 2 completed!")
        print(f"   Output (cut): {step2_output_cut_abs}")
        print(f"   Output (SR):  {step2_output_sr_abs}")
    
    else:
        print("\n[SKIP] SKIPPING STEP 2")
        # Nếu skip Step 2, cần xác định input cho Step 3
        if not args.skip_step3:
            if not args.step3_input:
                print("\n[!] Warning: Step 2 skipped but Step 3 requires input.")
                print("   Please specify --step3-input or skip Step 3 with --skip-step3")
                sys.exit(1)
    
    # ============================================
    # STEP 3: Feature Extraction
    # ============================================
    
    if not args.skip_step3:
        print("\n>> STARTING STEP 3: FEATURE EXTRACTION")
        
        # Xác định input cho Step 3
        if args.step3_input:
            step3_input_path = Path(args.step3_input)
            if not step3_input_path.is_absolute():
                step3_input_path = project_root / step3_input_path
        else:
            # Mặc định dùng output Step 2 SR
            if args.skip_step2:
                print("\n[X] Error: Step 2 skipped. Please specify --step3-input")
                sys.exit(1)
            step3_input_path = step2_dir / step2_output_sr
        
        # Validate Step 3 input exists
        if not step3_input_path.exists():
            print(f"\n[X] Error: Step 3 input not found: {step3_input_path}")
            sys.exit(1)
        
        # Count images in Step 3 input
        image_count = len(list(step3_input_path.glob("*.jpg"))) + len(list(step3_input_path.glob("*.png")))
        print(f"\n[INFO] Step 3 input contains {image_count} images")
        print(f"   Path: {step3_input_path}")
        
        if image_count == 0:
            print("\n[!] No images found in Step 3 input. Skipping Step 3.")
        else:
            # Xác định output cho Step 3
            if args.step3_output:
                step3_output_dir = Path(args.step3_output)
                if not step3_output_dir.is_absolute():
                    step3_output_dir = step3_dir / step3_output_dir
            else:
                step3_output_dir = step3_dir / "output" / args.run_name
            
            # Tạo output directory
            step3_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Import và chạy Step 3
            try:
                # Add step3 directory to path
                sys.path.insert(0, str(step3_dir))
                from feature_extractor import process_folder
                
                # Xác định output CSV path
                step3_output_csv = step3_output_dir / "keypoints_count.csv"
                
                # Tạo preprocessed directory trong output
                step3_preprocessed_dir = step3_output_dir / "preprocessed"
                step3_preprocessed_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"\n[INFO] Processing {image_count} images...")
                print(f"   Input:  {step3_input_path}")
                print(f"   Output: {step3_output_dir}")
                print(f"   CSV:    {step3_output_csv}")
                
                # Modify process_folder để chấp nhận absolute paths
                # Hoặc copy images vào input folder của step3
                import shutil
                
                # Tạo input folder trong step3_dir
                step3_temp_input = step3_dir / "input" / args.run_name
                step3_temp_input.mkdir(parents=True, exist_ok=True)
                
                # Copy images to temp input
                print(f"\n[INFO] Copying images to Step 3 input folder...")
                copied = 0
                for img_file in step3_input_path.glob("*.jpg"):
                    shutil.copy2(img_file, step3_temp_input / img_file.name)
                    copied += 1
                for img_file in step3_input_path.glob("*.png"):
                    shutil.copy2(img_file, step3_temp_input / img_file.name)
                    copied += 1
                
                print(f"   Copied {copied} images")
                
                # Change to step3_dir to run process_folder (vì nó dùng relative paths)
                original_cwd = os.getcwd()
                os.chdir(str(step3_dir))
                
                try:
                    # Update paths to be relative to step3_dir
                    relative_input = step3_temp_input.relative_to(step3_dir)
                    relative_output_csv = step3_output_csv.relative_to(step3_dir)
                    relative_preprocessed = step3_preprocessed_dir.relative_to(step3_dir)
                    
                    # Sử dụng hàm process_folder từ module với preprocessed_dir tùy chỉnh
                    process_folder(
                        str(relative_input),
                        str(relative_output_csv),
                        scale_factor=args.step3_scale_factor,
                        preprocessed_dir=str(relative_preprocessed)
                    )
                    
                    print(f"\n[OK] Step 3 completed!")
                    print(f"   Output CSV: {step3_output_csv}")
                    print(f"   Preprocessed images: {step3_preprocessed_dir}")
                    
                finally:
                    os.chdir(original_cwd)
                
            except ImportError as e:
                print(f"\n[X] Error importing Step 3 module: {e}")
                print("   Make sure feature_extractor.py exists in step03_feature_extractor_matcher/")
                sys.exit(1)
            except Exception as e:
                print(f"\n[X] Error running Step 3: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    else:
        print("\n[SKIP] SKIPPING STEP 3")
    
    # ============================================
    # PIPELINE COMPLETED
    # ============================================
    
    print(f"\n{'='*70}")
    print("[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*70}")
    print(f"\n[OUTPUT] Output Summary:")
    print(f"   Run name: {args.run_name}")
    if not args.skip_step1:
        print(f"   Step 1 (Detection): {step1_output_path}")
    if not args.skip_step2:
        print(f"   Step 2 (Auto-cut):  {step2_dir / step2_output_cut}")
        print(f"   Step 2 (Super-Res): {step2_dir / step2_output_sr}")
    if not args.skip_step3:
        if 'step3_output_dir' in locals():
            print(f"   Step 3 (Features):  {step3_output_dir}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Pipeline interrupted by user (Ctrl+C)")
        print("   Partial results may be available in output directories.")
        sys.exit(130)  # Standard exit code for Ctrl+C

