# Pipeline - Hệ thống xử lý biển số xe tự động

## 📖 Tổng quan

Pipeline này kết nối 2 bước xử lý tự động:
- **Step 1**: Phát hiện và cắt biển số từ video (YOLO + Polygon ROI)
- **Step 2**: Nâng cao chất lượng ảnh (Auto-cut + Super Resolution)

```
Video giao thông
      ↓
[Step 1: YOLO Detection]
  ✓ Detect biển số với YOLO
  ✓ Filter với Polygon ROI
  ✓ Lưu ảnh biển số đã cắt
      ↓
Ảnh biển số thô
      ↓
[Step 2: Enhancement]
  ✓ Auto-cut với Canny edge detection
  ✓ Chỉnh perspective distortion
  ✓ Super Resolution 4x
      ↓
Ảnh biển số chất lượng cao
```

---

## 🚀 Cách sử dụng

### **1. Chạy Full Pipeline (Step 1 → Step 2)**

```bash
# Cách đơn giản nhất
python run_pipeline.py data/input/road1_can_cao.mp4

# Với interactive ROI selection
python run_pipeline.py data/input/road1_can_cao.mp4 --interactive-roi

# Với tên run tùy chỉnh
python run_pipeline.py data/input/road1_can_cao.mp4 --run-name test_20241030
```

**Kết quả:**
- Step 1 output: `data/output/cropped_plates_{run_name}/`
- Step 2 cut: `step02_use_edge_detection/data/plates_after_cut/{run_name}/`
- Step 2 SR: `step02_use_edge_detection/data/plates_after_cut_super_resolution/{run_name}/`

---

### **2. Chạy chỉ Step 1 (Detection)**

```bash
# Chạy Step 1 thông thường
python main.py data/input/road1_can_cao.mp4

# Với interactive ROI selection
python main.py data/input/road1_can_cao.mp4 --interactive-roi

# Với config tùy chỉnh
python main.py data/input/video.mp4 --config config/my_config.yaml
```

---

### **3. Chạy chỉ Step 2 (Enhancement)**

Nếu bạn đã có ảnh biển số từ Step 1 hoặc nguồn khác:

```bash
# Cách 1: Dùng script standalone
python run_step2_only.py data/output/cropped_plates_polygon

# Cách 2: Chạy trực tiếp
cd step02_use_edge_detection
python main.py --input ../data/output/cropped_plates_polygon

# Chỉ auto-cut, bỏ qua super resolution
python run_step2_only.py data/output/cropped_plates_polygon --skip-super-resolution

# Chỉ super resolution, bỏ qua auto-cut
python run_step2_only.py data/output/cropped_plates_polygon --skip-auto-cut
```

---

### **4. Pipeline với Step 1 đã chạy sẵn**

Nếu bạn đã chạy Step 1 trước đó:

```bash
# Chỉ chạy Step 2 với output có sẵn
python run_pipeline.py --skip-step1 --step1-output data/output/cropped_plates_polygon
```

---

## ⚙️ Cấu hình

### **Config cho Step 1** (`config/config_polygon_example.yaml`)

```yaml
roi:
  enabled: true
  mode: "polygon"
  interactive_selection: true  # Chọn ROI bằng chuột
  points:  # Hoặc định nghĩa sẵn points
    - [200, 150]
    - [950, 100]
    - [1100, 650]
    - [100, 700]

model:
  path: "models/best.pt"
  confidence_threshold: 0.6

output:
  cropped_plates_dir: "data/output/cropped_plates_polygon"
  annotated_video_path: "data/output/annotated_video_polygon.mp4"
```

### **Config cho Step 2** (`step02_use_edge_detection/config.yaml`)

```yaml
paths:
  input_dir: "../data/output/cropped_plates_polygon"
  output_cut_dir: "data/plates_after_cut/auto"
  output_super_resolution_dir: "data/plates_after_cut_super_resolution/auto"

processing:
  super_resolution:
    model_name: "fsrcnn"
    scale: 4
    model_path: "models/super_resolution/FSRCNN_x4.pb"
```

---

## 📁 Cấu trúc thư mục

```
project_root/
├── main.py                          # Step 1 entry point
├── run_pipeline.py                  # Pipeline script (Step 1 → Step 2)
├── run_step2_only.py                # Step 2 standalone script
├── PIPELINE_README.md               # Tài liệu này
│
├── src/                             # Step 1 source code
│   ├── video_processor.py
│   ├── model_inference.py
│   ├── polygon_roi_manager.py
│   └── ...
│
├── config/                          # Step 1 configs
│   ├── config_polygon_example.yaml
│   └── config_polygon_saved.yaml
│
├── data/
│   ├── input/                       # Video đầu vào
│   │   └── road1_can_cao.mp4
│   └── output/                      # Step 1 output
│       ├── cropped_plates_polygon/  # Ảnh biển số đã cắt
│       └── annotated_video.mp4      # Video có annotations
│
└── step02_use_edge_detection/       # Step 2 project
    ├── main.py                      # Step 2 entry point
    ├── config.yaml                  # Step 2 config
    ├── modules/
    │   ├── auto_cut_image.py
    │   ├── super_resolution.py
    │   └── utils.py
    ├── models/
    │   └── super_resolution/
    │       └── FSRCNN_x4.pb
    └── data/
        ├── plates_after_cut/        # Ảnh sau auto-cut
        └── plates_after_cut_super_resolution/  # Ảnh sau SR
```

---

## 🎯 Workflow Examples

### **Example 1: Xử lý video mới hoàn toàn**

```bash
# Bước 1: Chạy full pipeline với interactive ROI
python run_pipeline.py data/input/new_video.mp4 --interactive-roi --run-name video_20241030

# Kết quả:
# ✓ data/output/cropped_plates_video_20241030/  (298 ảnh)
# ✓ step02.../plates_after_cut/video_20241030/  (245 ảnh)
# ✓ step02.../plates_after_cut_super_resolution/video_20241030/  (245 ảnh)
```

### **Example 2: Chạy lại Step 2 với params khác**

```bash
# Đã có output Step 1, muốn thử model SR khác
cd step02_use_edge_detection
python main.py --input ../data/output/cropped_plates_polygon \
               --output-sr data/output/sr_edsr \
               --skip-auto-cut
```

### **Example 3: Batch processing nhiều video**

```bash
# Tạo script batch
for video in data/input/*.mp4; do
    echo "Processing $video"
    python run_pipeline.py "$video" --run-name "$(basename $video .mp4)"
done
```

---

## 📊 Output Summary

| Step | Output | Mô tả |
|------|--------|-------|
| **Step 1** | `data/output/cropped_plates_{name}/` | Ảnh biển số đã cắt từ video |
| **Step 1** | `data/output/annotated_video_{name}.mp4` | Video có annotations |
| **Step 2** | `step02.../plates_after_cut/{name}/` | Ảnh sau auto-cut (perspective corrected) |
| **Step 2** | `step02.../plates_after_cut_super_resolution/{name}/` | Ảnh sau super resolution 4x |

---

## 🔧 Command Line Options

### **run_pipeline.py**

```
Options:
  input_video              Video đầu vào (required unless --skip-step1)
  --skip-step1             Bỏ qua Step 1
  --skip-step2             Bỏ qua Step 2
  --step1-config PATH      Config cho Step 1
  --step1-output PATH      Output folder của Step 1
  --step2-config PATH      Config cho Step 2
  --interactive-roi        Chọn ROI bằng chuột
  --roi-frame N            Frame để chọn ROI (default: 0)
  --skip-auto-cut          Bỏ qua auto-cut trong Step 2
  --skip-super-resolution  Bỏ qua super resolution
  --run-name NAME          Tên cho run (dùng để đặt tên folders)
```

### **run_step2_only.py**

```
Options:
  input_folder             Folder chứa ảnh cần xử lý
  --output-name NAME       Tên cho output folders
  --skip-auto-cut          Bỏ qua auto-cut
  --skip-super-resolution  Bỏ qua super resolution
  --config PATH            Config file
```

---

## 🐛 Troubleshooting

### **Lỗi: "Model not found"**

```bash
# Kiểm tra model có trong thư mục không
ls models/best.pt
ls step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb

# Cập nhật path trong config nếu cần
```

### **Lỗi: "Input folder không tồn tại"**

```bash
# Kiểm tra output của Step 1
ls data/output/cropped_plates_polygon/

# Chạy lại Step 1 nếu cần
python main.py data/input/road1_can_cao.mp4 --interactive-roi
```

### **Không detect được biển số**

- Thử giảm `confidence_threshold` trong config Step 1
- Kiểm tra polygon ROI có bao phủ đúng vùng không
- Xem video output để verify

### **Auto-cut không hoạt động**

- Ảnh biển số có thể quá mờ hoặc bị che khuất
- Thử điều chỉnh Canny parameters trong config
- Xem console output để check lỗi cụ thể

---

## 💡 Tips & Best Practices

### **Tối ưu Performance**

```yaml
# Step 1: Xử lý ít frame hơn
frame_sampling:
  skip_frames: 10  # Tăng lên để xử lý nhanh hơn

# Step 1: Tăng confidence threshold
model:
  confidence_threshold: 0.7  # Giảm false positives
```

### **Tối ưu Accuracy**

```yaml
# Step 1: Xử lý nhiều frame hơn
frame_sampling:
  skip_frames: 2

# Step 1: Giảm confidence threshold
model:
  confidence_threshold: 0.5  # Catch nhiều plates hơn
```

### **Quản lý Output**

```bash
# Đặt tên run có ý nghĩa
python run_pipeline.py data/input/video.mp4 --run-name "location_date_time"

# Ví dụ: hanoi_road1_20241030_morning
```

---

## 🔄 Backward Compatibility

Code cũ vẫn hoạt động:

```python
# Step 2 - Old style (vẫn work)
from modules.auto_cut_image import process_all_images
from modules.super_resolution import superres_images_in_folder

process_all_images("73")
superres_images_in_folder("data/plates_after_cut/73", "data/output/73")
```

---

## 📝 Notes

- Pipeline tự động tạo output folders nếu chưa có
- Mỗi run có thể có tên riêng để tránh ghi đè
- Config có thể override bằng command line arguments
- Step 1 và Step 2 có output riêng biệt, không ảnh hưởng lẫn nhau

---

## 🎓 Hướng dẫn chi tiết

Xem thêm:
- [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn cài đặt
- [README.md](README.md) - Tài liệu Step 1
- `step02_use_edge_detection/` - Step 2 documentation

---

**Tạo bởi:** Pipeline automation script
**Phiên bản:** 1.0
**Ngày:** 2024

