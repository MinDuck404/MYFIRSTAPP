import cv2
import numpy as np
import os
import time
import json
from mss import mss
from pynput import keyboard, mouse

# Tọa độ vùng quét (x1, y1, x2, y2)
region = {"top": 545, "left": 644, "width": 1289 - 644, "height": 577 - 545}

# Thư mục lưu video và dữ liệu
output_dir = "training_data"
os.makedirs(output_dir, exist_ok=True)

# Biến trạng thái quay
recording = False
video_writer = None
mouse_data = [] 
video_name = None  # Để lưu tên video hiện tại

# Tên video ngẫu nhiên
def create_random_video_name():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"video_{timestamp}.avi")

# Ghi lại nhấn chuột
def on_click(x, y, button, pressed):
    if pressed and recording:  # Chỉ ghi lại khi đang quay
        action = "right_click" if button == mouse.Button.right else "left_click"
        timestamp = time.time()
        mouse_data.append({"timestamp": timestamp, "action": action, "x": x, "y": y})
        print(f"Mouse {action} at ({x}, {y}) logged.")

# Listener chuột
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

# Bàn phím điều khiển
def on_press(key):
    global recording, video_writer, mouse_data, video_name

    try:
        if key.char == "`":  # Nhấn ` để bắt đầu/dừng quay
            if not recording:
                print("Bắt đầu quay video...")
                recording = True
                video_name = create_random_video_name()
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                video_writer = cv2.VideoWriter(video_name, fourcc, 20.0, (region["width"], region["height"]))
                mouse_data = []  # Reset dữ liệu chuột
            else:
                print("Dừng quay video...")
                recording = False
                if video_writer:
                    video_writer.release()
                    video_writer = None

                # Lưu dữ liệu nhấn chuột vào file JSON
                data_file = video_name.replace(".avi", ".json")
                with open(data_file, "w") as f:
                    json.dump(mouse_data, f, indent=4)
                print(f"Dữ liệu chuột lưu tại: {data_file}")
    except AttributeError:
        pass

# Listener bàn phím
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

# Hàm quay video
def record_screen():
    global recording, video_writer
    sct = mss()
    print("Nhấn ` để bắt đầu/dừng quay video. Nhấn ESC để thoát.")

    try:
        while True:
            if recording:
                # Chụp màn hình trong vùng chỉ định
                frame = np.array(sct.grab(region))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # Ghi khung hình vào video
                if video_writer:
                    video_writer.write(frame)

                # Hiển thị khung hình (tuỳ chọn)
                cv2.imshow("Recording", frame)

            # Dừng nếu nhấn ESC
            if cv2.waitKey(1) & 0xFF == 27:  # Nhấn ESC để thoát
                break
    except KeyboardInterrupt:
        print("Thoát chương trình.")
    finally:
        if recording and video_writer:
            print("Tự động dừng và lưu video khi thoát.")
            recording = False
            video_writer.release()
            data_file = video_name.replace(".avi", ".json")
            with open(data_file, "w") as f:
                json.dump(mouse_data, f, indent=4)
            print(f"Dữ liệu chuột lưu tại: {data_file}")
        cv2.destroyAllWindows()

# Chạy hàm quay video
record_screen()
keyboard_listener.stop()
mouse_listener.stop()
