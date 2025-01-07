import cv2
import json
import os

# Thư mục chứa video và file JSON
data_dir = "training_data"
output_dir = "labeled_frames"
os.makedirs(output_dir, exist_ok=True)

# Tạo danh sách cặp video và JSON
data_files = [
    (os.path.join(data_dir, f), os.path.join(data_dir, f.replace(".avi", ".json")))
    for f in os.listdir(data_dir) if f.endswith(".avi")
]

# Duyệt qua từng cặp video và JSON
for video_path, json_path in data_files:
    print(f"Xử lý: {video_path} và {json_path}")

    # Đảm bảo cả video và JSON đều tồn tại
    if not os.path.exists(json_path):
        print(f"Bỏ qua {video_path} (không tìm thấy file JSON tương ứng)")
        continue

    # Load dữ liệu nhấn chuột
    with open(json_path, "r") as f:
        mouse_data = json.load(f)

    # Đọc video
    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # FPS của video
    start_time = os.path.getctime(video_path)    # Timestamp bắt đầu video (tính bằng giây)

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Tính timestamp của khung hình hiện tại
        frame_timestamp = start_time + (frame_index / frame_rate)

        # Kiểm tra khung hình có gắn nhãn không
        label = None
        for event in mouse_data:
            if abs(frame_timestamp - event["timestamp"]) < 0.05:  # Sai số nhỏ (50ms)
                label = event["action"]
                break

        # Lưu khung hình có nhãn (nếu cần)
        if label:
            label_dir = os.path.join(output_dir, label)
            os.makedirs(label_dir, exist_ok=True)
            frame_name = f"{os.path.splitext(os.path.basename(video_path))[0]}_frame_{frame_index:04d}.jpg"
            cv2.imwrite(os.path.join(label_dir, frame_name), frame)

        frame_index += 1

    cap.release()
    print(f"Hoàn tất xử lý {video_path}")

print("Xử lý tất cả video hoàn tất!")
