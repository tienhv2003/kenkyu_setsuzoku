import cv2
import cv2.dnn_superres
import numpy as np
import os

# Tính BASE_DIR từ vị trí file hiện tại (dùng realpath để đảm bảo đường dẫn đúng)
# __file__ = step02_use_edge_detection/modules/super_resolution.py
# dirname(__file__) = step02_use_edge_detection/modules
# dirname(dirname(__file__)) = step02_use_edge_detection
_file_path = os.path.realpath(__file__)  # Dùng realpath thay vì abspath để resolve đúng
BASE_DIR = os.path.dirname(os.path.dirname(_file_path))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "super_resolution", "FSRCNN_x4.pb")

# Global model instance (để tránh load lại nhiều lần)
_global_model = None


def load_super_resolution_model(model_path=None, model_name="fsrcnn", scale=4):
    """
    Load super resolution model
    
    Args:
        model_path (str): Path to model file (default: FSRCNN_x4.pb)
        model_name (str): Model name (fsrcnn, espcn, edsr, lapsrn)
        scale (int): Scale factor (2, 3, 4, or 8 for lapsrn)
        
    Returns:
        cv2.dnn_superres.DnnSuperResImpl: Loaded model
    """
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    
    # Normalize đường dẫn và convert sang absolute path
    model_path = os.path.normpath(os.path.abspath(model_path))
    
    if not os.path.exists(model_path):
        # In thông tin debug để dễ tìm lỗi
        print(f"[ERROR] Model file not found: {model_path}")
        print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
        print(f"[DEBUG] DEFAULT_MODEL_PATH: {DEFAULT_MODEL_PATH}")
        print(f"[DEBUG] __file__: {__file__}")
        print(f"[DEBUG] realpath(__file__): {os.path.realpath(__file__)}")
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Kiểm tra file có thể đọc được không
    try:
        with open(model_path, 'rb') as f:
            f.read(1)  # Đọc 1 byte để test
    except Exception as e:
        raise FileNotFoundError(f"Cannot read model file: {model_path}. Error: {e}")
    
    # Trên Windows, OpenCV có thể có vấn đề với đường dẫn Unicode
    # Convert sang short path nếu cần (Windows only)
    if os.name == 'nt':  # Windows
        try:
            import win32api
            model_path = win32api.GetShortPathName(model_path)
        except ImportError:
            # Nếu không có pywin32, thử dùng đường dẫn gốc
            pass
        except Exception:
            # Nếu GetShortPathName fail, dùng đường dẫn gốc
            pass
    
    model = cv2.dnn_superres.DnnSuperResImpl_create()
    # Dùng đường dẫn đã normalize
    model.readModel(model_path)
    model.setModel(model_name.lower(), scale)
    
    return model


# Initialize default model for backward compatibility
model_FSRCNN = load_super_resolution_model()

#画像フォルダ内のすべての画像を処理する関数
def superres_images_in_folder(input_folder, output_folder, model=None, verbose=True):
    """
    Áp dụng super resolution cho tất cả ảnh trong folder
    
    Args:
        input_folder (str): Thư mục chứa ảnh đầu vào
        output_folder (str): Thư mục lưu ảnh đầu ra
        model: Super resolution model (nếu None sẽ dùng model_FSRCNN mặc định)
        verbose (bool): In chi tiết quá trình xử lý
        
    Returns:
        dict: Thống kê kết quả {total, success, failed}
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(input_folder):
        print(f"❌ Thư mục input không tồn tại: {input_folder}")
        return {"total": 0, "success": 0, "failed": 0}
    
    # Sử dụng model được truyền vào hoặc model mặc định
    if model is None:
        model = model_FSRCNN

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total = len(image_files)
    success_count = 0
    failed_count = 0
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"   SUPER RESOLUTION - 4x UPSCALING")
        print(f"{'='*60}")
        print(f"Input:  {input_folder}")
        print(f"Output: {output_folder}")
        print(f"Total images: {total}")
        print(f"{'='*60}\n")
    
    for idx, image_file in enumerate(image_files, start=1):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, image_file)
        
        img = cv2.imread(input_path)
        if img is None:
            if verbose:
                print(f"⚠️  [{idx}/{total}] Không đọc được: {image_file}")
            failed_count += 1
            continue
        
        try:
            if verbose:
                print(f"🔍 [{idx}/{total}] Đang xử lý: {image_file}")
            
            # Step 1: Super resolution
            upscaled_img = model.upsample(img)
            
            # Step 2: Convert to grayscale for better OCR
            gray_img = cv2.cvtColor(upscaled_img, cv2.COLOR_BGR2GRAY)
            
            # Step 3: Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_img = clahe.apply(gray_img)
            
            # Step 4: Add white border to stabilize OCR feature extraction
            padded = cv2.copyMakeBorder(enhanced_img, 30, 30, 30, 30, 
                                       cv2.BORDER_CONSTANT, value=255)
            
            cv2.imwrite(output_path, padded)
            
            if verbose:
                print(f"   ✅ Đã lưu: {output_path}")
            success_count += 1
            
        except Exception as e:
            if verbose:
                print(f"   ❌ Lỗi: {e}")
            failed_count += 1
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"📊 KẾT QUẢ SUPER RESOLUTION:")
        print(f"   ✅ Thành công: {success_count}/{total}")
        print(f"   ❌ Thất bại:   {failed_count}/{total}")
        print(f"{'='*60}\n")
    
    return {
        "total": total,
        "success": success_count,
        "failed": failed_count
    }




