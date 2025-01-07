import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

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

# Custom Dataset
class PokemonDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted(os.listdir(root_dir))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        self.images = []
        self.labels = []
        
        for pokemon in self.classes:
            pokemon_dir = os.path.join(root_dir, pokemon)
            if not os.path.isdir(pokemon_dir):
                continue
                
            for root, dirs, files in os.walk(pokemon_dir):
                for file in files:
                    if file.endswith('.png'):
                        self.images.append(os.path.join(root, file))
                        self.labels.append(self.class_to_idx[pokemon])
        
        print(f"Found {len(self.images)} images across {len(self.classes)} classes")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGBA')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

# Model Architecture
class PokemonClassifier(nn.Module):
    def __init__(self, num_classes):
        super(PokemonClassifier, self).__init__()
        self.model = models.resnet18(pretrained=True)
        self.model.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        
    def forward(self, x):
        return self.model(x)

# Training Function
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs, device):
    best_acc = 0.0
    best_model_state = None
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} [Train]')
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        train_losses.append(epoch_loss)
        train_accuracies.append(epoch_acc)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(val_loader, desc=f'Epoch {epoch+1}/{num_epochs} [Val]')
            for images, labels in pbar:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                # Update progress bar
                pbar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'acc': f'{100.*correct/total:.2f}%'
                })
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * correct / total
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_state = model.state_dict().copy()
        
        print(f'\nEpoch {epoch+1}/{num_epochs}:')
        print(f'Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.2f}%')
        print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        print('-' * 60)
    
    return train_losses, val_losses, train_accuracies, val_accuracies, best_model_state

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
    
    # Data transforms
    train_transform = transforms.Compose([
        ToSilhouette(),
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    val_transform = transforms.Compose([
        ToSilhouette(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    # Dataset và DataLoader
    print("Loading datasets...")
    train_dataset = PokemonDataset('output_train', transform=train_transform)
    val_dataset = PokemonDataset('output_test', transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=4)
    
    # Model setup
    num_classes = len(train_dataset.classes)
    print(f"\nCreating model with {num_classes} classes...")
    model = PokemonClassifier(num_classes).to(device)
    
    # Loss và optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    print("\nStarting training...")
    num_epochs = 30
    train_losses, val_losses, train_accuracies, val_accuracies, best_model_state = train_model(
        model, train_loader, val_loader, criterion, optimizer, num_epochs, device
    )
    
    # Save best model
    print("\nSaving model...")
    torch.save({
        'model_state_dict': best_model_state,
        'classes': train_dataset.classes,
        'class_to_idx': train_dataset.class_to_idx
    }, 'pokemon_classifier_silhouette.pth')
    
    # Plot training history
    print("\nPlotting training history...")
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='Train Acc')
    plt.plot(val_accuracies, label='Val Acc')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_history_silhouette.png')
    plt.close()

    print("\nTraining completed!")

# Example usage for prediction
def predict_example():
    # Load model
    checkpoint = torch.load('pokemon_classifier_silhouette.pth')
    model = PokemonClassifier(len(checkpoint['classes']))
    model.load_state_dict(checkpoint['model_state_dict'])
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # Transform for prediction
    predict_transform = transforms.Compose([
        ToSilhouette(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    # Make prediction
    image_path = "path_to_your_test_image.png"
    predicted_class, confidence = predict_image(
        model, image_path, predict_transform, device, checkpoint['classes']
    )
    print(f"Predicted Pokemon: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")

if __name__ == '__main__':
    main()
    # Uncomment below line to run prediction example
    # predict_example()