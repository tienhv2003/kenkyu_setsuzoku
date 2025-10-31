# 📦 Hướng dẫn chuyển đổi sang cấu trúc mới

## Tổng quan

Tài liệu này hướng dẫn chuyển đổi từ cấu trúc cũ (step02 nested) sang cấu trúc mới (step01 và step02 ngang hàng).

---

## Cấu trúc cũ vs mới

### **Cấu trúc cũ (Nested)**

```
step01_use_model_train20251007/
├── main.py
├── src/
├── data/
├── run_pipeline.py          ← Trong step01
├── run_step2_only.py        ← Trong step01
└── step02_use_edge_detection/   ← Nested
    ├── main.py
    ├── modules/
    └── data/
```

### **Cấu trúc mới (Parallel)**

```
connecting/
├── step01_use_model_train20251007/  ← Step 1
│   ├── main.py
│   ├── src/
│   └── data/
├── step02_use_edge_detection/       ← Step 2 (ngang hàng)
│   ├── main.py
│   ├── modules/
│   └── data/
├── run_pipeline.py                  ← Ở thư mục chung
├── run_step2_only.py                ← Ở thư mục chung
└── restructure_project.py           ← Script di chuyển
```

---

## Các bước thực hiện

### **Bước 1: Backup dữ liệu**

```bash
# Backup toàn bộ project
cd connecting/
cp -r step01_use_model_train20251007 step01_use_model_train20251007_backup

# Hoặc chỉ backup data
cd step01_use_model_train20251007/step02_use_edge_detection/
cp -r data data_backup
```

### **Bước 2: Chạy script tái cấu trúc**

```bash
cd connecting/
python restructure_project.py
```

**Script sẽ:**
1. Di chuyển `step02_use_edge_detection` từ trong `step01/` ra ngoài `connecting/`
2. Di chuyển các pipeline scripts ra `connecting/`
3. Giữ nguyên tất cả data

### **Bước 3: Verify cấu trúc mới**

```bash
cd connecting/

# Kiểm tra thư mục
ls -la
# Phải thấy:
#   step01_use_model_train20251007/
#   step02_use_edge_detection/
#   run_pipeline.py
#   run_step2_only.py

# Kiểm tra data vẫn còn
ls step01_use_model_train20251007/data/output/
ls step02_use_edge_detection/data/
```

### **Bước 4: Test pipeline**

```bash
# Test với video có sẵn
python run_pipeline.py step01_use_model_train20251007/data/input/road1_can_cao.mp4 --skip-step2

# Nếu OK, test full pipeline
python run_pipeline.py step01_use_model_train20251007/data/input/road1_can_cao.mp4
```

---

## Cập nhật scripts/configs

### **Scripts cần cập nhật**

Nếu bạn có custom scripts:

**Trước:**
```python
# Old: từ trong step01/
import sys
sys.path.append('step02_use_edge_detection/modules')

video_path = 'data/input/video.mp4'
```

**Sau:**
```python
# New: từ connecting/
import sys
sys.path.append('step02_use_edge_detection/modules')

video_path = 'step01_use_model_train20251007/data/input/video.mp4'
```

### **Configs cần cập nhật**

**step02_use_edge_detection/config.yaml:**

```yaml
paths:
  # OLD (relative to step01/)
  input_dir: "../data/output/cropped_plates_polygon"
  
  # NEW (relative to step02/, pointing to step01/)
  input_dir: "../step01_use_model_train20251007/data/output/cropped_plates_polygon"
```

---

## Working Directory Changes

### **Chạy pipeline**

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

### **Chạy Step 1**

**Trước và Sau - KHÔNG ĐỔI:**
```bash
cd step01_use_model_train20251007/
python main.py data/input/video.mp4
```

### **Chạy Step 2 standalone**

**Trước:**
```bash
cd step01_use_model_train20251007/
python run_step2_only.py data/output/cropped_plates_polygon
```

**Sau:**
```bash
cd connecting/
python run_step2_only.py step01_use_model_train20251007/data/output/cropped_plates_polygon
```

---

## Rollback (nếu cần)

Nếu có vấn đề, rollback về cấu trúc cũ:

```bash
cd connecting/

# Xóa bản backup nếu có
rm -rf step01_use_model_train20251007/step02_use_edge_detection

# Di chuyển step02 về trong step01
mv step02_use_edge_detection step01_use_model_train20251007/

# Di chuyển pipeline scripts về step01
mv run_pipeline.py step01_use_model_train20251007/
mv run_step2_only.py step01_use_model_train20251007/
mv PIPELINE_README.md step01_use_model_train20251007/
mv QUICKSTART.md step01_use_model_train20251007/

# Hoặc restore từ backup
rm -rf step01_use_model_train20251007
mv step01_use_model_train20251007_backup step01_use_model_train20251007
```

---

## Lợi ích của cấu trúc mới

✅ **Rõ ràng hơn**: Step 1 và Step 2 độc lập, dễ hiểu

✅ **Dễ maintain**: Mỗi step có thư mục riêng, không lồng nhau

✅ **Linh hoạt**: Có thể dev Step 1 và Step 2 độc lập

✅ **Version control**: Dễ dàng git submodules nếu cần

✅ **Scalable**: Dễ thêm Step 3, Step 4 trong tương lai

---

## FAQs

### **Q: Data có bị mất không?**

A: Không, script chỉ di chuyển thư mục, không xóa data.

### **Q: Configs có cần cập nhật không?**

A: Chỉ cần cập nhật nếu có hardcode paths. Pipeline scripts mới đã handle paths tự động.

### **Q: Scripts cũ còn chạy được không?**

A: Scripts trong step01/ và step02/ vẫn chạy được bình thường.

### **Q: Git có ảnh hưởng không?**

A: Git history vẫn giữ nguyên. Nên commit trước khi migrate.

### **Q: Có thể dùng cả 2 cấu trúc không?**

A: Không nên. Chọn 1 cấu trúc và stick với nó.

---

## Checklist

Sau khi migrate, kiểm tra:

- [ ] `connecting/step01_use_model_train20251007/` exists
- [ ] `connecting/step02_use_edge_detection/` exists  
- [ ] `connecting/run_pipeline.py` exists
- [ ] `connecting/run_step2_only.py` exists
- [ ] Data trong `step01/data/output/` vẫn còn
- [ ] Data trong `step02/data/` vẫn còn
- [ ] Models còn nguyên:
  - [ ] `step01/models/best.pt`
  - [ ] `step02/models/super_resolution/FSRCNN_x4.pb`
- [ ] Test pipeline chạy OK
- [ ] Xóa backup sau khi verify

---

## Support

Nếu gặp vấn đề:

1. Kiểm tra [PIPELINE_README_v2.md](PIPELINE_README_v2.md)
2. Kiểm tra [QUICKSTART.md](QUICKSTART.md)
3. Rollback về cấu trúc cũ
4. Chạy lại script với verbose: `python restructure_project.py`

---

**Chúc may mắn với cấu trúc mới!** 🎉

