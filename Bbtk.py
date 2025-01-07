import os
import cv2
import numpy as np
import shutil

def add_custom_noise(image, intensity):
    """
    Add custom noise to an image: turns random pixels into black.
    
    Args:
        image (np.ndarray): Input image (H, W, C).
        intensity (float): Noise intensity (0.0 to 1.0).
    
    Returns:
        np.ndarray: Noisy image.
    """
    noisy_image = image.copy()
    h, w, _ = image.shape

    # Tìm tất cả các pixel không trong suốt
    mask = noisy_image[:, :, 3] > 0
    valid_pixels = np.argwhere(mask)

    # Số pixel sẽ chuyển thành màu đen
    num_noisy_pixels = int(len(valid_pixels) * intensity)
    noisy_indices = np.random.choice(len(valid_pixels), num_noisy_pixels, replace=False)

    for idx in noisy_indices:
        y, x = valid_pixels[idx]
        noisy_image[y, x, :3] = 0  # Chuyển pixel thành màu đen

    return noisy_image

def reorganize_and_generate_noise(src_dir, dest_dir, num_levels=100):
    """
    Reorganize dataset and add custom noise to images in a new structure.
    
    Args:
        src_dir (str): Path to the original dataset.
        dest_dir (str): Path to the destination dataset.
        num_levels (int): Number of noise levels to generate.
    """
    for pokemon_id in os.listdir(src_dir):
        pokemon_path = os.path.join(src_dir, pokemon_id)
        if not os.path.isdir(pokemon_path):
            continue

        # Lấy tên Pokémon (bỏ ID)
        pokemon_name = pokemon_id.split("_", 1)[-1]

        for root, dirs, files in os.walk(pokemon_path):
            for file in files:
                if file.lower() == "sprite.png":
                    # Đường dẫn nguồn và xác định các thư mục đích
                    src_file = os.path.join(root, file)
                    relative_path = os.path.relpath(root, src_dir)
                    new_relative_path = relative_path.split("_", 1)[-1]  # Bỏ ID khỏi đường dẫn
                    dest_folder = os.path.join(dest_dir, new_relative_path)
                    
                    # Tạo thư mục đích
                    os.makedirs(dest_folder, exist_ok=True)

                    # Sao chép ảnh gốc
                    dest_file = os.path.join(dest_folder, "sprite.png")
                    shutil.copy(src_file, dest_file)

                    # Tạo và lưu ảnh nhiễu
                    image = cv2.imread(src_file, cv2.IMREAD_UNCHANGED)
                    for level in range(1, num_levels + 1):
                        intensity = level / num_levels
                        noisy_image = add_custom_noise(image, intensity)
                        noisy_file = os.path.join(dest_folder, f"noise{level}.png")
                        cv2.imwrite(noisy_file, noisy_image)
                        print(f"Saved noisy image: {noisy_file}")

    print(f"Dataset has been reorganized and processed with noise. Output path: {dest_dir}")

# Đường dẫn thư mục nguồn và đích
src_directory = r"pokemon"  # Đường dẫn dataset gốc
dest_directory = r"train"  # Đường dẫn thư mục đích

# Chạy hàm xử lý
reorganize_and_generate_noise(src_directory, dest_directory)
