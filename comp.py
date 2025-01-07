import os
import json
# Đường dẫn đến thư mục train
train_dir = "output_train"

# Lấy danh sách các lớp từ thư mục
class_names = sorted(os.listdir(train_dir))

# Tạo ánh xạ giữa chỉ số lớp và tên lớp
class_indices = {class_name: idx for idx, class_name in enumerate(class_names)}
class_indices_reversed = {v: k for k, v in class_indices.items()}

# Lưu danh sách lớp vào JSON để sử dụng sau này

with open("class_indices.json", "w") as json_file:
    json.dump(class_indices, json_file)

print("Class indices saved to class_indices.json")
