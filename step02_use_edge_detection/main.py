#!/usr/bin/env python3
"""
Step 02 - License Plate Enhancement
Auto-cut với Canny edge detection + Super Resolution

Usage:
    # Chạy với config file
    python main.py --config config.yaml
    
    # Chạy với input/output folder cụ thể
    python main.py --input ../data/output/cropped_plates_polygon --output-cut data/output/cut --output-sr data/output/sr
    
    # Chỉ chạy auto-cut (bỏ qua super resolution)
    python main.py --input ../data/output/cropped_plates_polygon --skip-super-resolution
"""

import os
import sys
import argparse
from pathlib import Path

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.auto_cut_image import process_images_from_folder
from modules.super_resolution import superres_images_in_folder, load_super_resolution_model
from modules.utils import load_config, ensure_directory_exists, resolve_path, get_project_root


def main():
    """
    Main entry point cho Step 02
    """
    parser = argparse.ArgumentParser(
        description="Step 02 - License Plate Enhancement (Auto-cut + Super Resolution)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Chạy với config file
    python main.py --config config.yaml
    
    # Chạy với input/output cụ thể
    python main.py --input ../data/output/cropped_plates_polygon
    
    # Chỉ auto-cut, bỏ qua super resolution
    python main.py --input ../data/output/cropped_plates_polygon --skip-super-resolution
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--input',
        help='Input folder chứa ảnh biển số (override config)'
    )
    
    parser.add_argument(
        '--output-cut',
        help='Output folder cho ảnh sau auto-cut (override config)'
    )
    
    parser.add_argument(
        '--output-sr',
        help='Output folder cho ảnh sau super resolution (override config)'
    )
    
    parser.add_argument(
        '--skip-auto-cut',
        action='store_true',
        help='Bỏ qua bước auto-cut'
    )
    
    parser.add_argument(
        '--skip-super-resolution',
        action='store_true',
        help='Bỏ qua bước super resolution'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=True,
        help='In chi tiết quá trình xử lý'
    )
    
    args = parser.parse_args()
    
    # Load config
    config_path = resolve_path(args.config, base_dir=get_project_root())
    
    if os.path.exists(config_path):
        print(f"📄 Loading config from: {config_path}")
        config = load_config(config_path)
    else:
        print(f"⚠️  Config file not found: {config_path}")
        print("Using default configuration...")
        config = {
            'paths': {
                'input_dir': '../data/output/cropped_plates_polygon',
                'output_cut_dir': 'data/plates_after_cut/auto',
                'output_super_resolution_dir': 'data/plates_after_cut_super_resolution/auto'
            },
            'processing': {
                'super_resolution': {
                    'model_path': 'models/super_resolution/FSRCNN_x4.pb',
                    'model_name': 'fsrcnn',
                    'scale': 4
                }
            }
        }
    
    # Override với command line arguments
    if args.input:
        input_dir = resolve_path(args.input, base_dir=get_project_root())
    else:
        input_dir = resolve_path(config['paths']['input_dir'], base_dir=get_project_root())
    
    if args.output_cut:
        output_cut_dir = resolve_path(args.output_cut, base_dir=get_project_root())
    else:
        output_cut_dir = resolve_path(config['paths']['output_cut_dir'], base_dir=get_project_root())
    
    if args.output_sr:
        output_sr_dir = resolve_path(args.output_sr, base_dir=get_project_root())
    else:
        output_sr_dir = resolve_path(config['paths']['output_super_resolution_dir'], base_dir=get_project_root())
    
    # Validate input
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input folder không tồn tại: {input_dir}")
        sys.exit(1)
    
    # Ensure output directories exist
    ensure_directory_exists(output_cut_dir)
    ensure_directory_exists(output_sr_dir)
    
    print(f"\n{'='*70}")
    print(f"   STEP 02 - LICENSE PLATE ENHANCEMENT")
    print(f"{'='*70}")
    print(f"Input:              {input_dir}")
    print(f"Output (Auto-cut):  {output_cut_dir}")
    print(f"Output (Super-Res): {output_sr_dir}")
    print(f"{'='*70}\n")
    
    # Step 1: Auto-cut với Canny edge detection
    if not args.skip_auto_cut:
        print("\n🔹 BƯỚC 1: AUTO-CUT VỚI CANNY EDGE DETECTION")
        results_cut = process_images_from_folder(
            input_dir, 
            output_cut_dir,
            verbose=args.verbose
        )
        
        if results_cut['success'] == 0:
            print("⚠️  Không có ảnh nào được auto-cut thành công.")
            print("Bỏ qua bước super resolution.")
            sys.exit(0)
    else:
        print("\n⏭️  Bỏ qua bước Auto-cut")
    
    # Step 2: Super Resolution
    if not args.skip_super_resolution:
        print("\n🔹 BƯỚC 2: SUPER RESOLUTION")
        
        # Load super resolution model
        sr_config = config.get('processing', {}).get('super_resolution', {})
        model_path = resolve_path(
            sr_config.get('model_path', 'models/super_resolution/FSRCNN_x4.pb'),
            base_dir=get_project_root()
        )
        model_name = sr_config.get('model_name', 'fsrcnn')
        scale = sr_config.get('scale', 4)
        
        print(f"Loading model: {model_path}")
        try:
            sr_model = load_super_resolution_model(model_path, model_name, scale)
        except Exception as e:
            print(f"❌ Lỗi load model: {e}")
            print("Sử dụng model mặc định...")
            sr_model = None
        
        # Xác định input cho super resolution
        if args.skip_auto_cut:
            # Nếu skip auto-cut, dùng input_dir làm source
            sr_input = input_dir
        else:
            # Nếu đã auto-cut, dùng output_cut_dir làm source
            sr_input = output_cut_dir
        
        results_sr = superres_images_in_folder(
            sr_input,
            output_sr_dir,
            model=sr_model,
            verbose=args.verbose
        )
    else:
        print("\n⏭️  Bỏ qua bước Super Resolution")
    
    print(f"\n{'='*70}")
    print("✅ HOÀN THÀNH STEP 02!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
