"""
Polygon ROI Selector Module
Cho phép người dùng chọn ROI dạng polygon bằng cách click các điểm trên video
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


class PolygonROISelector:
    """
    Interactive Polygon ROI selector sử dụng mouse callback
    Người dùng click để thêm điểm, tạo thành polygon
    """
    
    def __init__(self, window_name: str = "Select Polygon ROI", max_points: int = 4):
        """
        Initialize Polygon ROI selector
        
        Args:
            window_name (str): Tên cửa sổ hiển thị
            max_points (int): Số điểm tối đa (mặc định 4 cho tứ giác)
        """
        self.window_name = window_name
        self.max_points = max_points
        self.points = []  # List of (x, y) tuples
        self.current_frame = None
        self.scale_factor = 1.0  # Scale factor for coordinate adjustment
        
        # Setup mouse callback
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1200, 800)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
    
    def mouse_callback(self, event: int, x: int, y: int, flags: int, param) -> None:
        """
        Mouse callback function để xử lý click
        
        Args:
            event: Mouse event type
            x, y: Mouse coordinates (trên display frame đã resize)
            flags: Mouse flags
            param: Additional parameters
        """
        # Điều chỉnh coordinates về frame gốc
        orig_x = int(x / self.scale_factor)
        orig_y = int(y / self.scale_factor)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Left click: Thêm điểm
            if len(self.points) < self.max_points:
                self.points.append((orig_x, orig_y))
                print(f"Điểm {len(self.points)}: ({orig_x}, {orig_y})")
            else:
                print(f"Đã đủ {self.max_points} điểm! Nhấn 'r' để reset hoặc ENTER để xác nhận.")
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click: Xóa điểm cuối cùng
            if self.points:
                removed = self.points.pop()
                print(f"Đã xóa điểm: {removed}")
    
    def get_polygon_points(self) -> Optional[List[Tuple[int, int]]]:
        """
        Lấy danh sách các điểm của polygon
        
        Returns:
            List of (x, y) tuples hoặc None nếu chưa đủ điểm
        """
        if len(self.points) >= 3:
            return self.points
        return None
    
    def draw_polygon_preview(self, frame: np.ndarray) -> np.ndarray:
        """
        Vẽ preview polygon trên frame
        
        Args:
            frame (np.ndarray): Frame để vẽ
            
        Returns:
            np.ndarray: Frame với polygon preview
        """
        display_frame = frame.copy()
        
        # Vẽ các điểm đã chọn
        for i, pt in enumerate(self.points):
            cv2.circle(display_frame, pt, 8, (0, 255, 0), -1)
            cv2.circle(display_frame, pt, 10, (255, 255, 255), 2)
            
            # Label cho điểm
            label = f"P{i+1}"
            cv2.putText(display_frame, label, (pt[0]+15, pt[1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Vẽ các cạnh nối giữa các điểm
        if len(self.points) > 1:
            for i in range(len(self.points)):
                pt1 = self.points[i]
                pt2 = self.points[(i+1) % len(self.points)]
                cv2.line(display_frame, pt1, pt2, (0, 255, 0), 2)
        
        # Tô màu semi-transparent cho vùng polygon (nếu có >= 3 điểm)
        if len(self.points) >= 3:
            overlay = display_frame.copy()
            pts = np.array(self.points, dtype=np.int32)
            cv2.fillPoly(overlay, [pts], (0, 255, 0))
            cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0, display_frame)
        
        # Hiển thị hướng dẫn
        instructions = [
            f"Da chon: {len(self.points)}/{self.max_points} diem",
            "LEFT CLICK: Them diem",
            "RIGHT CLICK: Xoa diem cuoi",
            "ENTER: Xac nhan (can >= 3 diem)",
            "'r': Reset tat ca",
            "ESC: Huy",
            f"Scale: {self.scale_factor:.2f}x"
        ]
        
        # Vẽ background cho text
        bg_height = len(instructions) * 30 + 20
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (5, 5), (400, bg_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
        
        # Vẽ text hướng dẫn
        for i, instruction in enumerate(instructions):
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            cv2.putText(display_frame, instruction, (10, 30 + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return display_frame
    
    def select_roi_from_video(self, video_path: str, frame_number: int = 0) -> Optional[List[Tuple[int, int]]]:
        """
        Chọn Polygon ROI từ video bằng cách hiển thị frame và cho phép người dùng chọn
        
        Args:
            video_path (str): Đường dẫn đến video
            frame_number (int): Số frame để hiển thị (0 = frame đầu tiên)
            
        Returns:
            List of (x, y) tuples representing polygon vertices hoặc None
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Không thể mở video: {video_path}")
            return None
        
        # Đọc frame được chỉ định
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print(f"Không thể đọc frame {frame_number} từ video")
            return None
        
        self.current_frame = frame
        
        print(f"\n{'='*50}")
        print(f"   POLYGON ROI SELECTION MODE")
        print(f"{'='*50}")
        print(f"Video: {video_path}")
        print(f"Frame: {frame_number}")
        print(f"Max points: {self.max_points}")
        print(f"\nHướng dẫn:")
        print("  - LEFT CLICK để thêm điểm")
        print("  - RIGHT CLICK để xóa điểm cuối")
        print("  - Nhấn ENTER để xác nhận (cần ít nhất 3 điểm)")
        print("  - Nhấn 'r' để reset")
        print("  - Nhấn ESC để hủy")
        print(f"{'='*50}\n")
        
        while True:
            # Vẽ preview polygon
            display_frame = self.draw_polygon_preview(frame)
            
            # Resize frame để hiển thị tốt hơn và lưu scale factor
            height, width = display_frame.shape[:2]
            if width > 1200:
                self.scale_factor = 1200 / width
                new_width = int(width * self.scale_factor)
                new_height = int(height * self.scale_factor)
                display_frame = cv2.resize(display_frame, (new_width, new_height))
            else:
                self.scale_factor = 1.0
            
            cv2.imshow(self.window_name, display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 13:  # ENTER key
                polygon_points = self.get_polygon_points()
                if polygon_points:
                    print(f"\n✓ Polygon ROI đã được chọn với {len(polygon_points)} điểm:")
                    for i, pt in enumerate(polygon_points):
                        print(f"    P{i+1}: {pt}")
                    cv2.destroyWindow(self.window_name)
                    return polygon_points
                else:
                    print("⚠ Vui lòng chọn ít nhất 3 điểm trước khi xác nhận!")
            
            elif key == ord('r'):  # Reset
                self.points = []
                print("✓ Đã reset tất cả điểm")
            
            elif key == 27:  # ESC key
                print("✗ Đã hủy Polygon ROI selection")
                cv2.destroyWindow(self.window_name)
                return None
        
        cv2.destroyWindow(self.window_name)
        return None
    
    def select_roi_from_frame(self, frame: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        Chọn Polygon ROI từ frame cụ thể
        
        Args:
            frame (np.ndarray): Frame để chọn ROI
            
        Returns:
            List of (x, y) tuples representing polygon vertices hoặc None
        """
        self.current_frame = frame
        
        print(f"\n{'='*50}")
        print(f"   POLYGON ROI SELECTION MODE")
        print(f"{'='*50}")
        print(f"Max points: {self.max_points}")
        print(f"\nHướng dẫn:")
        print("  - LEFT CLICK để thêm điểm")
        print("  - RIGHT CLICK để xóa điểm cuối")
        print("  - Nhấn ENTER để xác nhận (cần ít nhất 3 điểm)")
        print("  - Nhấn 'r' để reset")
        print("  - Nhấn ESC để hủy")
        print(f"{'='*50}\n")
        
        while True:
            # Vẽ preview polygon
            display_frame = self.draw_polygon_preview(frame)
            
            # Resize frame để hiển thị tốt hơn và lưu scale factor
            height, width = display_frame.shape[:2]
            if width > 1200:
                self.scale_factor = 1200 / width
                new_width = int(width * self.scale_factor)
                new_height = int(height * self.scale_factor)
                display_frame = cv2.resize(display_frame, (new_width, new_height))
            else:
                self.scale_factor = 1.0
            
            cv2.imshow(self.window_name, display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 13:  # ENTER key
                polygon_points = self.get_polygon_points()
                if polygon_points:
                    print(f"\n✓ Polygon ROI đã được chọn với {len(polygon_points)} điểm:")
                    for i, pt in enumerate(polygon_points):
                        print(f"    P{i+1}: {pt}")
                    cv2.destroyWindow(self.window_name)
                    return polygon_points
                else:
                    print("⚠ Vui lòng chọn ít nhất 3 điểm trước khi xác nhận!")
            
            elif key == ord('r'):  # Reset
                self.points = []
                print("✓ Đã reset tất cả điểm")
            
            elif key == 27:  # ESC key
                print("✗ Đã hủy Polygon ROI selection")
                cv2.destroyWindow(self.window_name)
                return None
        
        cv2.destroyWindow(self.window_name)
        return None


def select_polygon_roi_interactive(video_path: str, frame_number: int = 0, max_points: int = 4) -> Optional[List[Tuple[int, int]]]:
    """
    Hàm tiện ích để chọn Polygon ROI interactive từ video
    
    Args:
        video_path (str): Đường dẫn đến video
        frame_number (int): Số frame để hiển thị
        max_points (int): Số điểm tối đa
        
    Returns:
        List of (x, y) tuples hoặc None
    """
    selector = PolygonROISelector(max_points=max_points)
    return selector.select_roi_from_video(video_path, frame_number)


def select_polygon_roi_from_frame(frame: np.ndarray, max_points: int = 4) -> Optional[List[Tuple[int, int]]]:
    """
    Hàm tiện ích để chọn Polygon ROI từ frame
    
    Args:
        frame (np.ndarray): Frame để chọn ROI
        max_points (int): Số điểm tối đa
        
    Returns:
        List of (x, y) tuples hoặc None
    """
    selector = PolygonROISelector(max_points=max_points)
    return selector.select_roi_from_frame(frame)

