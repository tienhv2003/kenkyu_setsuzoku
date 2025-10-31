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

# 四角形領域を自動検出して補正する関数
def detect_and_correct(img, save_path):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4:
            doc_cnt = approx
            break
    else:
        print("❌ 四角形が見つかりませんでした。")
        return False

    pts = doc_cnt.reshape(4, 2)
    sorted_pts = sort_vertices(pts)

    (tl, tr, bl, br) = sorted_pts
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxWidth = int(max(widthA, widthB))
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [0, maxHeight - 1],
        [maxWidth - 1, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(sorted_pts, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    cv2.imwrite(save_path, warped)
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


def process_images_from_folder(input_dir, output_dir, skip_failed=True, verbose=True):
    """
    Xử lý tất cả ảnh trong folder với Canny edge detection
    
    Args:
        input_dir (str): Thư mục chứa ảnh đầu vào
        output_dir (str): Thư mục lưu ảnh đầu ra
        skip_failed (bool): Bỏ qua ảnh không detect được contour
        verbose (bool): In chi tiết quá trình xử lý
        
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

    if verbose:
        print(f"\n{'='*60}")
        print(f"   AUTO-CUT IMAGE - CANNY EDGE DETECTION")
        print(f"{'='*60}")
        print(f"Input:  {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Total images: {total_inputs}")
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
        
        success = detect_and_correct(img, save_path)
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
