import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import json
import os

# 모델 클래스 정의
def get_model(num_classes):
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 현재 파일의 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 클래스 이름을 JSON 파일에서 로드
class_names_path = os.path.join(BASE_DIR, 'game3', 'class_names.json')
with open(class_names_path, 'r', encoding='utf-8') as f:
    class_names = json.load(f)

# 모델 초기화 및 로드
model_path = os.path.join(BASE_DIR, 'game3', 'finalLLL_model.pth')
model = get_model(len(class_names)).to(device)
model.load_state_dict(torch.load(model_path))
model.eval()

# 전처리 파이프라인 설정
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

def predict_image(image):
    img_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted.item()]
        predicted_prob = probabilities[0][predicted.item()].item()
        print(predicted_class, predicted_prob)
    return predicted_class, predicted_prob