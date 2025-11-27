"""
Video Processing Module - POLYGON ROI ONLY VERSION
Simplified version chỉ support Polygon ROI
"""

import cv2
import os
import numpy as np
from .model_inference import LicensePlateDetector
from .polygon_roi_manager import PolygonROIManager
from .simple_plate_tracker import SimplePlateTracker, Track
from .utils import ensure_directory_exists, resolve_path


class VideoProcessor:
    """
    Main video processing class - Polygon ROI Only
    """
    
    def __init__(self, config: dict):
        """
        Initialize video processor with configuration
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.detector = None
        self.roi_manager = None
        self.tracker = None
        self.setup_components()
    
    def setup_components(self) -> None:
        """
        Setup detector and ROI manager
        """
        # Initialize detector
        model_config = self.config['model']
        self.detector = LicensePlateDetector(
            model_path=model_config['path'],
            confidence_threshold=model_config['confidence_threshold'],
            iou_threshold=model_config['iou_threshold']
        )
        
        # Initialize Polygon ROI manager
        roi_config = self.config['roi']
        if roi_config['enabled']:
            print(f"ROI Mode: Polygon")
            
            if roi_config.get('interactive_selection', False):
                # Interactive selection
                self.roi_manager = PolygonROIManager()
            else:
                # Load từ config
                points = roi_config.get('points', None)
                if points:
                    # Convert list of lists to list of tuples
                    points = [tuple(p) for p in points]
                    self.roi_manager = PolygonROIManager(points=points)
                else:
                    self.roi_manager = PolygonROIManager()
        
        # Ensure output directories exist
        ensure_directory_exists(self.config['output']['cropped_plates_dir'])
        
        # Initialize Tracker
        tracking_config = self.config.get('tracking', {})
        if tracking_config.get('enabled', False):
            print("\n=== Initializing Tracker ===")
            self.tracker = SimplePlateTracker(
                max_age=tracking_config.get('max_age', 8),
                min_hits=tracking_config.get('min_hits', 2),
                iou_threshold=tracking_config.get('iou_threshold', 0.35)
            )
            print("✅ Tracking enabled: Duplicate plates will be filtered\n")
        else:
            self.tracker = None
            print("ℹ️  Tracking disabled: All detections will be saved\n")
    
    def setup_roi_interactive(self, video_path: str, frame_number: int = 0, max_points: int = 4) -> bool:
        """
        Setup ROI bằng cách chọn interactive từ video
        
        Args:
            video_path (str): Đường dẫn đến video
            frame_number (int): Số frame để hiển thị
            max_points (int): Số điểm tối đa cho polygon
            
        Returns:
            bool: True nếu ROI được setup thành công
        """
        if self.roi_manager is None:
            print("Error: ROI manager chưa được khởi tạo")
            return False
        
        print(f"\n=== Interactive Polygon ROI Selection ===")
        print(f"Video: {video_path}")
        print(f"Frame: {frame_number}")
        print(f"Max points: {max_points}")
        
        success = self.roi_manager.set_roi_from_video(video_path, frame_number, max_points)
        
        if success:
            print(f"Polygon ROI đã được set với {len(self.roi_manager.points)} điểm")
        else:
            print("Không thể setup Polygon ROI interactive")
        
        return success
    
    def process_video(self, input_video_path: str) -> None:
        """
        Process video file and extract license plates
        
        Args:
            input_video_path (str): Path to input video file
        """
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Input video not found: {input_video_path}")
        
        # Open video capture
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video file: {input_video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        # Setup video writer for annotated output
        output_config = self.config['output']
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            resolve_path(output_config['annotated_video_path']),
            fourcc,
            self.config['video']['output_fps'],
            (width, height)
        )
        
        # Check if video writer is initialized properly
        if not out.isOpened():
            print(f"Warning: Could not initialize video writer for {output_config['annotated_video_path']}")
            print("Video output will not be saved")
            out = None
        else:
            print(f"Video writer initialized successfully: {output_config['annotated_video_path']}")
        
        # Processing parameters
        skip_frames = self.config['frame_sampling']['skip_frames']
        plate_counter = self.config['output']['plate_filename_counter_start']
        frame_count = 0
        processed_frames = 0
        paused = False
        
        # Setup display window for real-time detection viewing
        display_window = "Live Detection View"
        cv2.namedWindow(display_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(display_window, 1200, 800)
        
        # Get max_frames limit if specified
        max_frames = self.config.get('processing', {}).get('max_frames', None)
        
        print(f"Starting video processing with frame skip = {skip_frames}")
        if max_frames:
            print(f"⚠️  Max frames limit: {max_frames}")
        print("Controls:")
        print("  'q' - Quit processing")
        print("  'p' - Pause/Resume")
        print("  's' - Save current frame")
        print("  SPACE - Process current frame immediately")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Check if we've reached max frames limit
                if max_frames and frame_count > max_frames:
                    print(f"\n⚠️  Reached max frames limit ({max_frames}). Stopping...")
                    break
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord('p'):
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                elif key == ord('s'):
                    # Save current frame
                    save_path = resolve_path(f"data/output/frame_{frame_count:06d}.jpg")
                    cv2.imwrite(save_path, frame)
                    print(f"Saved frame to: {save_path}")
                
                # If paused, just display frame without processing
                if paused:
                    display_frame = frame.copy()
                    if self.roi_manager:
                        display_frame = self.roi_manager.draw_roi_overlay(display_frame)
                    
                    # Add pause indicator
                    cv2.putText(display_frame, "PAUSED - Press 'p' to resume", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    cv2.imshow(display_window, display_frame)
                    continue
                
                # Skip frames based on configuration (unless SPACE is pressed)
                should_process = (frame_count % skip_frames == 0) or (key == ord(' '))
                
                if not should_process:
                    # Still write the frame to output video (without processing)
                    if out is not None:
                        if self.roi_manager:
                            frame_with_roi = self.roi_manager.draw_roi_overlay(frame)
                            out.write(frame_with_roi)
                        else:
                            out.write(frame)
                    
                    # Display frame without processing
                    display_frame = frame.copy()
                    if self.roi_manager:
                        display_frame = self.roi_manager.draw_roi_overlay(display_frame)
                    
                    # Add frame info
                    cv2.putText(display_frame, f"Frame: {frame_count}/{total_frames} (Skipped)", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow(display_window, display_frame)
                    continue
                
                processed_frames += 1
                print(f"Processing frame {frame_count}/{total_frames} (processed: {processed_frames})")
                
                # Process frame
                processed_frame = self.process_frame(frame, plate_counter, frame_count)
                
                # Write processed frame to output video
                if out is not None:
                    out.write(processed_frame)
                
                # Display processed frame with detection info
                display_frame = processed_frame.copy()
                
                # Add processing info
                info_text = f"Frame: {frame_count}/{total_frames} | Processed: {processed_frames}"
                cv2.putText(display_frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow(display_window, display_frame)
                
                # Update plate counter
                plate_counter += 1
        
        except KeyboardInterrupt:
            print("Processing interrupted by user")
        
        finally:
            # Lưu remaining track khi video kết thúc (nếu có tracking)
            if self.tracker is not None and getattr(self.tracker, "active_track", None) is not None:
                print("\n=== Video ended, saving remaining active track (if valid) ===")
                track = self.tracker.active_track
                if track.is_confirmed(self.tracker.min_hits) and track.best_cropped is not None:
                    self._save_tracked_plate(track.best_cropped, plate_counter, track)
                    plate_counter += 1
                    print(f"  💾 Saved remaining Track {track.track_id}")
            
            # Cleanup
            cap.release()
            if out is not None:
                out.release()
            cv2.destroyAllWindows()
            print("Display windows closed")
            
            print(f"Processing completed!")
            print(f"Total frames processed: {processed_frames}")
            print(f"License plates saved: {plate_counter - self.config['output']['plate_filename_counter_start']}")
            # Use resolved absolute path for display
            annotated_path = resolve_path(output_config['annotated_video_path'])
            print(f"Annotated video saved to: {annotated_path}")
    
    def process_frame(self, frame: np.ndarray, plate_counter: int, frame_number: int = 0) -> np.ndarray:
        """
        Process a single frame with Polygon ROI and optional Tracking
        
        Args:
            frame (np.ndarray): Input frame
            plate_counter (int): Current plate counter for naming
            frame_number (int): Current frame number (for tracking)
            
        Returns:
            np.ndarray: Processed frame with annotations
        """
        # 1. Detect license plates
        detections = self.detector.detect_license_plates(frame)
        
        # Print detection info (before filtering)
        if detections:
            print(f"  Found {len(detections)} license plate(s) in frame")
            for i, detection in enumerate(detections):
                x1, y1, x2, y2, confidence, class_id = detection
                print(f"    Detection {i+1}: confidence={confidence:.3f}, bbox=({x1},{y1},{x2},{y2})")
        
        # 2. Filter detections by polygon ROI
        if self.roi_manager:
            frame_shape = (frame.shape[0], frame.shape[1])  # (height, width)
            detections = self.roi_manager.filter_detections(detections, frame_shape)
            print(f"  After polygon filtering: {len(detections)} detection(s)")
        
        # 3. TRACKING LOGIC (IF ENABLED)
        if self.tracker is not None:
            plates_saved = self._process_with_tracking(frame, detections, 
                                                        plate_counter, frame_number)
            # Draw tracks
            annotated_frame = self._draw_tracks(frame)
            
            # Add track count info
            stats = self.tracker.get_stats()
            cv2.putText(annotated_frame, 
                       f"Active: {stats['active_tracks']} | Confirmed: {stats['confirmed_tracks']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 4. NO TRACKING (FALLBACK - ORIGINAL LOGIC)
        else:
            plates_saved = 0
            for detection in detections:
                cropped_plate = self.detector.crop_license_plate(frame, detection)
                if cropped_plate is not None:
                    self.save_cropped_plate(cropped_plate, plate_counter)
                    plate_counter += 1
                    plates_saved += 1
            
            if plates_saved > 0:
                print(f"  Saved {plates_saved} license plate image(s)")
            
            # Draw detections
            annotated_frame = self.detector.draw_detections(frame, detections)
            
            # Add detection count
            if detections:
                cv2.putText(annotated_frame, f"Detections: {len(detections)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 5. Draw Polygon ROI overlay
        if self.roi_manager:
            annotated_frame = self.roi_manager.draw_roi_overlay(annotated_frame)
        
        return annotated_frame
    
    def save_cropped_plate(self, cropped_plate: np.ndarray, plate_counter: int) -> None:
        """
        Save cropped license plate image
        
        Args:
            cropped_plate (np.ndarray): Cropped license plate image
            plate_counter (int): Plate counter for filename
        """
        output_dir = resolve_path(self.config['output']['cropped_plates_dir'])
        prefix = self.config['output']['plate_filename_prefix']
        filename = f"{prefix}{plate_counter:03d}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        try:
            cv2.imwrite(filepath, cropped_plate)
            print(f"Saved license plate: {filename}")
        except Exception as e:
            print(f"Error saving license plate {filename}: {e}")
    
    # ========== TRACKING METHODS ==========
    
    def _process_with_tracking(self, frame: np.ndarray, detections: list, 
                              plate_counter: int, frame_number: int) -> int:
        """
        Xử lý detections với tracking để loại bỏ duplicate
        
        Args:
            frame: Current frame
            detections: List of detections
            plate_counter: Current plate counter
            frame_number: Current frame number
        
        Returns:
            Number of plates saved
        """
        # Update tracker
        active_tracks, completed_tracks = self.tracker.update(detections, frame_number)
        
        # Crop và cache ảnh cho active tracks
        for track in active_tracks:
            # Tạo detection tuple từ track bbox
            det_tuple = (*track.bbox, track.confidence, 0)
            cropped = self.detector.crop_license_plate(frame, det_tuple)
            
            # Lưu ảnh nếu đây là best frame
            if cropped is not None and track.confidence == track.best_confidence:
                track.best_cropped = cropped
        
        # Lưu ảnh cho completed tracks
        plates_saved = 0
        for track in completed_tracks:
            if track.best_cropped is not None:
                # Tạo filename với track_id
                self._save_tracked_plate(track.best_cropped, plate_counter, track)
                plate_counter += 1
                plates_saved += 1
                
                print(f"  💾 Saved Track {track.track_id}: "
                      f"conf={track.best_confidence:.3f}, "
                      f"hits={track.hits}, "
                      f"frames=[{track.first_frame}-{track.last_frame}]")
        
        if plates_saved > 0:
            print(f"  Total saved this frame: {plates_saved} plate(s)")
        
        return plates_saved
    
    def _save_tracked_plate(self, cropped_plate: np.ndarray, plate_counter: int, 
                           track: Track) -> None:
        """
        Lưu ảnh biển số từ track với metadata
        
        Args:
            cropped_plate: Cropped plate image
            plate_counter: Plate counter
            track: Track object
        """
        output_dir = resolve_path(self.config['output']['cropped_plates_dir'])
        prefix = self.config['output']['plate_filename_prefix']
        
        # Format: plate_001_track005_conf087.jpg
        filename = (f"{prefix}{plate_counter:03d}_"
                   f"track{track.track_id:03d}_"
                   f"conf{int(track.best_confidence*100):03d}.jpg")
        filepath = os.path.join(output_dir, filename)
        
        try:
            cv2.imwrite(filepath, cropped_plate)
            print(f"    → {filename}")
        except Exception as e:
            print(f"    ❌ Error saving {filename}: {e}")
    
    def _draw_tracks(self, frame: np.ndarray) -> np.ndarray:
        """
        Vẽ tracks lên frame
        
        Args:
            frame: Input frame
        
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        # Màu sắc cho track active
        color = (0, 255, 0)  # Green

        # Vẽ chỉ 1 track active nếu đã confirmed
        if self.tracker is not None and getattr(self.tracker, "active_track", None) is not None:
            track = self.tracker.active_track
            if track.is_confirmed(self.tracker.min_hits):
                x1, y1, x2, y2 = map(int, track.bbox)
                
                # Vẽ bbox
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Vẽ label
                label = f"ID:{track.track_id} | {track.confidence:.2f} | H:{track.hits}"
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                
                # Background cho text
                cv2.rectangle(annotated_frame, (x1, y1 - text_h - 10), 
                             (x1 + text_w, y1), color, -1)
                
                # Text
                cv2.putText(annotated_frame, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated_frame
