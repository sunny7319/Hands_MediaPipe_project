import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import time
import os

cap = cv2.VideoCapture(0)
segmentor = SelfiSegmentation()

ret, frame = cap.read()
imgBg = cv2.imread("./bg3.jpg")
imgBg = cv2.resize(imgBg, (frame.shape[1], frame.shape[0]))  # 누끼 뒷배경 크기가 프레임 크기와 맞아야 한다.

img_list = []
for _, file_name in enumerate(os.listdir("./img/")):
    temp = cv2.imread("./img/" + file_name, cv2.IMREAD_UNCHANGED)
    temp = cv2.resize(temp, (110, 100))
    img_list.append(temp)

num = 0
while cap.isOpened():  # print(time.time())
    success, img = cap.read()
    imgOut = segmentor.removeBG(cv2.flip(img, 1), imgBg, cutThreshold=.1)

    num = num % 20  # print(num)

    x = 25
    y = 25
    imgOverlay = cvzone.overlayPNG(imgOut, img_list[num], pos=[x, y])

    cv2.imshow("imgOverlay", imgOverlay)
    cv2.waitKey(1)  # 값이 커지면 전체 while문 도는 속도(프레임)를 늦춘다.

    num += 1

    if cv2.waitKey(1) == ord('a'):  # 여기만 값을 키우면 키 입력만 답답하게 받는다.
        print('a')
    if cv2.waitKey(1) == 27:  # ESC key to exit  # & 0xFF
        break

cap.release()
cv2.destroyAllWindows()
