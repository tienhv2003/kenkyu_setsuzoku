# CURSOR: DO NOT MODIFY THIS FILE
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
    
    def __init__(self, points: Optional[List[Tuple[int, int]]] = None):
        """
        Initialize Polygon ROI manager with points
        
        Args:
            points: List of (x, y) tuples defining polygon vertices
                   e.g., [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                   If None, ROI will be set interactively
        """
        self.points = None
        self.points_array = None  # Cached numpy array
        self.mask = None
        self.mask_shape = None  # Track mask dimensions
        self.bounding_box = None
        
        if points:
            self.set_points(points)
    
    def set_points(self, points: List[Tuple[int, int]]) -> None:
        """
        Set polygon points manually
        
        Args:
            points: List of (x, y) tuples (minimum 3 points)
        
        Raises:
            ValueError: If less than 3 points provided
        """
        if not points or len(points) < 3:
            raise ValueError("Polygon cần ít nhất 3 điểm")
        
        self.points = points
        self.points_array = np.array(points, dtype=np.int32)  # Cache
        self.mask = None  # Reset mask - will be recreated on next filter
        self.mask_shape = None
        self._calculate_bounding_box()
    
    def set_roi_from_video(self, video_path: str, frame_number: int = 0, 
                          max_points: int = 4) -> bool:
        """
        Set ROI bằng cách chọn interactive từ video
        
        Args:
            video_path: Đường dẫn đến video
            frame_number: Số frame để hiển thị
            max_points: Số điểm tối đa
            
        Returns:
            True nếu ROI được chọn thành công
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
            frame: Frame để chọn ROI
            max_points: Số điểm tối đa
            
        Returns:
            True nếu ROI được chọn thành công
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
            True nếu ROI đã được set
        """
        return self.points is not None and len(self.points) >= 3
    
    def _calculate_bounding_box(self) -> None:
        """
        Tính bounding box của polygon để optimize processing
        """
        if not self.points:
            return
        
        x_coords = self.points_array[:, 0]
        y_coords = self.points_array[:, 1]
        
        self.bounding_box = (
            int(np.min(x_coords)),
            int(np.min(y_coords)),
            int(np.max(x_coords)),
            int(np.max(y_coords))
        )
        
        print(f"Polygon bounding box: {self.bounding_box}")
    
    def _ensure_mask(self, frame_shape: Tuple[int, int]) -> None:
        """
        Đảm bảo mask được tạo với đúng frame shape
        Tự động tạo mask nếu chưa có hoặc shape thay đổi
        
        Args:
            frame_shape: (height, width) của frame
        """
        if not self.is_roi_set():
            return
        
        height, width = frame_shape[:2]
        
        # Tạo mask mới nếu chưa có hoặc shape thay đổi
        if self.mask is None or self.mask_shape != (height, width):
            self.mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(self.mask, [self.points_array], 255)
            self.mask_shape = (height, width)
            print(f"Created mask with shape: {self.mask_shape}")
    
    def is_point_in_polygon(self, x: int, y: int) -> bool:
        """
        Kiểm tra điểm có nằm trong polygon không
        Utility method cho single point check
        
        Args:
            x, y: Point coordinates
            
        Returns:
            True if point is inside polygon
        """
        if not self.is_roi_set():
            return True
        
        result = cv2.pointPolygonTest(self.points_array, (float(x), float(y)), False)
        return result >= 0
    
    def is_bbox_in_polygon(self, x1: int, y1: int, x2: int, y2: int, 
                          threshold: float = 0.8) -> bool:
        """
        Kiểm tra bbox có đủ overlap với polygon không (mask-based)
        
        Args:
            x1, y1, x2, y2: Bounding box coordinates
            threshold: Tỷ lệ overlap tối thiểu (0.0-1.0)
            
        Returns:
            True if overlap ratio >= threshold
        """
        if not self.is_roi_set():
            return True
        
        if self.mask is None:
            raise RuntimeError(
                "Mask chưa được tạo! Gọi filter_detections() với frame_shape "
                "hoặc _ensure_mask() trước."
            )
        
        # Quick rejection using bounding box
        if self.bounding_box:
            bbox_x1, bbox_y1, bbox_x2, bbox_y2 = self.bounding_box
            if x2 < bbox_x1 or x1 > bbox_x2 or y2 < bbox_y1 or y1 > bbox_y2:
                return False  # Completely outside polygon bbox
        
        # Clamp bbox to mask bounds
        h, w = self.mask.shape
        x1_clamp = max(0, min(x1, w))
        y1_clamp = max(0, min(y1, h))
        x2_clamp = max(0, min(x2, w))
        y2_clamp = max(0, min(y2, h))
        
        if x1_clamp >= x2_clamp or y1_clamp >= y2_clamp:
            return False  # Invalid bbox after clamping
        
        # Calculate overlap ratio
        patch = self.mask[y1_clamp:y2_clamp, x1_clamp:x2_clamp]
        if patch.size == 0:
            return False
        
        overlap_ratio = np.count_nonzero(patch) / patch.size
        return overlap_ratio >= threshold

    def filter_detections(
        self, 
        detections: List[Tuple[int, int, int, int, float, int]],
        frame_shape: Optional[Tuple[int, int]] = None,
        threshold: float = 0.8
    ) -> List[Tuple[int, int, int, int, float, int]]:
        """
        Lọc detections dựa trên mask polygon
        
        Args:
            detections: List of (x1, y1, x2, y2, confidence, class_id)
            frame_shape: (height, width) - required nếu mask chưa được tạo
            threshold: Tỷ lệ overlap tối thiểu (0.0-1.0)
            
        Returns:
            Filtered list of detections
            
        Raises:
            ValueError: If mask chưa có và frame_shape is None
        """
        if not self.is_roi_set():
            return detections
        
        # Ensure mask exists
        if self.mask is None:
            if frame_shape is None:
                raise ValueError(
                    "frame_shape cần thiết để tạo mask lần đầu. "
                    "Truyền frame_shape=(height, width) vào."
                )
            self._ensure_mask(frame_shape)
        
        filtered = []
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            if self.is_bbox_in_polygon(x1, y1, x2, y2, threshold):
                filtered.append(det)
        
        return filtered
    
    def draw_roi_overlay(self, frame: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Draw polygon ROI overlay on frame
        
        Args:
            frame: Input frame
            alpha: Transparency of overlay (0.0-1.0)
            
        Returns:
            Frame with polygon ROI overlay
        """
        if not self.is_roi_set():
            return frame
        
        # Ensure mask is created for this frame size
        self._ensure_mask(frame.shape[:2])
        
        result = frame.copy()
        
        # Create colored overlay using mask
        overlay = frame.copy()
        overlay[self.mask == 255] = (0, 255, 0)  # Green inside polygon
        
        # Blend overlay with original
        cv2.addWeighted(overlay, alpha, result, 1 - alpha, 0, result)
        
        # Draw polygon border
        cv2.polylines(result, [self.points_array], True, (0, 255, 0), 3)
        
        # Draw vertices
        for i, pt in enumerate(self.points):
            cv2.circle(result, pt, 8, (0, 255, 0), -1)
            cv2.circle(result, pt, 10, (255, 255, 255), 2)
            
            # Label
            label = f"P{i+1}"
            text_x = pt[0] + 15
            text_y = pt[1] - 10
            
            # Text background
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(result, (text_x - 2, text_y - text_h - 2), 
                         (text_x + text_w + 2, text_y + 2), (0, 0, 0), -1)
            
            cv2.putText(result, label, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add info text
        if self.bounding_box:
            x1, y1, x2, y2 = self.bounding_box
            mask_info = f" | Mask: {self.mask_shape}" if self.mask_shape else ""
            info_text = f"Polygon ROI ({len(self.points)} points) | BBox: ({x1},{y1})-({x2},{y2}){mask_info}"
            
            (info_w, info_h), _ = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(result, (5, frame.shape[0] - 30), 
                         (info_w + 15, frame.shape[0] - 5), (0, 0, 0), -1)
            
            cv2.putText(result, info_text, (10, frame.shape[0] - 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return result