import cv2
import mediapipe as mp
import numpy as np
import os
from classgo import Moving
from recognition_lib import util
from recognition_part import recognition
from tensorflow.keras.models import load_model

# TensorFlow warning 제거
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 모델 로드 및 컴파일
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5)
cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 웹캠 스트리밍 함수(게임 대기화면 mediapipe 확인 캠)
def check_frames():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Load GIF files
nabi_1 = cv2.VideoCapture('outpart_lib/butterfly_1.gif')
nabi_2 = cv2.VideoCapture('outpart_lib/butterfly_3.gif')
nabi_3 = cv2.VideoCapture('outpart_lib/butterfly_4.gif')

cat_1 = cv2.VideoCapture('outpart_lib/cat_1.gif')
cat_2 = cv2.VideoCapture('outpart_lib/cat_2.gif')
cat_3 = cv2.VideoCapture('outpart_lib/cat_3.gif')

snail_1 = cv2.VideoCapture('outpart_lib/snail_1.gif')
snail_2 = cv2.VideoCapture('outpart_lib/snail_2.gif')
snail_3 = cv2.VideoCapture('outpart_lib/snail_3.gif')

deer_1 = cv2.VideoCapture('outpart_lib/deer.gif')
deer_2 = cv2.VideoCapture('outpart_lib/deer_1.gif')
deer_3 = cv2.VideoCapture('outpart_lib/deer_2.gif')

heart_1 = cv2.VideoCapture('outpart_lib/heart.gif')
heart_2 = cv2.VideoCapture('outpart_lib/heart.gif')
heart_3 = cv2.VideoCapture('outpart_lib/heart.gif')

duck_1 = cv2.VideoCapture('outpart_lib/duck_1.gif')
duck_2 = cv2.VideoCapture('outpart_lib/duck_2.gif')
duck_3 = cv2.VideoCapture('outpart_lib/duck_3.gif')

sun_1 = cv2.VideoCapture('outpart_lib/sun.gif')
sun_2 = cv2.VideoCapture('outpart_lib/sun.gif')
sun_3 = cv2.VideoCapture('outpart_lib/sun.gif')

house_1 = cv2.VideoCapture('outpart_lib/house.gif')
house_2 = cv2.VideoCapture('outpart_lib/house.gif')
house_3 = cv2.VideoCapture('outpart_lib/house.gif')

tree_1 = cv2.VideoCapture('outpart_lib/tree.gif')
tree_2 = cv2.VideoCapture('outpart_lib/tree.gif')
tree_3 = cv2.VideoCapture('outpart_lib/tree.gif')

rock_1 = cv2.VideoCapture('outpart_lib/rock.gif')
rock_2 = cv2.VideoCapture('outpart_lib/rock.gif')
rock_3 = cv2.VideoCapture('outpart_lib/rock.gif')

flower_1 = cv2.VideoCapture('outpart_lib/flower.gif')
flower_2 = cv2.VideoCapture('outpart_lib/flower.gif')
flower_3 = cv2.VideoCapture('outpart_lib/flower.gif')

dog_1 = cv2.VideoCapture('outpart_lib/dog_1.gif')
dog_2 = cv2.VideoCapture('outpart_lib/dog_3.gif')
dog_3 = cv2.VideoCapture('outpart_lib/dog_7.gif')

def reset_gif(gif):
    gif.set(cv2.CAP_PROP_POS_FRAMES, 0)

score = 0
position2 = [0, 0]
current_image_info = []
def generate_frames():
    global score
    global position2
    global current_image_info
    with mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5) as hands:
        counting = 1
        dict_hand = util.make_dict_hand()
        while True:
            success, image = cap.read()
            if not success:
                break

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            nw, nh = image.shape[1], image.shape[0]

            if results.multi_hand_landmarks:
                recog = recognition(image, results.multi_hand_landmarks, dict_hand, counting)
                recog.draw_load_hand()

                if counting % 10 == 0:
                    detect_label = recog.recog_main()

                    if detect_label:    # 레이블이 감지된 경우
                        for i in range(len(detect_label)):
                            label, position = detect_label[i]
                            position2 = convert_position(position)
                            save_game_data(label, position2)
                            # 예: position이 [[x, y]] 형태라면
                            if isinstance(position[0], list):
                                x_c = int(position[0][0] * nw)
                                y_c = int(position[0][1] * nh)
                            else:
                                x_c = int(position[0] * nw)
                                y_c = int(position[1] * nh)

                            if label == 0:
                                rndN = np.random.randint(1, 4)
                                # nabi = [nabi_1, nabi_2, nabi_3][rndN - 1]
                                # if x_c + 100 > nw or y_c + 100 > nh:
                                #     x_c, y_c = nw - 100, nh - 100
                                # flag.append(Moving(nabi, x_c, y_c, 100, 100, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 1:
                                rndN = np.random.randint(1, 4)
                                # cat = [cat_1, cat_2, cat_3][rndN - 1]
                                # if x_c + 200 > nw or y_c + 200 > nh:
                                #     x_c, y_c = nw - 200, nh - 200
                                # flag.append(Moving(cat, x_c, y_c, 200, 200, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 2:
                                rndN = np.random.randint(1, 4)
                                # snail = [snail_1, snail_2, snail_3][rndN - 1]
                                # if x_c + 70 > nw or y_c + 70 > nh:
                                #     x_c, y_c = nw - 70, nh - 70
                                # flag.append(Moving(snail, x_c, y_c, 70, 70, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 3:
                                rndN = np.random.randint(1, 4)
                                # deer = [deer_1, deer_2, deer_3][rndN - 1]
                                if x_c + 300 > nw or y_c + 300 > nh:
                                    x_c, y_c = nw - 300, nh - 300
                                # flag.append(Moving(deer, x_c, y_c, 300, 300, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 4:
                                rndN = np.random.randint(1, 4)
                                # heart = [heart_1, heart_2, heart_3][rndN - 1]
                                if x_c + 100 > nw or y_c + 100 > nh:
                                    x_c, y_c = nw - 100, nh - 100
                                # flag.append(Moving(heart, x_c, y_c, 100, 100, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 5:
                                rndN = np.random.randint(1, 4)
                                # duck = [duck_1, duck_2, duck_3][rndN - 1]
                                if x_c + 150 > nw or y_c + 150 > nh:
                                    x_c, y_c = nw - 150, nh - 150
                                # flag.append(Moving(duck, x_c, y_c, 150, 150, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 6:
                                rndN = np.random.randint(1, 4)
                                # sun = [sun_1, sun_2, sun_3][rndN - 1]
                                if x_c + 180 > nw or y_c + 180 > nh:
                                    x_c, y_c = nw - 180, nh - 180
                                # flag.append(Moving(sun, x_c, y_c, 180, 180, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 7:
                                rndN = np.random.randint(1, 4)
                                # house = [house_1, house_2, house_3][rndN - 1]
                                if x_c + 400 > nw or y_c + 400 > nh:
                                    x_c, y_c = nw - 400, nh - 400
                                # flag.append(Moving(house, x_c, y_c, 400, 400, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 8:
                                rndN = np.random.randint(1, 4)
                                # tree = [tree_1, tree_2, tree_3][rndN - 1]
                                if x_c + 350 > nw or y_c + 350 > nh:
                                    x_c, y_c = nw - 350, nh - 350
                                # flag.append(Moving(tree, x_c, y_c, 350, 350, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 9:
                                rndN = np.random.randint(1, 4)
                                # rock = [rock_1, rock_2, rock_3][rndN - 1]
                                if x_c + 120 > nw or y_c + 120 > nh:
                                    x_c, y_c = nw - 120, nh - 120
                                # flag.append(Moving(rock, x_c, y_c, 120, 120, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 10:
                                rndN = np.random.randint(1, 4)
                                # flower = [flower_1, flower_2, flower_3][rndN - 1]
                                if x_c + 70 > nw or y_c + 70 > nh:
                                    x_c, y_c = nw - 70, nh - 70
                                size = 70
                                way = 0
                                # flag.append(Moving(flower, x_c, y_c, 70, 70, 0))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

                            elif label == 11:
                                rndN = np.random.randint(1, 4)
                                # dog = [dog_1, dog_2, dog_3][rndN - 1]
                                if x_c + 100 > nw or y_c + 100 > nh:
                                    x_c, y_c = nw - 100, nh - 100
                                # flag.append(Moving(dog, x_c, y_c, 100, 100, 1))
                                # print(f"현재 라벨과 좌표는 label: {label}, position: {position2}")

            counting += 1
            score += 1
            # 혹시 모르니 원본코드 지우지 말것
            # for obj in flag:
            #     frame = obj.gif.read()[1]
            #     if frame is not None and frame.size != 0:
            #         obj.frame = cv2.resize(frame, (obj.resize_x, obj.resize_y))
            #         if obj.way == 1:
            #             obj.frame = cv2.flip(obj.frame, 1)
            #         image[obj.rp[obj.c][1]:obj.rp[obj.c][1] + obj.frame.shape[0],
            #             obj.rp[obj.c][0]:obj.rp[obj.c][0] + obj.frame.shape[1]] = obj.frame
            #     reset_gif(obj.gif)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def get_score():
    return score

def get_position():
    return position2, current_image_info

def get_labels_positions():
    global detect_label
    return detect_label

def convert_position(posi):
    video_width = 1173.33
    video_height = 880
    
    # 비디오의 시작 좌표 (화면 중앙 배치 기준)
    start_x = (1920 - video_width) / 2  # = 373.33
    start_y = 100
    
    # 변환 공식 적용
    if isinstance(posi[0], list):
        X = posi[0][0] * video_width + start_x
        Y = posi[0][1] * video_height + start_y
    else:
        X = posi[0] * video_width + start_x
        Y = posi[1] * video_height + start_y
    
    return X, Y

import json
import datetime
# 저장된 게임 데이터를 담은 파일 경로
GAME_DATA_FILE = 'active1.json'

# 게임 데이터를 파일에 저장하는 함수
def save_game_data(label, position2):
    if os.path.exists(GAME_DATA_FILE) and os.path.getsize(GAME_DATA_FILE) > 0:
        with open(GAME_DATA_FILE, 'r') as file:
            game_data = json.load(file)
    else:
        game_data = []

    new_entry = {
        'id':1,
        'page':1,
        'label': label,
        'x_coordinate': position2[0],
        'y_coordinate': position2[1],
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'score':1,
        'evaluation':1
    }

    game_data.append(new_entry)
    
    with open(GAME_DATA_FILE, 'w') as file:
        json.dump(game_data, file, indent=4)
    
    return True