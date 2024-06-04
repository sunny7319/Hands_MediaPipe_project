import os
import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

frame_count = 0
time_clock = 0
latency = 1  # 지연시간(ms)
fps = 1000/latency  # float
##########################################################################################################
fps_real = fps/64  # 실제 fps는 while문 연산속도에 달려있음, 보정값으로 나눠줘야 함, 보정값과 time_clock은 비례
rock_gesture_sensitivity = 0.05
##########################################################################################################

def is_rock_gesture(hand_landmarks, rock_gesture_sensitivity):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_dip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP]
    middle_dip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
    ring_dip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP]
    pinky_dip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP]
    
    # Check if all finger tips are close to the respective DIPs (indicating a closed fist)
    if (abs(thumb_tip.x - thumb_ip.x) < rock_gesture_sensitivity and abs(thumb_tip.y - thumb_ip.y) < rock_gesture_sensitivity and
        abs(index_tip.x - index_dip.x) < rock_gesture_sensitivity and abs(index_tip.y - index_dip.y) < rock_gesture_sensitivity and
        abs(middle_tip.x - middle_dip.x) < rock_gesture_sensitivity and abs(middle_tip.y - middle_dip.y) < rock_gesture_sensitivity and
        abs(ring_tip.x - ring_dip.x) < rock_gesture_sensitivity and abs(ring_tip.y - ring_dip.y) < rock_gesture_sensitivity and
        abs(pinky_tip.x - pinky_dip.x) < rock_gesture_sensitivity and abs(pinky_tip.y - pinky_dip.y) < rock_gesture_sensitivity):
        return True
    return False

cap = cv2.VideoCapture(0)
segmentor = SelfiSegmentation()

imgBg = np.zeros((480, 640, 3), dtype=np.uint8)
imgBg[:] = (0, 255, 0)

while cap.isOpened():

    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    result = hands.process(img)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Check if the detected hand is in 'rock' gesture
            if is_rock_gesture(hand_landmarks, rock_gesture_sensitivity):

                middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

                x = int(middle_pip.x*640)
                y = int(middle_pip.y*480)

                cv2.circle(img, (x, y), 10, (0, 0, 255), 5)

    imgOut = segmentor.removeBG(img, imgBg, cutThreshold=.1)

    frame_count += 1 #####################################################
    time_clock = int(frame_count / int(fps_real)) ########################
    print(time_clock) ####################################################

    text = "time = " + str(time_clock)
    cv2.putText(imgOut, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


    cv2.imshow("imgOut", imgOut)

    cv2.waitKey(latency)  # 값이 커지면 전체 while문 도는 속도(프레임)를 늦춘다.

    if cv2.waitKey(latency) & 0xFF == ord('a'):  # 여기만 값을 키우면 키 입력만 답답하게 받는다.
        print('a')
    if cv2.waitKey(latency) & 0xFF == 27:  # ESC key to exit  # & 0xFF
        break

hands.close()
cap.release()
cv2.destroyAllWindows()