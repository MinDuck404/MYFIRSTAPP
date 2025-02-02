from PIL import Image, ImageOps
import numpy as np
import torch
from torchvision import transforms
from train import PokemonClassifier, predict_image

# Đường dẫn model và ảnh
MODEL_PATH = "pokemon_classifier_silhouette.pth"
IMAGE_PATH = r"C:\Users\duccj\Downloads\image.png"

def remove_background(image_path):
    # Mở ảnh
    image = Image.open(image_path).convert("RGBA")
    data = np.array(image)
    
    # Tách kênh màu RGBA
    r, g, b, a = data.T
    
    # Xác định các pixel màu đen (hoặc gần đen)
    black_areas = (r < 50) & (g < 50) & (b < 50)  # Điều kiện màu đen
    
    # Xóa nền: pixel không phải màu đen => trong suốt
    data[..., -1][~black_areas.T] = 0  # Kênh alpha = 0 (trong suốt) với pixel không đen
    
    # Tạo ảnh mới
    result_image = Image.fromarray(data)
    return result_image

def main():
    # Xác định thiết bị
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model = PokemonClassifier(len(checkpoint['classes']))
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    
    # Danh sách lớp
    class_names = checkpoint['classes']
    
    # Chuẩn bị transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    # Tách nền và lưu ảnh
    processed_image = remove_background(IMAGE_PATH)
    processed_image.save("processed_image.png")  # Lưu lại ảnh đã xử lý (tùy chọn)
    
    # Chuyển từ RGBA sang RGB trước khi đưa vào model
    processed_image_rgb = processed_image.convert("RGB")
    processed_image_tensor = transform(processed_image_rgb).unsqueeze(0).to(device)
    
    # Dự đoán
    model.eval()
    with torch.no_grad():
        outputs = model(processed_image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = probabilities.max(1)
    
    print(f"Predicted Class: {class_names[predicted.item()]}")
    print(f"Confidence: {confidence.item():.2%}")

if __name__ == "__main__":
    main()
