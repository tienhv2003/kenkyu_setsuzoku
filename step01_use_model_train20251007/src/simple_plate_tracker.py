"""
Simple License Plate Tracker
Tracking biển số qua các frames để loại bỏ duplicate
Phiên bản đơn giản: chỉ theo dõi 1 biển số chính tại một thời điểm (one-track-at-a-time)
Sử dụng IoU matching giữa frame hiện tại và track active
"""

import numpy as np
from typing import List, Tuple, Optional


class Track:
    """
    Đại diện cho một track (biển số được theo dõi qua nhiều frames)
    """
    
    def __init__(self, track_id: int, detection: Tuple, frame_number: int):
        """
        Initialize track
        
        Args:
            track_id: ID duy nhất của track
            detection: (x1, y1, x2, y2, confidence, class_id)
            frame_number: Frame số khi track được tạo
        """
        self.track_id = track_id
        self.bbox = list(detection[:4])  # [x1, y1, x2, y2]
        self.confidence = detection[4]
        
        # Track state
        self.hits = 1           # Số lần được detect
        self.age = 0            # Số frames kể từ lần detect cuối
        self.state = 'tentative'  # tentative → confirmed → deleted
        
        # Best frame tracking
        self.best_confidence = self.confidence
        self.best_bbox = list(self.bbox)
        self.best_frame_number = frame_number
        self.best_cropped = None  # Lưu ảnh crop tốt nhất
        
        # Metadata
        self.first_frame = frame_number
        self.last_frame = frame_number
    
    def update(self, detection: Tuple, frame_number: int) -> None:
        """
        Cập nhật track với detection mới
        
        Args:
            detection: (x1, y1, x2, y2, confidence, class_id)
            frame_number: Frame số hiện tại
        """
        self.bbox = list(detection[:4])
        self.confidence = detection[4]
        self.hits += 1
        self.age = 0  # Reset age
        self.last_frame = frame_number
        
        # Cập nhật best frame nếu confidence tốt hơn
        if self.confidence > self.best_confidence:
            self.best_confidence = self.confidence
            self.best_bbox = list(self.bbox)
            self.best_frame_number = frame_number
    
    def mark_missing(self) -> None:
        """Đánh dấu track không được detect ở frame này"""
        self.age += 1
    
    def is_confirmed(self, min_hits: int) -> bool:
        """Kiểm tra track đã được confirm chưa"""
        return self.hits >= min_hits
    
    def should_delete(self, max_age: int) -> bool:
        """Kiểm tra track có nên bị xóa không"""
        return self.age > max_age


class SimplePlateTracker:
    """
    Simple tracker chỉ theo dõi 1 biển số chính tại một thời điểm
    Phù hợp với video xe đi lần lượt qua khung hình
    """
    
    def __init__(self, max_age: int = 8, min_hits: int = 2, 
                 iou_threshold: float = 0.35):
        """
        Initialize tracker
        
        Args:
            max_age: Số frames tối đa không detect trước khi xóa track
            min_hits: Số lần detect tối thiểu để track được confirmed
            iou_threshold: Ngưỡng IoU để match detection với track
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        
        # Chỉ một track đang active tại một thời điểm
        self.active_track: Optional[Track] = None
        self.next_id = 1
        
        print("SimplePlateTracker initialized (one-track-at-a-time):")
        print(f"  max_age={max_age}, min_hits={min_hits}, iou_threshold={iou_threshold}")
    
    def update(self, detections: List[Tuple], frame_number: int) -> Tuple[List[Track], List[Track]]:
        """
        Cập nhật tracker với detections từ frame mới (theo dõi 1 track duy nhất)
        
        Args:
            detections: List of (x1, y1, x2, y2, confidence, class_id)
            frame_number: Frame số hiện tại
        
        Returns:
            active_tracks: [active_track] nếu đang có track, ngược lại []
            completed_tracks: List các tracks vừa hoàn thành (cần lưu)
        """
        completed: List[Track] = []

        # Trường hợp 1: chưa có track active
        if self.active_track is None:
            if not detections:
                return [], []
            
            # Chọn detection "tốt nhất" làm biển số chính (confidence cao nhất)
            best_det = max(detections, key=lambda d: d[4])
            self.active_track = Track(self.next_id, best_det, frame_number)
            self.next_id += 1
            return [self.active_track], []

        # Trường hợp 2: đã có track active → cố gắng match với detections hiện tại
        if detections:
            best_iou = 0.0
            best_det: Optional[Tuple] = None
            
            for det in detections:
                iou = self._calculate_iou(det[:4], self.active_track.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_det = det
            
            if best_det is not None and best_iou >= self.iou_threshold:
                # Match tốt → cập nhật track
                self.active_track.update(best_det, frame_number)
            else:
                # Không match detection nào đủ tốt
                self.active_track.mark_missing()
        else:
            # Không có detection nào trong frame
            self.active_track.mark_missing()

        # Kiểm tra xem track active có nên kết thúc không
        if self.active_track.should_delete(self.max_age):
            finished = self.active_track
            self.active_track = None
            
            if finished.is_confirmed(self.min_hits):
                completed.append(finished)
        
        active_tracks = [self.active_track] if self.active_track is not None else []
        return active_tracks, completed
    
    @staticmethod
    def _calculate_iou(bbox1: List, bbox2: List) -> float:
        """
        Tính IoU giữa 2 bounding boxes
        
        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]
        
        Returns:
            IoU value (0-1)
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def get_active_track_count(self) -> int:
        """Lấy số lượng tracks đang active"""
        return 1 if self.active_track is not None else 0
    
    def get_stats(self) -> dict:
        """Lấy thống kê tracker"""
        confirmed = 0
        if self.active_track is not None and self.active_track.is_confirmed(self.min_hits):
            confirmed = 1
        return {
            'active_tracks': self.get_active_track_count(),
            'next_id': self.next_id,
            'confirmed_tracks': confirmed,
        }

