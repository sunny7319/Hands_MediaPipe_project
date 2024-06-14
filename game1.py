import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from recognition_part import recognition
from recognition_lib import util
import mediapipe as mp
import datetime
import json
import os

# DB
######################################################################
# 저장된 게임 데이터를 담은 파일 경로
GAME_DATA_FILE = 'game1.json'

# 게임 데이터를 파일에 저장하는 함수
def save_game_data(x, y, stage):
    print('호출됨')
    if os.path.exists(GAME_DATA_FILE) and os.path.getsize(GAME_DATA_FILE) > 0:
        with open(GAME_DATA_FILE, 'r') as file:
            game_data = json.load(file)
    else:
        game_data = []

    new_entry = {
        'id':1,
        'page':1,
        'label': stage,
        'x_coordinate': x,
        'y_coordinate': y,
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'evaluation':1
    }

    game_data.append(new_entry)
    
    with open(GAME_DATA_FILE, 'w') as file:
        json.dump(game_data, file, indent=4)
    
    return True
######################################################################

# load
imgBg = cv2.imread("./game1/img/background_cam_1.jpg")
imgBg = cv2.resize(imgBg, (640, 480))

imgSun = cv2.imread("./game1/img/sun.png", cv2.IMREAD_UNCHANGED)
imgSun = cv2.resize(imgSun, (150, 150))

imgHeart = cv2.imread("./game1/img/heart.png", cv2.IMREAD_UNCHANGED)
imgHeart = cv2.resize(imgHeart, (380, 120))

imgFlower = cv2.imread("./game1/img/flower.png", cv2.IMREAD_UNCHANGED)
imgFlower = cv2.resize(imgFlower, (100, 80))

imgTree = cv2.imread("./game1/img/tree.png", cv2.IMREAD_UNCHANGED)
imgTree = cv2.resize(imgTree, (150, 300))

img_list_butterfly = []
for _, file_name in enumerate(os.listdir("./game1/img/img_gif_butterfly/")):
    temp = cv2.imread("./game1/img/img_gif_butterfly/" + file_name, cv2.IMREAD_UNCHANGED)
    temp = cv2.resize(temp, (80, 70))
    img_list_butterfly.append(temp)

img_list_cat = []
for _, file_name in enumerate(os.listdir("./game1/img/img_gif_cat/")):
    temp = cv2.imread("./game1/img/img_gif_cat/" + file_name, cv2.IMREAD_UNCHANGED)
    temp = cv2.resize(temp, (160, 150))
    img_list_cat.append(temp)

img_list_dog = []
for _, file_name in enumerate(os.listdir("./game1/img/img_gif_dog/")):
    temp = cv2.imread("./game1/img/img_gif_dog/" + file_name, cv2.IMREAD_UNCHANGED)
    temp = cv2.resize(temp, (320, 270))
    img_list_dog.append(temp)

# init

# data


###############################################################################################
# exe

stage_web = 1
quit = 0

def game1_frames():
    global stage_web
    global quit

    quit = 0
    x_coor = 0
    y_coor = 0

    cap = cv2.VideoCapture(0)
    segmentor = SelfiSegmentation()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5)

    # with mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5) as hands:
    dict_hand = util.make_dict_hand()

    loop = 1  # 0부터 시작하면 바로 인식해버림
    stage = 0
    latency = 1
    
    location = [(10,10), (30,110), (400,170), (200,10), (45,120), (20,170), (460,50)]
    # 해(6) 강아지(dog1/11) 고양이(1) 하트(4) 나비(0) 꽃(10) 나무(8)
    quiz_data = [6, 11, 1, 4, 0, 10, 8]

    # while True:
    while cap.isOpened():

        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        result = hands.process(img)
        imgOverlay = segmentor.removeBG(img, imgBg, cutThreshold=.1)

        if result.multi_hand_landmarks:
            recog = recognition(imgOverlay, result.multi_hand_landmarks, dict_hand, loop)
            recog.draw_load_hand()

            if loop % 10 == 0:
                detect_label = recog.recog_main()

                if detect_label:  # 레이블이 감지된 경우
                    print(detect_label[0][0])
                    label = detect_label[0][0]
                    print(label)

                    for i in range(len(detect_label)):
                        _, position = detect_label[i]

                    if label == quiz_data[stage]:
                        stage += 1

                        # 예: position이 [[x, y]] 형태라면
                        if isinstance(position[0], list):
                            x_coor = position[0][0]
                            y_coor = position[0][1]
                        else:
                            x_coor = position[0]
                            y_coor = position[1]

                        print(detect_label)
                        save_game_data(x_coor,y_coor,stage_web)

        if stage >= 1:
            imgOverlay = cvzone.overlayPNG(imgOverlay, imgSun, pos=location[0])
        if stage >= 2:
            imgOverlay = cvzone.overlayPNG(imgOverlay, img_list_dog[loop % 14], pos=location[1])
        if stage >= 3:
            imgOverlay = cvzone.overlayPNG(imgOverlay, img_list_cat[loop % 8], pos=location[2])
        if stage >= 4:
            imgOverlay = cvzone.overlayPNG(imgOverlay, imgHeart, pos=location[3])
        if stage >= 5:
            imgOverlay = cvzone.overlayPNG(imgOverlay, img_list_butterfly[loop % 20], pos=location[4])
        if stage >= 6:
            imgOverlay = cvzone.overlayPNG(imgOverlay, imgFlower, pos=location[5])
        if stage >= 7:
            imgOverlay = cvzone.overlayPNG(imgOverlay, imgTree, pos=location[6])

        # text1 = "stage = " + str(stage)
        # cv2.putText(imgOverlay, text1, (150, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        stage_web = stage
        
        ###############################################################################################
        # cv2.imshow("game2", imgOverlay)  # 화면 출력
        _, buffer = cv2.imencode('.jpg', imgOverlay)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # cv2.waitKey(latency)  # 값이 커지면 전체 while문 도는 속도(프레임)를 늦춘다.

        loop += 1

        # stage 진행 로직
        if stage >= 7:
            #################################### to survey
                # cv2.waitKey(1)
                print("to survey")
                cv2.waitKey(5000)
                hands.close()  # 손 인식 & 캠 종료(이하 3줄)
                cap.release()
                cv2.destroyAllWindows()
                quit = 1

        if cv2.waitKey(latency) & 0xFF == 27:  # ESC key to exit  # & 0xFF
            break


    hands.close()
    cap.release()
    cv2.destroyAllWindows()

def get_data_1():
    return stage_web, quit
