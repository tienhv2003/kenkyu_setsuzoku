"""
YOLO Model Inference Module
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional


class LicensePlateDetector:
    """
    YOLO-based license plate detector
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.6, iou_threshold: float = 0.45):
        """
        Initialize the detector
        
        Args:
            model_path (str): Path to the trained YOLO model
            confidence_threshold (float): Minimum confidence for detections
            iou_threshold (float): IoU threshold for NMS
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """
        Load the YOLO model
        """
        try:
            self.model = YOLO(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {self.model_path}: {e}")
    
    def detect_license_plates(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float, int]]:
        """
        Detect license plates in a frame
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            List[Tuple]: List of detections (x1, y1, x2, y2, confidence, class_id)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold, iou=self.iou_threshold)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates and properties
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Only process license plate detections (class 0)
                        if class_id == 0:  # license_plate class
                            detections.append((int(x1), int(y1), int(x2), int(y2), float(confidence), class_id))
            
            return detections
            
        except Exception as e:
            print(f"Error during detection: {e}")
            return []
    
    def crop_license_plate(self, frame: np.ndarray, detection: Tuple[int, int, int, int, float, int]) -> Optional[np.ndarray]:
        """
        Crop license plate from frame based on detection
        
        Args:
            frame (np.ndarray): Input frame
            detection (Tuple): Detection tuple (x1, y1, x2, y2, confidence, class_id)
            
        Returns:
            Optional[np.ndarray]: Cropped license plate image or None
        """
        x1, y1, x2, y2, _, _ = detection
        
        # Ensure coordinates are within frame bounds
        height, width = frame.shape[:2]
        x1 = max(0, min(x1, width))
        y1 = max(0, min(y1, height))
        x2 = max(x1, min(x2, width))
        y2 = max(y1, min(y2, height))
        
        # Add some padding around the detection
        padding = 5
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)
        
        # Crop the license plate
        cropped = frame[y1:y2, x1:x2]
        
        # Check if cropped image is valid
        if cropped.size > 0:
            return cropped
        
        return None
    
    def draw_detections(self, frame: np.ndarray, detections: List[Tuple[int, int, int, int, float, int]]) -> np.ndarray:
        """
        Draw detection boxes on frame
        
        Args:
            frame (np.ndarray): Input frame
            detections (List[Tuple]): List of detections
            
        Returns:
            np.ndarray: Frame with drawn detections
        """
        annotated_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2, confidence, class_id = detection
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label and confidence
            label = f"License Plate: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Draw background for text
            cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # Draw text
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return annotated_frame
