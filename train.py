import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
import os

# Đường dẫn dữ liệu
data_dir = "labeled_frames"
model_save_path = "trained_model.keras"

# Các tham số
img_width, img_height = 64, 64  # Kích thước ảnh đầu vào
batch_size = 32
epochs = 10

# 1. Tạo ImageDataGenerator để load và tiền xử lý dữ liệu
datagen = ImageDataGenerator(
    rescale=1.0 / 255,          # Chuẩn hóa giá trị pixel về [0, 1]
    validation_split=0.2       # Chia 20% dữ liệu làm tập validation
)

# Load dữ liệu train và validation
train_generator = datagen.flow_from_directory(
    data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="categorical",
    subset="training"           # Sử dụng cho tập train
)

validation_generator = datagen.flow_from_directory(
    data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation"         # Sử dụng cho tập validation
)

# 2. Xây dựng mô hình CNN
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(img_width, img_height, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation="softmax")  # Số lớp tương ứng số nhãn
])

# 3. Compile mô hình
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 4. Thiết lập callback để lưu mô hình tốt nhất
checkpoint = ModelCheckpoint(
    model_save_path,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

# 5. Train mô hình
print("Bắt đầu train mô hình...")
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=validation_generator,
    callbacks=[checkpoint]
)

# 6. Lưu mô hình cuối cùng
model.save(model_save_path)
print(f"Đã lưu mô hình tại: {model_save_path}")
