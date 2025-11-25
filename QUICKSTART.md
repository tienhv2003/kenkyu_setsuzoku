# 🚀 Quick Start Guide - Pipeline (Cấu trúc ngang hàng)

## Cấu trúc mới

```
connecting/
├── step01_use_model_train20251007/  ← Step 1: Detection
├── step02_use_edge_detection/       ← Step 2: Enhancement
├── step03_feature_extractor_matcher/ ← Step 3: Feature Extraction
├── run_pipeline.py                  ← Pipeline
└── QUICKSTART.md                    ← File này
```

---

## Bước 1: Tái cấu trúc (nếu chưa làm)

```bash
cd connecting/
python restructure_project.py
```

**Kết quả:**
- Di chuyển `step02_use_edge_detection` ra ngoài
- Di chuyển pipeline scripts ra thư mục chung

---

## Bước 2: Chạy Pipeline

```bash
cd connecting/

# Chạy với interactive ROI
python run_pipeline.py step01_use_model_train20251007/data/input/road1_can_cao.mp4 --interactive-roi
```

**Interactive ROI:**
1. Cửa sổ video hiện ra
2. Click 4 lần để chọn polygon ROI
3. Nhấn **ENTER** để xác nhận
4. Pipeline tự động chạy

---

## Bước 3: Xem kết quả

```bash
# Step 1 output
ls step01_use_model_train20251007/data/output/cropped_plates_*/

# Step 2 output
ls step02_use_edge_detection/data/plates_after_cut_super_resolution/*/
```

---

## Các lệnh thường dùng

### **Full pipeline**
```bash
cd connecting/
python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4
```

### **Chỉ Step 2**
```bash
cd connecting/
python run_step2_only.py step01_use_model_train20251007/data/output/cropped_plates_polygon
```

### **Batch processing**
```bash
cd connecting/
for video in step01_use_model_train20251007/data/input/*.mp4; do
    python run_pipeline.py "$video" --run-name "$(basename $video .mp4)"
done
```

---

## Troubleshooting

**Lỗi: "Step 2 directory not found"**
```bash
python restructure_project.py
```

**Lỗi: "Model not found"**
```bash
ls step01_use_model_train20251007/models/best.pt
ls step02_use_edge_detection/models/super_resolution/FSRCNN_x4.pb
```

**Đường dẫn sai**
- Luôn chạy từ `connecting/`
- Dùng đường dẫn relative: `step01_use_model_train20251007/data/input/video.mp4`

---

## So sánh với cấu trúc cũ

**Trước:**
```bash
cd step01_use_model_train20251007/
python run_pipeline.py data/input/video.mp4
```

**Sau:**
```bash
cd connecting/
python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4
```

---

📖 Xem [PIPELINE_README.md](PIPELINE_README.md) để biết chi tiết đầy đủ

