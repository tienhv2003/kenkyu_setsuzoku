# Pipeline - Hệ thống xử lý biển số xe tự động (v2)

## 📖 Tổng quan

Pipeline kết nối Step 1 và Step 2 ở cấu trúc ngang hàng.

## 📁 Cấu trúc thư mục

```
connecting/                                    ← Working directory
├── step01_use_model_train20251007/           ← Step 1
│   ├── main.py
│   ├── src/
│   ├── models/best.pt
│   └── data/
│       ├── input/                             # Videos
│       └── output/                            # Cropped plates
│
├── step02_use_edge_detection/                ← Step 2 (ngang hàng)
│   ├── main.py
│   ├── modules/
│   ├── models/super_resolution/
│   └── data/
│       ├── plates_after_cut/
│       └── plates_after_cut_super_resolution/
│
├── run_pipeline.py                            ← Pipeline chính
├── run_step2_only.py                          ← Step 2 standalone
├── restructure_project.py                     ← Migration script
└── PIPELINE_README_v2.md                      ← File này
```

## 🚀 Quick Start

### **1. Tái cấu trúc (một lần)**

```bash
cd connecting/
python restructure_project.py
```

### **2. Chạy pipeline**

```bash
cd connecting/
python run_pipeline.py step01_use_model_train20251007/data/input/video.mp4 --interactive-roi
```

### **3. Chỉ Step 2**

```bash
cd connecting/
python run_step2_only.py step01_use_model_train20251007/data/output/cropped_plates_polygon
```

## 📊 Outputs

- **Step 1**: `step01_use_model_train20251007/data/output/cropped_plates_{name}/`
- **Step 2**: `step02_use_edge_detection/data/plates_after_cut_{name}/`
- **Step 2**: `step02_use_edge_detection/data/plates_after_cut_super_resolution/{name}/`

## 💡 Lưu ý

- Luôn chạy từ thư mục `connecting/`
- Đường dẫn relative từ `connecting/`
- Step 1 và Step 2 độc lập, có output riêng

Xem [QUICKSTART.md](QUICKSTART.md) để biết thêm chi tiết.

