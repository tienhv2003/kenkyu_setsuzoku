# 🚀 Quick Start Guide - Pipeline

## 5 phút để chạy pipeline hoàn chỉnh

### **Bước 1: Chuẩn bị**

```bash
# Kiểm tra đã cài đặt dependencies
pip install -r requirements.txt

# Kiểm tra model YOLO
ls models/best.pt

# Kiểm tra model Super Resolution
ls step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb
```

### **Bước 2: Chạy Pipeline**

```bash
# Chạy với video có sẵn
python run_pipeline.py data/input/road1_can_cao.mp4 --interactive-roi
```

**Interactive ROI Selection:**
1. Cửa sổ video sẽ hiện ra
2. Click chuột trái 4 lần để chọn 4 góc polygon ROI
3. Nhấn **ENTER** để xác nhận
4. Pipeline sẽ tự động chạy Step 1 → Step 2

### **Bước 3: Xem kết quả**

```bash
# Step 1 output (ảnh biển số thô)
ls data/output/cropped_plates_road1_can_cao_*/

# Step 2 output (ảnh đã enhance)
ls step02_use_edge_detection/data/plates_after_cut_super_resolution/road1_can_cao_*/
```

---

## Các lệnh thường dùng

### **Chạy full pipeline (tự động)**
```bash
python run_pipeline.py data/input/video.mp4
```

### **Chạy với ROI có sẵn (nhanh hơn)**
```bash
python run_pipeline.py data/input/video.mp4 --step1-config config/config_polygon_saved.yaml
```

### **Chạy lại Step 2 với ảnh có sẵn**
```bash
python run_step2_only.py data/output/cropped_plates_polygon
```

### **Chỉ detect, không enhance**
```bash
python run_pipeline.py data/input/video.mp4 --skip-step2
```

### **Chỉ enhance, không detect**
```bash
python run_pipeline.py --skip-step1 --step1-output data/output/cropped_plates_polygon
```

---

## Cấu trúc output

```
data/output/
├── cropped_plates_{run_name}/              ← Step 1: Ảnh biển số thô
└── annotated_video_{run_name}.mp4          ← Step 1: Video có annotations

step02_use_edge_detection/data/
├── plates_after_cut/{run_name}/            ← Step 2: Ảnh đã chỉnh perspective
└── plates_after_cut_super_resolution/      ← Step 2: Ảnh 4x super resolution
    └── {run_name}/
```

---

## Ví dụ workflow

```bash
# 1. Xử lý video mới
python run_pipeline.py data/input/new_video.mp4 --interactive-roi --run-name test01

# 2. Xem kết quả
ls data/output/cropped_plates_test01/
ls step02_use_edge_detection/data/plates_after_cut_super_resolution/test01/

# 3. Nếu không hài lòng với Step 2, chạy lại với params khác
python run_step2_only.py data/output/cropped_plates_test01 --output-name test01_v2
```

---

## Troubleshooting nhanh

**Lỗi model không tìm thấy:**
```bash
# Kiểm tra path
ls models/best.pt
ls step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb
```

**Không detect được gì:**
- Giảm confidence threshold trong config
- Chọn lại polygon ROI phù hợp hơn

**Pipeline chạy chậm:**
- Tăng `skip_frames` trong config Step 1
- Hoặc chỉ chạy super resolution: `--skip-auto-cut`

---

## Xem thêm

📖 [PIPELINE_README.md](PIPELINE_README.md) - Tài liệu đầy đủ
📖 [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn cài đặt
📖 [README.md](README.md) - Tài liệu Step 1

