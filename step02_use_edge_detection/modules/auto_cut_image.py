import cv2
import numpy as np
import os

# 頂点を左上、右上、左下、右下の順にソートする関数
def sort_vertices(vertices):
    sum_coords = vertices.sum(axis=1)
    diff_coords = np.diff(vertices, axis=1)

    top_left = vertices[np.argmin(sum_coords)]
    bottom_right = vertices[np.argmax(sum_coords)]
    top_right = vertices[np.argmin(diff_coords)]
    bottom_left = vertices[np.argmax(diff_coords)]

    return np.array([top_left, top_right, bottom_left, bottom_right], dtype=np.float32)


def calculate_adaptive_canny_thresholds(gray, method='percentile', low_percentile=10, high_percentile=30, 
                                       threshold_ratio=2.67, min_threshold1=30, max_threshold1=150,
                                       min_threshold2=80, max_threshold2=300):
    """
    Tự động tính Canny edge detection thresholds dựa trên đặc tính của ảnh
    
    Args:
        gray: Ảnh grayscale
        method: Phương pháp tính threshold ('percentile', 'otsu', 'median')
        low_percentile: Percentile thấp cho threshold1 (default: 10)
        high_percentile: Percentile cao cho threshold2 (default: 30)
        threshold_ratio: Tỷ lệ giữa threshold2 và threshold1 (default: 2.67 ≈ 200/75)
        min_threshold1: Giá trị tối thiểu cho threshold1
        max_threshold1: Giá trị tối đa cho threshold1
        min_threshold2: Giá trị tối thiểu cho threshold2
        max_threshold2: Giá trị tối đa cho threshold2
    
    Returns:
        tuple: (threshold1, threshold2)
    """
    # Tính gradient magnitude bằng Sobel
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    
    if method == 'percentile':
        # Dùng percentile của gradient magnitude
        threshold1 = np.percentile(gradient_magnitude, low_percentile)
        threshold2 = np.percentile(gradient_magnitude, high_percentile)
        
    elif method == 'median':
        # Dùng median của gradient magnitude
        median_gradient = np.median(gradient_magnitude)
        threshold1 = median_gradient * 0.5
        threshold2 = median_gradient * threshold_ratio
        
    elif method == 'otsu':
        # Dùng Otsu's method trên gradient magnitude
        gradient_uint8 = np.clip(gradient_magnitude, 0, 255).astype(np.uint8)
        otsu_threshold, _ = cv2.threshold(gradient_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        threshold1 = otsu_threshold * 0.5
        threshold2 = otsu_threshold * threshold_ratio
        
    else:
        # Fallback: dùng percentile
        threshold1 = np.percentile(gradient_magnitude, low_percentile)
        threshold2 = np.percentile(gradient_magnitude, high_percentile)
    
    # Đảm bảo threshold2 = threshold1 * ratio
    if threshold2 < threshold1 * threshold_ratio:
        threshold2 = threshold1 * threshold_ratio
    
    # Giới hạn trong khoảng cho phép
    threshold1 = np.clip(threshold1, min_threshold1, max_threshold1)
    threshold2 = np.clip(threshold2, min_threshold2, max_threshold2)
    
    return int(threshold1), int(threshold2)

# 四角形領域を自動検出して補正する関数
def detect_and_correct(img, save_path, crop_margin=0.0, canny_config=None, contour_config=None, 
                        skip_canny=False, verbose=False):
    """
    Phát hiện và chỉnh sửa hình chữ nhật (biển số) trong ảnh
    Chỉ làm perspective correction (chỉnh góc nghiêng) mà không cắt viền thừa
    
    Args:
        img: Ảnh đầu vào (BGR)
        save_path: Đường dẫn lưu ảnh đã chỉnh sửa
        crop_margin: Margin để mở rộng vùng cắt (0.0-1.0 = tỷ lệ, >1 = pixel)
        canny_config: Dict chứa cấu hình Canny edge detection
        contour_config: Dict chứa cấu hình contour detection
        skip_canny: Bỏ qua Canny edge detection, chỉ copy ảnh
        verbose: In thông tin chi tiết
    
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    # Nếu bỏ qua Canny, chỉ copy ảnh
    if skip_canny:
        cv2.imwrite(save_path, img)
        if verbose:
            print(f"   ⏭️  Bỏ qua Canny detection, copy ảnh trực tiếp")
            print(f"✅ 補正画像を保存しました: {save_path}")
        return True
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Lấy blur kernel size từ config hoặc dùng mặc định
    blur_kernel_size = 5
    if canny_config:
        blur_kernel_size = canny_config.get('blur_kernel_size', 5)
    
    blurred = cv2.GaussianBlur(gray, (blur_kernel_size, blur_kernel_size), 0)
    
    # Tính Canny thresholds
    if canny_config and canny_config.get('adaptive_threshold', False):
        # Tự động điều chỉnh threshold theo từng ảnh
        method = canny_config.get('adaptive_method', 'percentile')
        low_percentile = canny_config.get('adaptive_low_percentile', 10)
        high_percentile = canny_config.get('adaptive_high_percentile', 30)
        threshold_ratio = canny_config.get('threshold_ratio', 2.67)
        min_th1 = canny_config.get('min_threshold1', 30)
        max_th1 = canny_config.get('max_threshold1', 150)
        min_th2 = canny_config.get('min_threshold2', 80)
        max_th2 = canny_config.get('max_threshold2', 300)
        
        threshold1, threshold2 = calculate_adaptive_canny_thresholds(
            blurred, 
            method=method,
            low_percentile=low_percentile,
            high_percentile=high_percentile,
            threshold_ratio=threshold_ratio,
            min_threshold1=min_th1,
            max_threshold1=max_th1,
            min_threshold2=min_th2,
            max_threshold2=max_th2
        )
        
        if verbose:
            print(f"   🔧 Adaptive thresholds: {threshold1}, {threshold2} (method: {method})")
    else:
        # Dùng threshold cố định từ config hoặc mặc định
        threshold1 = 75
        threshold2 = 200
        if canny_config:
            threshold1 = canny_config.get('threshold1', 75)
            threshold2 = canny_config.get('threshold2', 200)
        
        if verbose:
            print(f"   🔧 Fixed thresholds: {threshold1}, {threshold2}")
    
    edged = cv2.Canny(blurred, threshold1, threshold2)

    # Lấy contour config
    approx_epsilon = 0.02
    if contour_config:
        approx_epsilon = contour_config.get('approx_epsilon', 0.02)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, approx_epsilon * peri, True)

        if len(approx) == 4:
            doc_cnt = approx
            break
    else:
        if verbose:
            print("❌ 四角形が見つかりませんでした。")
        return False

    pts = doc_cnt.reshape(4, 2)
    sorted_pts = sort_vertices(pts)

    (tl, tr, bl, br) = sorted_pts
    
    # Tính kích thước cơ bản của biển số
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    baseWidth = max(widthA, widthB)
    baseHeight = max(heightA, heightB)
    
    # Áp dụng margin để mở rộng vùng cắt (bỏ phần cắt viền thừa)
    if crop_margin > 0:
        if crop_margin <= 1.0:
            # Margin là tỷ lệ (0.0-1.0)
            margin_w = baseWidth * crop_margin
            margin_h = baseHeight * crop_margin
        else:
            # Margin là pixel
            margin_w = crop_margin
            margin_h = crop_margin
        
        maxWidth = int(baseWidth + 2 * margin_w)
        maxHeight = int(baseHeight + 2 * margin_h)
        
        if verbose:
            print(f"   📐 Crop margin: {crop_margin} (size: {maxWidth}x{maxHeight})")
    else:
        # Không có margin, cắt sát như cũ
        maxWidth = int(baseWidth)
        maxHeight = int(baseHeight)

    # Destination points cho perspective transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [0, maxHeight - 1],
        [maxWidth - 1, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(sorted_pts, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    cv2.imwrite(save_path, warped)
    if verbose:
        print(f"✅ 補正画像を保存しました: {save_path}")
    return True

# フォルダ内の全画像を処理する関数
def process_all_images(output_folder):
    """
    DEPRECATED: Sử dụng process_images_from_folder() thay thế
    Hàm này giữ lại để backward compatibility với code cũ
    """
    input_dir = f"data/number/{output_folder}"
    output_dir = f"data/plates_after_cut/{output_folder}"
    
    return process_images_from_folder(input_dir, output_dir)


def process_images_from_folder(input_dir, output_dir, skip_failed=True, verbose=True, 
                                canny_config=None, contour_config=None, crop_margin=0.0, 
                                skip_canny=False):
    """
    Xử lý tất cả ảnh trong folder với Canny edge detection
    
    Args:
        input_dir (str): Thư mục chứa ảnh đầu vào
        output_dir (str): Thư mục lưu ảnh đầu ra
        skip_failed (bool): Bỏ qua ảnh không detect được contour
        verbose (bool): In chi tiết quá trình xử lý
        canny_config (dict): Cấu hình cho Canny edge detection
        contour_config (dict): Cấu hình cho contour detection
        crop_margin (float): Margin để mở rộng vùng cắt (0.0-1.0 = tỷ lệ, >1 = pixel)
        skip_canny (bool): Bỏ qua Canny edge detection, chỉ copy ảnh
        
    Returns:
        dict: Thống kê kết quả {total, success, failed}
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_dir):
        print(f"❌ Thư mục input không tồn tại: {input_dir}")
        return {"total": 0, "success": 0, "failed": 0}

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_inputs = len(files)
    cut_count = 0
    failed_count = 0

    # Lấy crop_margin và skip_canny từ config nếu không được truyền
    if crop_margin == 0.0 and canny_config:
        crop_margin = canny_config.get('crop_margin', 0.0)
    if not skip_canny and canny_config:
        skip_canny = canny_config.get('skip_canny_detection', False)
    
    if verbose:
        print(f"\n{'='*60}")
        if skip_canny:
            print(f"   AUTO-CUT IMAGE - COPY MODE (SKIP CANNY)")
        else:
            print(f"   AUTO-CUT IMAGE - CANNY EDGE DETECTION")
        print(f"{'='*60}")
        print(f"Input:  {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Total images: {total_inputs}")
        if skip_canny:
            print(f"⚠️  Canny detection: DISABLED (chỉ copy ảnh)")
        else:
            if crop_margin > 0:
                print(f"Crop margin: {crop_margin} ({'ratio' if crop_margin <= 1.0 else 'pixels'})")
            if canny_config:
                adaptive = canny_config.get('adaptive_threshold', False)
                if adaptive:
                    method = canny_config.get('adaptive_method', 'percentile')
                    print(f"Adaptive threshold: ENABLED (method: {method})")
                else:
                    th1 = canny_config.get('threshold1', 75)
                    th2 = canny_config.get('threshold2', 200)
                    print(f"Adaptive threshold: DISABLED (fixed: {th1}, {th2})")
        print(f"{'='*60}\n")

    for idx, filename in enumerate(files, start=1):
        input_path = os.path.join(input_dir, filename)
        save_path = os.path.join(output_dir, filename)

        img = cv2.imread(input_path)
        if img is None:
            if verbose:
                print(f"⚠️  [{idx}/{total_inputs}] Không đọc được: {filename}")
            failed_count += 1
            continue

        if verbose:
            print(f"📷 [{idx}/{total_inputs}] Đang xử lý: {filename}")
        
        success = detect_and_correct(img, save_path, crop_margin=crop_margin, 
                                     canny_config=canny_config, contour_config=contour_config, 
                                     skip_canny=skip_canny, verbose=verbose)
        if success:
            cut_count += 1
        else:
            failed_count += 1

    if verbose:
        print(f"\n{'='*60}")
        print(f"📊 KẾT QUẢ AUTO-CUT:")
        print(f"   ✅ Thành công: {cut_count}/{total_inputs}")
        print(f"   ❌ Thất bại:   {failed_count}/{total_inputs}")
        print(f"{'='*60}\n")
    
    return {
        "total": total_inputs,
        "success": cut_count,
        "failed": failed_count
    }

# メイン処理
if __name__ == "__main__":
    process_all_images('73')    
