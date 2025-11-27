#!/usr/bin/env python3
"""
Traffic License Plate Detector - Main Application

This application processes traffic videos to detect and extract license plates
using a trained YOLO model.

Usage:
    python main.py <input_video_path>

Example:
    python main.py data/input/traffic_video.mp4
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import load_config, ensure_directory_exists, resolve_path
from src.video_processor import VideoProcessor


def main():
    """
    Main application entry point
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Traffic License Plate Detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py data/input/traffic_video.mp4
    python main.py --config config/custom_config.yaml data/input/traffic_video.mp4
        """
    )
    
    parser.add_argument(
        'input_video',
        help='Path to input video file'
    )
    
    parser.add_argument(
        '--config',
        default='config/config_polygon_example.yaml',
        help='Path to configuration file (default: config/config_polygon_example.yaml)'
    )
    
    parser.add_argument(
        '--interactive-roi',
        action='store_true',
        help='Enable interactive ROI selection from video'
    )
    
    parser.add_argument(
        '--roi-frame',
        type=int,
        default=0,
        help='Frame number to use for ROI selection (default: 0)'
    )
    
    parser.add_argument(
        '--max-points',
        type=int,
        default=4,
        help='Maximum points for polygon ROI (default: 4, only for polygon mode)'
    )
    
    parser.add_argument(
        '--max-frames',
        type=int,
        help='Maximum number of frames to process (useful for testing with long videos)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for cropped plates (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Resolve input and config paths relative to project root
    input_video_path = resolve_path(args.input_video)
    config_path = resolve_path(args.config)

    # Validate input video
    if not os.path.exists(input_video_path):
        print(f"Error: Input video file not found: {input_video_path}")
        sys.exit(1)
    
    # Validate config file
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Load configuration
        print(f"Loading configuration from: {config_path}")
        config = load_config(config_path)
        
        # Enable interactive ROI selection if requested
        if args.interactive_roi:
            config['roi']['interactive_selection'] = True
            print("Interactive ROI selection enabled")
        
        # Set max frames if specified
        if args.max_frames:
            if 'processing' not in config:
                config['processing'] = {}
            config['processing']['max_frames'] = args.max_frames
            print(f"Max frames limit: {args.max_frames}")
        
        # Override output directory if specified
        if args.output_dir:
            config['output']['cropped_plates_dir'] = args.output_dir
            print(f"Output directory (overridden): {args.output_dir}")
            
            # Also update annotated video path to match
            output_dir_name = Path(args.output_dir).name
            video_dir = os.path.dirname(config['output']['annotated_video_path'])
            config['output']['annotated_video_path'] = os.path.join(video_dir, f"annotated_video_{output_dir_name.replace('cropped_plates_', '')}.mp4")
        
        # Validate model path
        model_path = resolve_path(config['model']['path'])
        if not os.path.exists(model_path):
            print(f"Error: Model file not found: {model_path}")
            print("Please place your trained YOLO model (.pt file) in the models/ directory")
            print("and update the model path in the configuration file.")
            sys.exit(1)
        
        # Ensure output directories exist
        config['output']['cropped_plates_dir'] = resolve_path(config['output']['cropped_plates_dir'])
        ensure_directory_exists(config['output']['cropped_plates_dir'])
        
        # Create output directory for annotated video
        config['output']['annotated_video_path'] = resolve_path(config['output']['annotated_video_path'])
        output_video_dir = os.path.dirname(config['output']['annotated_video_path'])
        ensure_directory_exists(output_video_dir)
        
        # Initialize and run video processor
        print("Initializing video processor...")
        processor = VideoProcessor(config)
        
        # Setup interactive ROI if enabled
        if config['roi'].get('interactive_selection', False):
            print("\nSetting up ROI interactively...")
            roi_mode = config['roi'].get('mode', 'rectangle')
            print(f"ROI Mode: {roi_mode}")
            
            if roi_mode == 'polygon':
                print(f"Max points: {args.max_points}")
            
            roi_success = processor.setup_roi_interactive(
                input_video_path, 
                args.roi_frame,
                max_points=args.max_points
            )
            
            if not roi_success:
                print("Failed to setup ROI. Exiting...")
                sys.exit(1)
        
        print(f"Starting video processing: {input_video_path}")
        # Propagate resolved model path so downstream uses absolute path
        config['model']['path'] = model_path
        processor.process_video(input_video_path)
        
        print("Video processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
