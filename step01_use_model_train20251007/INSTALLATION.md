# Hướng dẫn cài đặt - Traffic License Plate Detector

## Tính năng chính

- ✅ **Polygon ROI**: Chọn vùng quan tâm dạng tứ giác/đa giác
- ✅ **Interactive Selection**: Chọn ROI bằng chuột trực quan
- ✅ **Smart Filtering**: Tự động lọc detections nằm ngoài polygon
- ✅ **Real-time Display**: Hiển thị kết quả trong quá trình xử lý

## Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB+)
- **GPU**: Không bắt buộc nhưng khuyến nghị để tăng tốc xử lý
- **Dung lượng ổ cứng**: Đủ để lưu video đầu ra và hình ảnh biển số

## Bước 1: Cài đặt Python

1. Tải Python 3.8+ từ [python.org](https://www.python.org/downloads/)
2. Cài đặt với tùy chọn "Add Python to PATH"
3. Kiểm tra cài đặt:
   ```bash
   python --version
   pip --version
   ```

## Bước 2: Cài đặt các thư viện cần thiết

1. Mở Command Prompt hoặc PowerShell
2. Điều hướng đến thư mục dự án
3. Cài đặt các thư viện:
   ```bash
   pip install -r requirements.txt
   ```

### Cài đặt thủ công (nếu cần):
```bash
pip install ultralytics>=8.0.0
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install PyYAML>=6.0
pip install Pillow>=9.0.0
```

## Bước 3: Chuẩn bị mô hình YOLO

1. Đặt file mô hình (.pt) vào thư mục `models/`
2. Cập nhật đường dẫn mô hình trong config file:
   ```yaml
   model:
     path: "models/best.pt"
   ```

## Bước 4: Chuẩn bị video đầu vào

1. Đặt video giao thông vào thư mục `data/input/`
2. Hỗ trợ các định dạng: MP4, AVI, MOV, MKV

## Bước 5: Cấu hình ứng dụng

### Cấu hình Polygon ROI (Vùng quan tâm):

Có 2 cách để cấu hình Polygon ROI:

#### **Cách 1: Interactive Selection (Khuyến nghị)**

Chọn polygon bằng chuột trực tiếp trên video:

```yaml
roi:
  enabled: true
  mode: "polygon"
  interactive_selection: true  # Bật chế độ chọn bằng chuột
  max_points: 4  # Số điểm tối đa (3-6 điểm)
```

Khi chạy, bạn sẽ:
- **LEFT CLICK**: Thêm điểm mới
- **RIGHT CLICK**: Xóa điểm cuối
- **Nhấn 'r'**: Reset tất cả điểm
- **Nhấn ENTER**: Xác nhận polygon

#### **Cách 2: Config từ coordinates có sẵn**

Nếu bạn đã biết coordinates của polygon:

```yaml
roi:
  enabled: true
  mode: "polygon"
  interactive_selection: false
  points:
    - [200, 150]   # P1 (top-left)
    - [950, 100]   # P2 (top-right)
    - [1100, 650]  # P3 (bottom-right)
    - [100, 700]   # P4 (bottom-left)
  max_points: 4
```

### Cấu hình frame sampling:
```yaml
frame_sampling:
  skip_frames: 5  # Xử lý 1 frame mỗi 5 frames
```

### Cấu hình ngưỡng phát hiện:
```yaml
model:
  confidence_threshold: 0.6  # Ngưỡng tin cậy tối thiểu
  iou_threshold: 0.45        # Ngưỡng IoU cho NMS
```

### Cấu hình output:
```yaml
output:
  cropped_plates_dir: "data/output/cropped_plates_polygon"
  annotated_video_path: "data/output/annotated_video_polygon.mp4"
  plate_filename_prefix: "plate_"
  plate_filename_counter_start: 1
```

## Bước 6: Chạy ứng dụng

### **Chạy với Interactive Polygon Selection (Lần đầu):**

Chọn polygon ROI bằng chuột, sau đó tự động xử lý video:

```bash
python main.py data/input/road1_can_cao.mp4 --config config/config_polygon_example.yaml --interactive-roi
```

**Hướng dẫn:**
1. Cửa sổ video sẽ hiện ra
2. Click chuột trái 4 lần để chọn 4 điểm tạo polygon
3. Nhấn ENTER để xác nhận
4. Video sẽ được xử lý tự động với polygon đã chọn

### **Chạy với config có sẵn:**

Nếu bạn đã có polygon coordinates trong config:

```bash
python main.py data/input/road1_can_cao.mp4 --config config/config_polygon_saved.yaml
```

### **Các tùy chọn nâng cao:**

```bash
# Chọn frame khác để setup ROI (frame 100 thay vì frame 0)
python main.py data/input/video.mp4 --config config/config_polygon_example.yaml --interactive-roi --roi-frame 100

# Chọn polygon với 5 điểm thay vì 4
python main.py data/input/video.mp4 --config config/config_polygon_example.yaml --interactive-roi --max-points 5
```

### **Keyboard Controls trong quá trình xử lý:**

- **'q'**: Quit (thoát)
- **'p'**: Pause/Resume
- **'s'**: Save current frame
- **SPACE**: Process frame hiện tại ngay lập tức

## Bước 7: Kiểm tra kết quả

Sau khi chạy xong, kiểm tra:

1. **Hình ảnh biển số**: `data/output/cropped_plates_polygon/`
   - Format: `plate_001.jpg`, `plate_002.jpg`, ...
   - Chỉ chứa biển số nằm trong polygon ROI

2. **Video có chú thích**: `data/output/annotated_video_polygon.mp4`
   - Hiển thị polygon ROI màu xanh
   - Bounding boxes cho license plates detected
   - Frame info và detection count

## Xử lý sự cố

### Lỗi "Model not found":
- Kiểm tra file mô hình có tồn tại trong `models/`
- Kiểm tra đường dẫn trong config file
- Đảm bảo file `.pt` có trong thư mục `models/`

### Lỗi "Video not found":
- Kiểm tra đường dẫn video đầu vào
- Kiểm tra định dạng video có được hỗ trợ (MP4, AVI, MOV, MKV)
- Sử dụng đường dẫn tương đối từ thư mục project

### Lỗi "Module 'polygon_roi_manager' not found":
- Cài đặt lại các thư viện: `pip install -r requirements.txt`
- Kiểm tra Python path
- Đảm bảo đang chạy từ thư mục gốc của project

### Lỗi "Permission denied":
- Kiểm tra quyền ghi trong thư mục `data/output/`
- Chạy với quyền administrator nếu cần (Windows)
- Kiểm tra folder có bị lock bởi process khác không

### Polygon ROI không hiển thị:
- Kiểm tra `roi.enabled = true` trong config
- Kiểm tra `roi.mode = "polygon"` 
- Đảm bảo có ít nhất 3 điểm trong polygon
- Xem console output để check log

### Không detect được biển số:
- Kiểm tra polygon có bao phủ vùng cần detect không
- Thử giảm `confidence_threshold` xuống (ví dụ: 0.4)
- Kiểm tra model có được train đúng không
- Xem output video để verify polygon position

### Hiệu suất chậm:
- Tăng `skip_frames` trong cấu hình (xử lý ít frame hơn)
- Sử dụng GPU nếu có (CUDA)
- Chọn polygon nhỏ hơn (tối ưu bounding box)
- Giảm resolution video đầu vào

### Polygon bị sai vị trí sau khi chọn:
- Kiểm tra window có bị resize không (scale factor)
- Chọn lại polygon trên frame đầu tiên (frame 0)
- Đảm bảo coordinates được save đúng trong config

## Cấu trúc mô hình YOLO

Mô hình phải được huấn luyện để detect license plates.

**Lưu ý:**
- Model input: Video frames
- Model output: Bounding boxes với confidence scores
- Ứng dụng sẽ filter detections dựa trên polygon ROI

## Tips & Best Practices

### Chọn Polygon ROI hiệu quả:

1. **Chọn frame đại diện**: 
   - Dùng frame có xe để dễ visualize
   - Frame 0 hoặc frame giữa video thường tốt

2. **Chọn polygon theo hướng đường**:
   - Tận dụng perspective của camera
   - Loại trừ vỉa hè, cây cối, bóng đổ

3. **Tránh quá nhỏ hoặc quá lớn**:
   - Quá nhỏ: Mất detections
   - Quá lớn: Chậm và nhiều false positives

4. **Test và adjust**:
   - Xem output video để verify
   - Điều chỉnh nếu cần

### Tối ưu hóa Performance:

```yaml
# Cấu hình cho video tốc độ cao
frame_sampling:
  skip_frames: 10  # Xử lý ít frame hơn

model:
  confidence_threshold: 0.65  # Tăng để giảm false positives
```

```yaml
# Cấu hình cho accuracy cao
frame_sampling:
  skip_frames: 2  # Xử lý nhiều frame hơn

model:
  confidence_threshold: 0.5  # Giảm để catch nhiều plates
```

## Config Files

Project có sẵn các config files:

- **`config_polygon_example.yaml`**: Template với hướng dẫn chi tiết
- **`config_polygon_saved.yaml`**: Auto-generated sau interactive selection

**Khuyến nghị:**
1. Dùng `config_polygon_example.yaml` với `interactive_selection: true` lần đầu
2. Config sẽ tự động save với polygon coordinates
3. Lần sau dùng config đã save để chạy nhanh

## Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:

1. **Console output**: Xem log chi tiết
2. **Config file**: Verify format và values
3. **Video format**: Đảm bảo codec được hỗ trợ
4. **Python version**: Python 3.8+
5. **Dependencies**: `pip list` để check versions

**Debug tips:**
```bash
# Test import modules
python -c "from src.video_processor import VideoProcessor; print('OK')"

# Xem model info
python -c "from ultralytics import YOLO; model = YOLO('models/best.pt'); print(model.names)"
```

## Cấu trúc Project

```
step01_use_model_train20251007/
├── config/
│   ├── config_polygon_example.yaml   # Template
│   └── config_polygon_saved.yaml     # Auto-saved
├── data/
│   ├── input/                         # Videos input
│   └── output/                        # Results
├── models/
│   └── best.pt                        # YOLO model
├── src/
│   ├── model_inference.py
│   ├── polygon_roi_manager.py
│   ├── polygon_roi_selector.py
│   ├── utils.py
│   └── video_processor.py
├── main.py                            # Main entry point
└── requirements.txt
```
