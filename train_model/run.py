import torch
from torchvision import transforms
from PIL import Image
from train import PokemonClassifier, ToSilhouette, predict_image

# Đường dẫn đến model đã lưu
MODEL_PATH = "pokemon_classifier_silhouette.pth"
IMAGE_PATH = "output_test\\wyrdeer\\all\\base\\none\\noise1.png"  # Đường dẫn đến ảnh cần dự đoán

def load_model(model_path, device):
    # Load thông tin từ file checkpoint
    checkpoint = torch.load(model_path, map_location=device)
    model = PokemonClassifier(len(checkpoint['classes']))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    return model, checkpoint['classes']

def main():
    # Xác định thiết bị (GPU/CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    model, class_names = load_model(MODEL_PATH, device)
    print("Model loaded successfully!")
    
    # Chuẩn bị transform cho ảnh đầu vào
    transform = transforms.Compose([
        ToSilhouette(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    # Dự đoán ảnh
    predicted_class, confidence = predict_image(model, IMAGE_PATH, transform, device, class_names)
    
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")

if __name__ == "__main__":
    main()
