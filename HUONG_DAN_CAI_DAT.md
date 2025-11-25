# Hướng dẫn Cài đặt Môi trường

## Yêu cầu

- Python 3.8 trở lên
- Các thư viện Python cần thiết

## Cài đặt

### Bước 1: Kiểm tra Python

Mở Command Prompt hoặc PowerShell và chạy:

```
python --version
```

Phải hiển thị Python 3.8.x hoặc cao hơn.

### Bước 2: Cài đặt các thư viện

Chạy lệnh sau để cài đặt tất cả thư viện cần thiết:

```
pip install -r requirements.txt
```

**Lưu ý quan trọng:** Project này cần `opencv-contrib-python` (không phải `opencv-python`) để có module super resolution.

Nếu bạn đã cài `opencv-python`, hãy gỡ bỏ trước:

```
pip uninstall opencv-python
pip install opencv-contrib-python
```

### Bước 3: Kiểm tra cài đặt

Kiểm tra các module đã cài đặt đúng:

```
python -c "from ultralytics import YOLO; print('OK')"
python -c "import cv2; import cv2.dnn_superres; print('OK')"
python -c "import numpy, yaml, PIL; print('OK')"
```

Nếu tất cả đều hiển thị "OK" thì môi trường đã sẵn sàng.

## Cấu trúc Project

- `step01_use_model_train20251007/` - Phát hiện biển số bằng YOLO
- `step02_use_edge_detection/` - Tăng cường chất lượng ảnh
- `step03_feature_extractor_matcher/` - Trích xuất đặc trưng
- `run_pipeline.py` - Chạy toàn bộ pipeline

## Models

Đảm bảo các file model đã có:
- `step01_use_model_train20251007/models/best.pt` - Model YOLO
- `step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb` - Model super resolution

## Sử dụng

Xem file `README.md` và `QUICKSTART.md` để biết cách sử dụng.

