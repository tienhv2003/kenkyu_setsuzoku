import cv2
import os
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict
import shutil


def extract_features(image_path, orb=None):
    """
    Trích xuất keypoints và descriptors từ ảnh
    
    Args:
        image_path (str): Đường dẫn đến ảnh
        orb: ORB detector (nếu None sẽ tạo mới)
    
    Returns:
        tuple: (keypoints, descriptors, num_keypoints)
    """
    if orb is None:
        orb = cv2.ORB_create()
    
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None, None, 0
    
    # Tiền xử lý giống feature_extractor.py
    image = cv2.equalizeHist(image)
    image = cv2.copyMakeBorder(image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)
    
    # Detect và compute descriptors
    keypoints, descriptors = orb.detectAndCompute(image, None)
    
    if descriptors is None:
        descriptors = np.array([])
    
    return keypoints, descriptors, len(keypoints)


def match_features(desc1, desc2, match_ratio=0.75, min_matches=10):
    """
    So sánh descriptors giữa 2 ảnh
    
    Args:
        desc1: Descriptors của ảnh 1
        desc2: Descriptors của ảnh 2
        match_ratio: Tỷ lệ match để xác định ảnh trùng lặp (0.0-1.0)
        min_matches: Số matches tối thiểu để coi là trùng lặp
    
    Returns:
        float: Tỷ lệ match (0.0-1.0), càng cao càng giống nhau
    """
    if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
        return 0.0
    
    # Sử dụng Brute Force Matcher với Hamming distance cho ORB
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    
    try:
        matches = bf.knnMatch(desc1, desc2, k=2)
        
        # Lowe's ratio test để lọc matches tốt
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < match_ratio * n.distance:
                    good_matches.append(m)
        
        # Yêu cầu số matches tối thiểu
        if len(good_matches) < min_matches:
            return 0.0
        
        # Tính tỷ lệ match dựa trên số good matches
        max_matches = min(len(desc1), len(desc2))
        if max_matches == 0:
            return 0.0
        
        # Dùng cả tỷ lệ và số lượng matches để tính similarity
        ratio_score = len(good_matches) / max_matches
        
        # Normalize dựa trên số matches (nhiều matches hơn = chắc chắn hơn)
        # Nhưng không quá strict
        match_count_score = min(len(good_matches) / 50.0, 1.0)  # 50 matches = full score
        
        # Kết hợp cả 2: 70% ratio, 30% match count
        final_score = 0.7 * ratio_score + 0.3 * match_count_score
        
        return final_score
        
    except Exception as e:
        print(f"   ⚠️  Lỗi khi match features: {e}")
        return 0.0


def find_duplicate_groups(folder_path, similarity_threshold=0.5, match_ratio=0.75, min_matches=15, verbose=True):
    """
    Tìm các nhóm ảnh trùng lặp dựa trên features
    
    Args:
        folder_path (str): Thư mục chứa ảnh
        similarity_threshold (float): Ngưỡng similarity để coi là trùng lặp (0.0-1.0)
        match_ratio (float): Tỷ lệ match cho Lowe's ratio test
        verbose (bool): In thông tin chi tiết
    
    Returns:
        list: Danh sách các nhóm ảnh trùng lặp, mỗi nhóm là list các filename
    """
    orb = cv2.ORB_create()
    
    # Lấy danh sách ảnh
    image_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            image_files.append(filename)
    
    if len(image_files) < 2:
        if verbose:
            print("   ℹ️  Không đủ ảnh để so sánh (cần ít nhất 2 ảnh)")
        return []
    
    if verbose:
        print(f"\n   🔍 Đang trích xuất features từ {len(image_files)} ảnh...")
    
    # Trích xuất features cho tất cả ảnh
    image_features = {}
    for idx, filename in enumerate(image_files, 1):
        image_path = os.path.join(folder_path, filename)
        keypoints, descriptors, num_keypoints = extract_features(image_path, orb)
        
        if descriptors is not None and len(descriptors) > 0:
            image_features[filename] = {
                'keypoints': keypoints,
                'descriptors': descriptors,
                'num_keypoints': num_keypoints,
                'path': image_path
            }
            if verbose and idx % 10 == 0:
                print(f"      [{idx}/{len(image_files)}] {filename}: {num_keypoints} keypoints")
        else:
            if verbose:
                print(f"      ⚠️  [{idx}/{len(image_files)}] {filename}: Không tìm thấy features")
    
    if len(image_features) < 2:
        if verbose:
            print("   ⚠️  Không đủ ảnh có features để so sánh")
        return []
    
    if verbose:
        print(f"\n   🔗 Đang so sánh {len(image_features)} ảnh để tìm trùng lặp...")
    
    # So sánh từng cặp ảnh
    similarity_matrix = {}
    total_comparisons = len(image_features) * (len(image_features) - 1) // 2
    comparison_count = 0
    
    filenames = list(image_features.keys())
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            filename1 = filenames[i]
            filename2 = filenames[j]
            
            desc1 = image_features[filename1]['descriptors']
            desc2 = image_features[filename2]['descriptors']
            
            similarity = match_features(desc1, desc2, match_ratio, min_matches)
            similarity_matrix[(filename1, filename2)] = similarity
            
            comparison_count += 1
            if verbose and comparison_count % 10 == 0:
                print(f"      [{comparison_count}/{total_comparisons}] So sánh: {filename1} vs {filename2} = {similarity:.3f}")
    
    # Nhóm các ảnh trùng lặp (chỉ nhóm nếu similarity cao)
    groups = []
    processed = set()
    
    # Sắp xếp theo similarity từ cao xuống thấp để ưu tiên matches chắc chắn
    sorted_pairs = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)
    
    for (filename1, filename2), similarity in sorted_pairs:
        if filename1 in processed or filename2 in processed:
            continue
        
        if similarity >= similarity_threshold:
            # Tìm tất cả ảnh liên quan (chỉ thêm nếu similarity đủ cao)
            group = {filename1, filename2}
            processed.add(filename1)
            processed.add(filename2)
            
            # Tìm thêm ảnh trùng với nhóm này (chỉ thêm nếu similarity cao với ít nhất 1 ảnh trong nhóm)
            found_new = True
            max_iterations = 10  # Giới hạn số lần lặp để tránh nhóm quá lớn
            iteration = 0
            
            while found_new and iteration < max_iterations:
                iteration += 1
                found_new = False
                for f1, f2 in similarity_matrix:
                    if f1 in processed or f2 in processed:
                        continue
                    
                    similarity_val = similarity_matrix[(f1, f2)]
                    # Chỉ thêm nếu similarity cao với ít nhất 1 ảnh trong nhóm
                    if similarity_val >= similarity_threshold:
                        # Kiểm tra xem có ảnh nào trong nhóm match với f1 hoặc f2 không
                        should_add = False
                        for group_member in group:
                            pair1 = (group_member, f1) if group_member < f1 else (f1, group_member)
                            pair2 = (group_member, f2) if group_member < f2 else (f2, group_member)
                            
                            if pair1 in similarity_matrix and similarity_matrix[pair1] >= similarity_threshold:
                                should_add = True
                                break
                            if pair2 in similarity_matrix and similarity_matrix[pair2] >= similarity_threshold:
                                should_add = True
                                break
                        
                        if should_add:
                            group.add(f1)
                            group.add(f2)
                            processed.add(f1)
                            processed.add(f2)
                            found_new = True
            
            groups.append(list(group))
    
    if verbose:
        print(f"\n   📊 Tìm thấy {len(groups)} nhóm ảnh trùng lặp")
        for idx, group in enumerate(groups, 1):
            print(f"      Nhóm {idx}: {len(group)} ảnh - {', '.join(group[:3])}{'...' if len(group) > 3 else ''}")
    
    return groups


def select_best_image_in_group(group, folder_path, image_features=None, verbose=True):
    """
    Chọn ảnh đẹp nhất (có nhiều keypoints nhất) trong nhóm
    
    Args:
        group (list): Danh sách filename trong nhóm
        folder_path (str): Thư mục chứa ảnh
        image_features (dict): Dict chứa features đã extract (nếu có)
        verbose (bool): In thông tin chi tiết
    
    Returns:
        str: Filename của ảnh tốt nhất
    """
    if not group:
        return None
    
    if len(group) == 1:
        return group[0]
    
    # Nếu chưa có features, extract lại
    if image_features is None:
        orb = cv2.ORB_create()
        image_features = {}
        for filename in group:
            image_path = os.path.join(folder_path, filename)
            keypoints, descriptors, num_keypoints = extract_features(image_path, orb)
            if descriptors is not None:
                image_features[filename] = num_keypoints
    
    # Tìm ảnh có nhiều keypoints nhất
    best_image = None
    max_keypoints = -1
    
    for filename in group:
        if filename in image_features:
            num_keypoints = image_features[filename].get('num_keypoints', 0) if isinstance(image_features[filename], dict) else image_features[filename]
            if num_keypoints > max_keypoints:
                max_keypoints = num_keypoints
                best_image = filename
    
    # Nếu không tìm được qua features, dùng ảnh đầu tiên
    if best_image is None:
        best_image = group[0]
        max_keypoints = 0
    
    if verbose:
        print(f"      ✅ Chọn: {best_image} ({max_keypoints} keypoints)")
    
    return best_image


def remove_duplicates(folder_path, output_csv=None, similarity_threshold=0.5, 
                     match_ratio=0.75, min_matches=15, backup_duplicates=True, verbose=True):
    """
    Xóa các ảnh trùng lặp, giữ lại ảnh đẹp nhất trong mỗi nhóm
    
    Args:
        folder_path (str): Thư mục chứa ảnh
        output_csv (str, optional): File CSV để lưu kết quả
        similarity_threshold (float): Ngưỡng similarity để coi là trùng lặp
        match_ratio (float): Tỷ lệ match cho Lowe's ratio test
        backup_duplicates (bool): Có backup ảnh bị xóa vào thư mục riêng không
        verbose (bool): In thông tin chi tiết
    
    Returns:
        dict: Thống kê {total, kept, removed, groups}
    """
    folder_path = Path(folder_path)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"   REMOVE DUPLICATE IMAGES - FEATURE MATCHING")
        print(f"{'='*70}")
        print(f"Input folder: {folder_path}")
        print(f"Similarity threshold: {similarity_threshold}")
        print(f"Match ratio: {match_ratio}")
        print(f"{'='*70}\n")
    
    # Tìm các nhóm ảnh trùng lặp
    groups = find_duplicate_groups(str(folder_path), similarity_threshold, match_ratio, min_matches, verbose)
    
    # Đếm tổng số ảnh
    image_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
    total_images = len(image_files)
    
    # Trích xuất features để chọn ảnh tốt nhất
    if verbose:
        print(f"\n   🎯 Đang chọn ảnh tốt nhất trong mỗi nhóm...")
    
    orb = cv2.ORB_create()
    image_features = {}
    for filename in image_files:
        image_path = folder_path / filename
        keypoints, descriptors, num_keypoints = extract_features(str(image_path), orb)
        if descriptors is not None:
            image_features[filename] = {
                'num_keypoints': num_keypoints,
                'descriptors': descriptors
            }
    
    # Chọn ảnh tốt nhất và xóa các ảnh còn lại
    images_to_keep = set(image_files)  # Ban đầu giữ tất cả
    images_to_remove = []
    kept_images = []
    removed_images = []
    all_group_images = set()
    
    for group in groups:
        all_group_images.update(group)
        best_image = select_best_image_in_group(group, str(folder_path), image_features, verbose)
        
        if best_image:
            kept_images.append(best_image)
            # Xóa các ảnh khác trong nhóm
            for filename in group:
                if filename != best_image:
                    images_to_remove.append(filename)
                    removed_images.append(filename)
                    if filename in images_to_keep:
                        images_to_keep.remove(filename)
    
    # Ảnh không trong nhóm nào (không trùng lặp) cũng được giữ lại
    for filename in image_files:
        if filename not in all_group_images:
            kept_images.append(filename)
    
    # Backup và xóa ảnh
    if images_to_remove:
        if backup_duplicates:
            backup_dir = folder_path / "duplicates_backup"
            backup_dir.mkdir(exist_ok=True)
            
            if verbose:
                print(f"\n   💾 Đang backup {len(images_to_remove)} ảnh trùng lặp...")
            
            for filename in images_to_remove:
                src = folder_path / filename
                dst = backup_dir / filename
                shutil.move(str(src), str(dst))
                if verbose:
                    print(f"      📦 Moved: {filename} -> duplicates_backup/")
        else:
            if verbose:
                print(f"\n   🗑️  Đang xóa {len(images_to_remove)} ảnh trùng lặp...")
            
            for filename in images_to_remove:
                img_path = folder_path / filename
                img_path.unlink()
                if verbose:
                    print(f"      ❌ Deleted: {filename}")
    
    # Lưu kết quả vào CSV
    if output_csv:
        output_csv = Path(output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["filename", "status", "num_keypoints", "group"])
            
            # Ghi ảnh được giữ lại
            for idx, group in enumerate(groups, 1):
                best_image = select_best_image_in_group(group, str(folder_path), image_features, verbose=False)
                num_kp = image_features.get(best_image, {}).get('num_keypoints', 0) if best_image else 0
                writer.writerow([best_image, "kept", num_kp, f"group_{idx}"])
                
                for filename in group:
                    if filename != best_image:
                        num_kp = image_features.get(filename, {}).get('num_keypoints', 0) if filename in image_features else 0
                        writer.writerow([filename, "removed", num_kp, f"group_{idx}"])
            
            # Ghi ảnh không trùng lặp
            for filename in image_files:
                if filename not in [img for group in groups for img in group]:
                    num_kp = image_features.get(filename, {}).get('num_keypoints', 0) if filename in image_features else 0
                    writer.writerow([filename, "kept", num_kp, "unique"])
        
        if verbose:
            print(f"\n   📄 Kết quả đã lưu vào: {output_csv}")
    
    # Thống kê
    stats = {
        'total': total_images,
        'kept': len(kept_images),
        'removed': len(removed_images),
        'groups': len(groups),
        'unique': total_images - sum(len(g) for g in groups)
    }
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"   📊 KẾT QUẢ:")
        print(f"   Tổng số ảnh:     {stats['total']}")
        print(f"   Ảnh được giữ:    {stats['kept']} ({stats['unique']} unique, {len(groups)} từ {len(groups)} nhóm)")
        print(f"   Ảnh đã xóa:       {stats['removed']}")
        print(f"   Số nhóm trùng:    {stats['groups']}")
        print(f"{'='*70}\n")
    
    return stats


def main():
    """Test function"""
    folder_path = 'input'
    output_csv = 'output/duplicate_removal_result.csv'
    
    remove_duplicates(
        folder_path=folder_path,
        output_csv=output_csv,
        similarity_threshold=0.3,
        match_ratio=0.75,
        backup_duplicates=True,
        verbose=True
    )


if __name__ == "__main__":
    main()

