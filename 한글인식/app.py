# app.py
from flask import Flask, request, render_template, jsonify
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import json
import os
import base64
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 모델 클래스 정의
def get_model(num_classes):
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 클래스 이름을 JSON 파일에서 로드
with open('C:\\Users\\BIG3-04\\Desktop\\모델\\class_names.json', 'r', encoding='utf-8') as f:
    class_names = json.load(f)

# 모델 초기화 및 로드
model = get_model(len(class_names)).to(device)
model.load_state_dict(torch.load("C:\\Users\\BIG3-04\\Desktop\\모델\\finalLLL_model.pth"))
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
    return predicted_class, predicted_prob

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture_image():
    data = request.get_json()
    img_data = data['image']
    img_data = img_data.split(",")[1]
    img = Image.open(BytesIO(base64.b64decode(img_data)))
    predicted_class, predicted_prob = predict_image(img)
    return jsonify({'class': predicted_class, 'probability': predicted_prob})

if __name__ == "__main__":
    app.run(debug=True)
