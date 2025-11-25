# Traffic License Plate Processing Pipeline

Hệ thống xử lý biển số xe tự động 2 bước với YOLO Detection + Super Resolution Enhancement.

## 📁 Project Structure

```
connecting/
├── step01_use_model_train20251007/      # Step 1: Detection
├── step02_use_edge_detection/           # Step 2: Enhancement  
├── run_pipeline.py                      # Main pipeline
├── run_step2_only.py                    # Step 2 standalone
├── restructure_project.py               # Migration tool
├── README.md                            # This file
├── PIPELINE_README.md                   # Tài liệu đầy đủ
├── QUICKSTART.md                        # Hướng dẫn nhanh
└── MIGRATION_GUIDE.md                   # Migration guide
```

## 🚀 Quick Start

```bash
# 1. Di chuyển vào thư mục
cd connecting/

# 2. Chạy pipeline (nếu chưa có cấu trúc ngang hàng, chạy restructure_project.py trước)
python run_pipeline.py step01_use_model_train20251007/data/input/road1_can_cao.mp4 --interactive-roi

# 3. Kết quả
#    - Step 1: step01_use_model_train20251007/data/output/
#    - Step 2: step02_use_edge_detection/data/
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Hướng dẫn nhanh (5 phút)
- **[PIPELINE_README.md](PIPELINE_README.md)** - Tài liệu đầy đủ
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Hướng dẫn migration
- **[step01_use_model_train20251007/README.md](step01_use_model_train20251007/README.md)** - Step 1 docs
- **[step01_use_model_train20251007/INSTALLATION.md](step01_use_model_train20251007/INSTALLATION.md)** - Installation guide

## 🔄 Workflow

```
Video Input
    ↓
┌─────────────────────────┐
│  Step 1: Detection      │
│  - YOLO model           │
│  - Polygon ROI filter   │
│  - Save cropped plates  │
└─────────────────────────┘
    ↓
Cropped License Plates
    ↓
┌─────────────────────────┐
│  Step 2: Enhancement    │
│  - Auto-cut (Canny)     │
│  - Perspective correct  │
│  - Super Resolution 4x  │
└─────────────────────────┘
    ↓
High-Quality Plates
    ↓
┌─────────────────────────┐
│  Step 3: Feature Extract│
│  - Preprocessing         │
│  - ORB keypoints        │
│  - CSV output           │
└─────────────────────────┘
    ↓
Feature Data
```

## 💻 Usage Examples

### Full Pipeline
```bash
python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4
```

### Step 1 Only
```bash
cd step01_use_model_train20251007/
python main.py data/input/video.mp4 --interactive-roi
```

### Step 2 Only
```bash
python run_step2_only.py step01_use_model_train20251007/data/output/cropped_plates_polygon
```

### Batch Processing
```bash
for video in step01_use_model_train20251007/data/input/*.mp4; do
    python run_pipeline.py "$video"
done
```

## ⚙️ Requirements

```bash
# Python 3.8+
pip install -r requirements.txt
```

**Lưu ý:** Project này cần `opencv-contrib-python` (không phải `opencv-python`) để có module super resolution.

```bash
# Nếu đã cài opencv-python, gỡ bỏ trước:
pip uninstall opencv-python
pip install opencv-contrib-python>=4.8.0
```

📖 **Xem [HUONG_DAN_CAI_DAT.md](HUONG_DAN_CAI_DAT.md) để biết chi tiết cài đặt**

## 🎯 Features

### Step 1 - Detection
- ✅ YOLO-based license plate detection
- ✅ Interactive polygon ROI selection
- ✅ Frame sampling optimization
- ✅ Real-time video preview
- ✅ Automatic plate cropping

### Step 2 - Enhancement
- ✅ Canny edge detection
- ✅ Automatic perspective correction
- ✅ Super resolution (4x upscaling)
- ✅ FSRCNN model (fast & accurate)
- ✅ Batch processing

### Step 3 - Feature Extraction
- ✅ Image preprocessing (grayscale, histogram equalization)
- ✅ ORB keypoint detection
- ✅ CSV output with keypoint counts
- ✅ Preprocessed image saving

## 📊 Outputs

| Step | Location | Content |
|------|----------|---------|
| Step 1 | `step01.../data/output/cropped_plates_{name}/` | Cropped license plate images |
| Step 1 | `step01.../data/output/annotated_video_{name}.mp4` | Annotated video |
| Step 2 | `step02.../data/plates_after_cut/{name}/` | Perspective-corrected images |
| Step 2 | `step02.../data/plates_after_cut_super_resolution/{name}/` | Super-resolution images |
| Step 3 | `step03.../output/{name}/keypoints_count.csv` | Keypoint counts CSV |
| Step 3 | `step03.../output/{name}/preprocessed/` | Preprocessed images |

## 🆕 Migration from Old Structure

If you have the old nested structure:

```bash
python restructure_project.py
```

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

## 🐛 Troubleshooting

**"Step 2 directory not found"**
```bash
python restructure_project.py
```

**"Model not found"**
```bash
# Check models exist
ls step01_use_model_train20251007/models/best.pt
ls step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb
```

**Wrong paths**
- Always run from `connecting/` directory
- Use relative paths from `connecting/`

## 📝 License

Research and educational use.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV for image processing
- FSRCNN for super resolution

---

**Version:** 2.0 (Parallel Structure)  
**Updated:** 2024  
**Structure:** Step 1 và Step 2 ngang hàng

