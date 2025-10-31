# Traffic License Plate Detector

Ứng dụng Python để phát hiện và trích xuất biển số xe từ video giao thông sử dụng mô hình YOLO tùy chỉnh.

## Tính năng chính

- **Phát hiện biển số xe**: Sử dụng mô hình YOLO đã được huấn luyện để phát hiện biển số xe
- **Xử lý ROI**: Chỉ xử lý vùng quan tâm (Region of Interest) để tối ưu hiệu suất
- **Lấy mẫu frame**: Xử lý một frame mỗi N frames để tối ưu hiệu suất
- **Trích xuất biển số**: Tự động cắt và lưu hình ảnh biển số được phát hiện
- **Video có chú thích**: Tạo video đầu ra với các hộp giới hạn và nhãn

## Cấu trúc dự án

```
traffic_license_plate_detector/
├── src/                    # Mã nguồn chính
│   ├── __init__.py
│   ├── video_processor.py  # Xử lý video chính
│   ├── model_inference.py  # Suy luận mô hình YOLO
│   ├── roi_manager.py      # Quản lý vùng quan tâm
│   └── utils.py           # Các hàm tiện ích
├── models/                 # Thư mục chứa mô hình
│   └── your_trained_model.pt
├── data/
│   ├── input/             # Video đầu vào
│   └── output/            # Kết quả đầu ra
│       ├── cropped_plates/ # Hình ảnh biển số đã cắt
│       └── annotated_video.mp4
├── config/
│   └── config.yaml        # File cấu hình
├── requirements.txt       # Các thư viện cần thiết
└── main.py               # File chính để chạy ứng dụng
```

## Cài đặt

1. **Cài đặt Python 3.8+**

2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Đặt mô hình YOLO của bạn:**
   - Đặt file mô hình (.pt) vào thư mục `models/`
   - Cập nhật đường dẫn mô hình trong `config/config.yaml`

## Cấu hình

Chỉnh sửa file `config/config.yaml` để tùy chỉnh:

- **ROI (Vùng quan tâm)**: Định nghĩa vùng xử lý trong video
- **Frame sampling**: Số frame bỏ qua giữa các lần xử lý
- **Ngưỡng tin cậy**: Ngưỡng tối thiểu cho phát hiện biển số
- **Đường dẫn đầu ra**: Nơi lưu kết quả

## Sử dụng

### Chạy cơ bản:
```bash
python main.py data/input/traffic_video.mp4
```

### Sử dụng file cấu hình tùy chỉnh:
```bash
python main.py --config config/custom_config.yaml data/input/traffic_video.mp4
```

## Kết quả đầu ra

1. **Hình ảnh biển số đã cắt**: Lưu trong `data/output/cropped_plates/`
   - Tên file: `plate_001.jpg`, `plate_002.jpg`, ...
   - Chỉ lưu các biển số có độ tin cậy > ngưỡng đã cấu hình

2. **Video có chú thích**: Lưu trong `data/output/annotated_video.mp4`
   - Hiển thị hộp giới hạn quanh biển số được phát hiện
   - Hiển thị vùng ROI (nếu được bật)
   - Hiển thị nhãn và điểm tin cậy

## Cấu trúc mô hình

Mô hình YOLO phải được huấn luyện với 2 lớp:
- **Class 0**: license_plate
- **Class 1**: car

Ứng dụng chỉ xử lý các phát hiện của class 0 (license_plate).

## Xử lý lỗi

- Kiểm tra đường dẫn video đầu vào
- Kiểm tra file mô hình có tồn tại
- Kiểm tra quyền ghi trong thư mục đầu ra
- Kiểm tra cấu hình ROI có hợp lệ

## Yêu cầu hệ thống

- Python 3.8+
- RAM: Tối thiểu 4GB (khuyến nghị 8GB+)
- GPU: Không bắt buộc nhưng khuyến nghị để tăng tốc xử lý
- Dung lượng ổ cứng: Đủ để lưu video đầu ra và hình ảnh biển số

## Ghi chú

- Ứng dụng được thiết kế để xử lý video giao thông thực tế
- ROI giúp loại bỏ các vùng không liên quan (logo, chữ trên màn hình, v.v.)
- Frame sampling giúp tối ưu hiệu suất xử lý
- Tất cả các tham số có thể được tùy chỉnh thông qua file cấu hình
