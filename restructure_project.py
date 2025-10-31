#!/usr/bin/env python3
"""
Script tự động tái cấu trúc project
Di chuyển step02_use_edge_detection ra ngoài để ngang hàng với step01
"""

import os
import shutil
from pathlib import Path


def main():
    print("=" * 70)
    print("   TÁI CẤU TRÚC PROJECT - Step 1 và Step 2 ngang hàng")
    print("=" * 70)
    
    # Xác định thư mục hiện tại
    script_dir = Path(__file__).parent.resolve()
    connecting_dir = script_dir
    
    step01_dir = connecting_dir / "step01_use_model_train20251007"
    step02_inside = step01_dir / "step02_use_edge_detection"
    step02_outside = connecting_dir / "step02_use_edge_detection"
    
    print(f"\n📁 Thư mục connecting: {connecting_dir}")
    print(f"📁 Step 01: {step01_dir}")
    print(f"📁 Step 02 (cũ): {step02_inside}")
    print(f"📁 Step 02 (mới): {step02_outside}")
    
    # Kiểm tra step02 có tồn tại trong step01 không
    if not step02_inside.exists():
        print(f"\n❌ Không tìm thấy: {step02_inside}")
        print("Có thể đã được di chuyển rồi.")
        return
    
    # Kiểm tra step02 ở ngoài đã tồn tại chưa
    if step02_outside.exists():
        print(f"\n⚠️  Cảnh báo: {step02_outside} đã tồn tại!")
        response = input("Ghi đè? (y/N): ")
        if response.lower() != 'y':
            print("Hủy bỏ.")
            return
        print(f"Xóa thư mục cũ: {step02_outside}")
        shutil.rmtree(step02_outside)
    
    # Di chuyển step02
    print(f"\n🚀 Đang di chuyển step02_use_edge_detection...")
    shutil.move(str(step02_inside), str(step02_outside))
    print(f"✅ Đã di chuyển thành công!")
    
    # Di chuyển các file pipeline ra ngoài
    print(f"\n🚀 Đang di chuyển pipeline scripts...")
    
    files_to_move = [
        "run_pipeline.py",
        "run_step2_only.py",
        "PIPELINE_README.md",
        "QUICKSTART.md"
    ]
    
    for filename in files_to_move:
        src = step01_dir / filename
        dst = connecting_dir / filename
        
        if src.exists():
            if dst.exists():
                print(f"⚠️  {filename} đã tồn tại ở ngoài, bỏ qua...")
            else:
                shutil.move(str(src), str(dst))
                print(f"✅ Đã di chuyển: {filename}")
        else:
            print(f"⚠️  Không tìm thấy: {filename}")
    
    print(f"\n{'=' * 70}")
    print("✅ TÁI CẤU TRÚC HOÀN TẤT!")
    print("=" * 70)
    print("\n📊 Cấu trúc mới:")
    print("""
connecting/
├── step01_use_model_train20251007/
│   ├── main.py
│   ├── src/
│   ├── models/
│   └── data/
├── step02_use_edge_detection/
│   ├── main.py
│   ├── modules/
│   ├── models/
│   └── data/
├── run_pipeline.py
├── run_step2_only.py
├── PIPELINE_README.md
└── QUICKSTART.md
    """)
    
    print("\n⚠️  LƯU Ý: Cần cập nhật đường dẫn trong các file config!")
    print("Chạy script cập nhật: python update_paths.py")


if __name__ == "__main__":
    main()

