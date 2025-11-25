import cv2
import os
import csv

def process_folder(folder_path, output_csv, scale_factor=1.0, preprocessed_dir=None):
    """
    Xử lý tất cả ảnh trong thư mục và ghi số lượng keypoints vào CSV.
    
    Args:
        folder_path (str): Thư mục chứa ảnh
        output_csv (str): File CSV đầu ra
        scale_factor (float): Hệ số phóng to ảnh (mặc định 1.0 = không phóng to)
        preprocessed_dir (str, optional): Thư mục lưu ảnh đã preprocess. 
                                         Nếu None, dùng 'output/preprocessed' (relative to current dir)
    """
    orb = cv2.ORB_create()

    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "num_keypoints"])
        
        # Thư mục lưu ảnh sau khi chuyển xám + tăng tương phản
        if preprocessed_dir is None:
            preprocessed_dir = os.path.join('output', 'preprocessed')
        os.makedirs(preprocessed_dir, exist_ok=True)
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                image_path = os.path.join(folder_path, filename)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    print(f"Cảnh báo: Không đọc được ảnh {filename}")
                    continue
                
                # Tiền xử lý ảnh
                if scale_factor != 1.0:
                    image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
                
                image = cv2.equalizeHist(image)  # tăng tương phản
                
                base_name, _ = os.path.splitext(filename)
                image = cv2.copyMakeBorder(image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)  # thêm viền
                
                # Lưu ảnh sau khi thêm viền
                save_path_with_border = os.path.join(preprocessed_dir, f"{base_name}_gray_eq_border.png")
                cv2.imwrite(save_path_with_border, image)
                
                keypoints = orb.detect(image, None)
                writer.writerow([filename, len(keypoints)])
    
    print(f"Hoàn tất! CSV lưu tại: {output_csv}")

def main():
    folder_path = 'input'
    output_csv = 'output/keypoints_count.csv'
    scale_factor = 1.0  # Thay đổi nếu muốn phóng to ảnh, ví dụ 2.0
    
    process_folder(folder_path, output_csv, scale_factor)

if __name__ == "__main__":
    main()
