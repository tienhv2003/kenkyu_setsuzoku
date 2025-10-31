"""
Polygon ROI Manager Module
Quản lý Region of Interest dạng polygon sử dụng mask-based approach
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from .polygon_roi_selector import select_polygon_roi_interactive, select_polygon_roi_from_frame


class PolygonROIManager:
    """
    Quản lý ROI dạng polygon sử dụng mask-based filtering
    """
    
    def __init__(self, points: List[Tuple[int, int]] = None):
        """
        Initialize Polygon ROI manager with points
        
        Args:
            points: List of (x, y) tuples defining polygon vertices
                   e.g., [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                   If None, ROI will be set interactively
        """
        self.points = points if points else None
        self.mask = None
        self.bounding_box = None  # (x1, y1, x2, y2) của polygon
        
        if points:
            self._calculate_bounding_box()
    
    def set_points(self, points: List[Tuple[int, int]]) -> None:
        """
        Set polygon points manually
        
        Args:
            points: List of (x, y) tuples
        """
        self.points = points
        self._calculate_bounding_box()
    
    def set_roi_from_video(self, video_path: str, frame_number: int = 0, max_points: int = 4) -> bool:
        """
        Set ROI bằng cách chọn interactive từ video
        
        Args:
            video_path (str): Đường dẫn đến video
            frame_number (int): Số frame để hiển thị
            max_points (int): Số điểm tối đa
            
        Returns:
            bool: True nếu ROI được chọn thành công
        """
        try:
            polygon_points = select_polygon_roi_interactive(video_path, frame_number, max_points)
            if polygon_points:
                self.set_points(polygon_points)
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi chọn Polygon ROI interactive: {e}")
            return False
    
    def set_roi_from_frame(self, frame: np.ndarray, max_points: int = 4) -> bool:
        """
        Set ROI bằng cách chọn interactive từ frame
        
        Args:
            frame (np.ndarray): Frame để chọn ROI
            max_points (int): Số điểm tối đa
            
        Returns:
            bool: True nếu ROI được chọn thành công
        """
        try:
            polygon_points = select_polygon_roi_from_frame(frame, max_points)
            if polygon_points:
                self.set_points(polygon_points)
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi chọn Polygon ROI interactive: {e}")
            return False
    
    def is_roi_set(self) -> bool:
        """
        Kiểm tra xem ROI đã được set chưa
        
        Returns:
            bool: True nếu ROI đã được set
        """
        return self.points is not None and len(self.points) >= 3
    
    def _calculate_bounding_box(self) -> None:
        """
        Tính bounding box của polygon để optimize processing
        """
        if not self.points:
            return
        
        points_array = np.array(self.points)
        x_coords = points_array[:, 0]
        y_coords = points_array[:, 1]
        
        self.bounding_box = (
            int(np.min(x_coords)),
            int(np.min(y_coords)),
            int(np.max(x_coords)),
            int(np.max(y_coords))
        )
        
        print(f"Polygon bounding box: {self.bounding_box}")
    
    def create_mask(self, frame_shape: Tuple[int, int]) -> np.ndarray:
        """
        Tạo binary mask cho polygon
        
        Args:
            frame_shape: (height, width) của frame
            
        Returns:
            Binary mask (255 inside polygon, 0 outside)
        """
        height, width = frame_shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if self.is_roi_set():
            pts = np.array(self.points, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def extract_roi(self, frame: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Extract ROI bằng cách crop bounding box (tối ưu hóa)
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            Tuple of:
                - Cropped frame (vùng bounding box)
                - Offset coordinates (x_offset, y_offset)
        """
        if not self.is_roi_set():
            print("Warning: ROI chưa được set, sử dụng toàn bộ frame")
            return frame, (0, 0)
        
        if not self.bounding_box:
            self._calculate_bounding_box()
        
        x1, y1, x2, y2 = self.bounding_box
        height, width = frame.shape[:2]
        
        # Ensure coordinates are within frame bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)
        
        # Crop vùng bounding box
        cropped = frame[y1:y2, x1:x2]
        
        return cropped, (x1, y1)
    
    def is_point_in_polygon(self, x: int, y: int) -> bool:
        """
        Kiểm tra điểm có nằm trong polygon không sử dụng OpenCV
        
        Args:
            x, y: Point coordinates
            
        Returns:
            bool: True if point is inside polygon
        """
        if not self.is_roi_set():
            return True  # Nếu ROI chưa được set, coi như toàn bộ frame là ROI
        
        pts = np.array(self.points, dtype=np.int32)
        result = cv2.pointPolygonTest(pts, (float(x), float(y)), False)
        return result >= 0  # >= 0 means inside or on edge
    
    def is_bbox_in_polygon(self, x1: int, y1: int, x2: int, y2: int, 
                          threshold: float = 0.5) -> bool:
        """
        Kiểm tra bounding box có nằm trong polygon không
        Sử dụng center point hoặc intersection area
        
        Args:
            x1, y1, x2, y2: Bounding box coordinates
            threshold: Minimum overlap ratio (not used for center method)
            
        Returns:
            bool: True if bounding box is considered inside polygon
        """
        if not self.is_roi_set():
            return True
        
        # Method: Check if center point is inside polygon
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        return self.is_point_in_polygon(center_x, center_y)
    
    def adjust_detection_coordinates(self, detections: list, offset: Tuple[int, int] = (0, 0)) -> list:
        """
        Adjust detection coordinates from cropped space to full frame space
        và filter chỉ giữ detections nằm trong polygon
        
        Args:
            detections: List of detections in cropped coordinates
                       Format: [(x1, y1, x2, y2, confidence, class_id), ...]
            offset: (x_offset, y_offset) từ bounding box crop
            
        Returns:
            Filtered detections in full frame coordinates
        """
        if not self.is_roi_set():
            # Nếu ROI chưa được set, chỉ cần adjust coordinates
            x_offset, y_offset = offset
            adjusted = []
            for detection in detections:
                x1, y1, x2, y2, conf, cls = detection
                adjusted.append((x1 + x_offset, y1 + y_offset, 
                               x2 + x_offset, y2 + y_offset, conf, cls))
            return adjusted
        
        x_offset, y_offset = offset
        filtered_detections = []
        
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            
            # Adjust về full frame coordinates
            full_x1 = x1 + x_offset
            full_y1 = y1 + y_offset
            full_x2 = x2 + x_offset
            full_y2 = y2 + y_offset
            
            # Kiểm tra bounding box có nằm trong polygon không
            if self.is_bbox_in_polygon(full_x1, full_y1, full_x2, full_y2):
                filtered_detections.append((int(full_x1), int(full_y1), 
                                          int(full_x2), int(full_y2), conf, cls))
            else:
                center_x = (full_x1 + full_x2) // 2
                center_y = (full_y1 + full_y2) // 2
                print(f"  Filtered out detection at center ({center_x}, {center_y}) - outside polygon")
        
        return filtered_detections
    
    def draw_roi_overlay(self, frame: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Draw polygon ROI overlay on frame
        
        Args:
            frame (np.ndarray): Input frame
            alpha (float): Transparency of overlay
            
        Returns:
            np.ndarray: Frame with polygon ROI overlay
        """
        if not self.is_roi_set():
            return frame
        
        result = frame.copy()
        pts = np.array(self.points, dtype=np.int32)
        
        # Tạo overlay với polygon fill
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 255, 0))
        
        # Blend overlay với frame gốc
        cv2.addWeighted(overlay, alpha, result, 1 - alpha, 0, result)
        
        # Vẽ polygon border (màu đậm hơn)
        cv2.polylines(result, [pts], True, (0, 255, 0), 3)
        
        # Vẽ các điểm vertices
        for i, pt in enumerate(self.points):
            # Vẽ circle cho điểm
            cv2.circle(result, pt, 8, (0, 255, 0), -1)
            cv2.circle(result, pt, 10, (255, 255, 255), 2)
            
            # Label cho điểm
            label = f"P{i+1}"
            # Tính vị trí text để không bị che
            text_x = pt[0] + 15
            text_y = pt[1] - 10
            
            # Vẽ background cho text
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(result, (text_x - 2, text_y - text_h - 2), 
                         (text_x + text_w + 2, text_y + 2), (0, 0, 0), -1)
            
            # Vẽ text
            cv2.putText(result, label, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add polygon info
        if self.bounding_box:
            x1, y1, x2, y2 = self.bounding_box
            info_text = f"Polygon ROI ({len(self.points)} points) | BBox: ({x1},{y1})-({x2},{y2})"
            
            # Vẽ background cho info text
            (info_w, info_h), _ = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(result, (5, frame.shape[0] - 35), 
                         (info_w + 15, frame.shape[0] - 5), (0, 0, 0), -1)
            
            cv2.putText(result, info_text, (10, frame.shape[0] - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return result

