import torch
import torch.nn as nn
import torchvision.models as models
import cv2
from torchvision import transforms
from PIL import Image
import json

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
    transforms.Grayscale(num_output_channels=1),  # 흑백 이미지로 변환
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

def predict_image(image):
    img_tensor = transform(image).unsqueeze(0).to(device)

    # 모델에 입력
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted.item()]
        predicted_prob = probabilities[0][predicted.item()].item()

    return predicted_class, predicted_prob, probabilities[0].cpu().numpy()

def classify_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        cv2.imshow('Webcam', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            # 이미지를 PIL 형식으로 변환
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # 이미지 변환 및 예측
            predicted_class, predicted_prob, probabilities = predict_image(img)

            # 예측 결과를 출력
            print(f'예측된 클래스: {predicted_class} ({predicted_prob:.2f})')

            # 각 클래스별 확률 출력
            for i, prob in enumerate(probabilities):
                print(f'{class_names[i]}: {prob:.4f}')

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    classify_webcam()
