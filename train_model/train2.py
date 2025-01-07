import torch
import json
from torchvision import transforms
from PIL import Image
import numpy as np
import torch.nn as nn
from torchvision import models


# Custom Transform để chuyển ảnh thành silhouette
class ToSilhouette:
    def __call__(self, img):
        # Chuyển sang numpy array
        img_np = np.array(img)
        
        # Tạo mask cho các pixel không trong suốt (alpha > 0)
        if img_np.shape[2] == 4:  # Nếu có alpha channel
            mask = img_np[:, :, 3] > 0
        else:  # Nếu không có alpha channel, dùng threshold trên độ sáng
            mask = np.mean(img_np, axis=2) > 0
            
        # Tạo ảnh silhouette
        silhouette = np.zeros(img_np.shape[:2], dtype=np.uint8)
        silhouette[mask] = 255
        
        # Chuyển lại về PIL Image với 3 channels
        return Image.fromarray(silhouette).convert('RGB')

# Model Architecture
class PokemonClassifier(nn.Module):
    def __init__(self, num_classes):
        super(PokemonClassifier, self).__init__()
        self.model = models.resnet18(pretrained=True)
        self.model.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        
    def forward(self, x):
        return self.model(x)

# Prediction function
def predict_image(model, image_path, transform, device, class_names):
    # Load and transform image
    image = Image.open(image_path).convert('RGBA')
    image = transform(image).unsqueeze(0).to(device)
    
    # Get prediction
    model.eval()
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = probabilities.max(1)
        
    return class_names[predicted.item()], confidence.item()

def main():
    # Set random seed for reproducibility
    torch.manual_seed(42)
    torch.cuda.manual_seed(42)
    np.random.seed(42)
    
    # Check GPU availability
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # Load class indices from JSON file
    with open('class_indices.json', 'r') as f:
        class_indices = json.load(f)
    class_names = {v: k for k, v in class_indices.items()}
    
    # Load model
    checkpoint = torch.load('pokemon_classifier_silhouette.pth')
    model = PokemonClassifier(len(class_names))
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    
    # Transform for prediction
    predict_transform = transforms.Compose([
        ToSilhouette(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    # Make prediction
    image_path = "output_test\\charizard\\all\\base\\none\\noise1.png"  # Thay đổi đường dẫn hình ảnh
    predicted_class, confidence = predict_image(
        model, image_path, predict_transform, device, class_names
    )
    print(f"Predicted Pokemon: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")

if __name__ == '__main__':
    main()
