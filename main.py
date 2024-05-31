import cv2
import mediapipe as mp
import numpy as np
from classgo import Moving
from recognition_lib import util
from recognition_part import recognition

# TensorFlow warning 제거
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

# Variable initialization
mp_hands = mp.solutions.hands

# 웹캠 비디오 캡처 객체 초기화
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 이미지 불러오기
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

# gif를 생성하면 프레임 위치를 처음으로 초기화 해주는 함수
def reset_gif(gif):
    gif.set(cv2.CAP_PROP_POS_FRAMES, 0)

# 모션인식 
with mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5) as hands:

    counting = 1
    dict_hand = util.make_dict_hand()
    flag = []

    # q키를 누르면 웹캠 꺼짐
    while cv2.waitKey(10) != ord('q'):
        success, image = cap.read()
        if not success:
            continue
        
        # OpenCV를 사용하여 이미지를 좌우 반전하고 색상 공간을 BGR에서 RGB로 변환
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # MediaPipe Hands 모듈을 사용하여 손 탐지 수행
        results = hands.process(image)
        # 다시 이미지를 RGB에서 BGR로 변환
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # 이미지의 너비와 높이를 변수에 저장
        nw, nh = image.shape[1], image.shape[0]

        if results.multi_hand_landmarks:
            # 손이 인식되면
            recog = recognition(image, results.multi_hand_landmarks, dict_hand, counting)
            recog.draw_load_hand()  # 손의 인식선을 그려줌

            if counting % 10 == 0:
                # counting 값이 10의 배수일 때만 인식 수행
                detect_label = recog.recog_main()  # 손의 인식을 수행하여 레이블을 반환

                if detect_label:
                    # 레이블이 감지된 경우
                    for i in range(len(detect_label)):
                        label, position = detect_label[i]
                        print(f"label: {label}, position: {position}")  # position 구조 확인

                        # 예: position이 [[x, y]] 형태라면
                        if isinstance(position[0], list):
                            x_c = int(position[0][0] * nw)
                            y_c = int(position[0][1] * nh)
                        else:
                            x_c = int(position[0] * nw)
                            y_c = int(position[1] * nh)

                        if label == 0:
                            # 레이블이 0인 경우
                            rndN = np.random.randint(1, 4)  # 1에서 3까지의 랜덤 이미지 생성
                            if rndN == 1:
                                nabi = nabi_1
                            elif rndN == 2:
                                nabi = nabi_2
                            elif rndN == 3:
                                nabi = nabi_3
                            
                            # 이미지가 화면을 벗어나지 않도록 좌표 조정
                            if (x_c + 100 > nw) or (y_c + 100 > nh):
                                x_c = nw - 100
                                y_c = nh - 100

                            # Moving 객체를 생성하여 flag 리스트에 추가
                            flag.append(Moving(nabi, x_c, y_c, 100, 100, 1))


                        elif label == 1:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                cat = cat_1
                            elif rndN == 2:
                                cat = cat_2
                            elif rndN == 3:
                                cat = cat_3
                            if (x_c + 200 > nw) or (y_c + 200 > nh):
                                x_c = nw - 200
                                y_c = nh - 200
                            flag.append(Moving(cat, x_c, y_c, 200, 200, 1))

                        elif label == 2:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                snail = snail_1
                            elif rndN == 2:
                                snail = snail_2
                            elif rndN == 3:
                                snail = snail_3
                            if (x_c + 70 > nw) or (y_c + 70 > nh):
                                x_c = nw - 70
                                y_c = nh - 70
                            flag.append(Moving(snail, x_c, y_c, 70, 70, 1))

                        elif label == 3:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                deer = deer_1
                            elif rndN == 2:
                                deer = deer_2
                            elif rndN == 3:
                                deer = deer_3
                            if (x_c + 300 > nw) or (y_c + 300 > nh):
                                x_c = nw - 300
                                y_c = nh - 300
                            flag.append(Moving(deer, x_c, y_c, 300, 300, 1))

                        elif label == 4:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                heart = heart_1
                            elif rndN == 2:
                                heart = heart_2
                            elif rndN == 3:
                                heart = heart_3
                            if (x_c + 100 > nw) or (y_c + 100 > nh):
                                x_c = nw - 100
                                y_c = nh - 100
                            flag.append(Moving(heart, x_c, y_c, 100, 100, 0))

                        elif label == 5:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                duck = duck_1
                            elif rndN == 2:
                                duck = duck_2
                            elif rndN == 3:
                                duck = duck_3
                            if (x_c + 150 > nw) or (y_c + 150 > nh):
                                x_c = nw - 150
                                y_c = nh - 150
                            flag.append(Moving(duck, x_c, y_c, 150, 150, 1))

                        elif label == 6:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                sun = sun_1
                            elif rndN == 2:
                                sun = sun_2
                            elif rndN == 3:
                                sun = sun_3
                            if (x_c + 180 > nw) or (y_c + 180 > nh):
                                x_c = nw - 180
                                y_c = nh - 180
                            flag.append(Moving(sun, x_c, y_c, 180, 180, 0))

                        elif label == 7:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                house = house_1
                            elif rndN == 2:
                                house = house_2
                            elif rndN == 3:
                                house = house_3
                            if (x_c + 400 > nw) or (y_c + 400 > nh):
                                x_c = nw - 400
                                y_c = nh - 400
                            flag.append(Moving(house, x_c, y_c, 400, 400, 0))

                        elif label == 8:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                tree = tree_1
                            elif rndN == 2:
                                tree = tree_2
                            elif rndN == 3:
                                tree = tree_3
                            if (x_c + 350 > nw) or (y_c + 350 > nh):
                                x_c = nw - 350
                                y_c = nh - 350
                            flag.append(Moving(tree, x_c, y_c, 350, 350, 0))

                        elif label == 9:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                rock = rock_1
                            elif rndN == 2:
                                rock = rock_2
                            elif rndN == 3:
                                rock = rock_3
                            if (x_c + 120 > nw) or (y_c + 120 > nh):
                                x_c = nw - 120
                                y_c = nh - 120
                            flag.append(Moving(rock, x_c, y_c, 120, 120, 0))
                        
                        elif label == 10:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                flower = flower_1
                            elif rndN == 2:
                                flower = flower_2
                            elif rndN == 3:
                                flower = flower_3
                            if (x_c + 70 > nw) or (y_c + 70 > nh):
                                x_c = nw - 70
                                y_c = nh - 70
                            flag.append(Moving(flower, x_c, y_c, 70, 70, 0))

                        elif label == 11:
                            rndN = np.random.randint(1, 4)
                            if rndN == 1:
                                dog = dog_1
                            elif rndN == 2:
                                dog = dog_2
                            elif rndN == 3:
                                dog = dog_3
                            if (x_c + 100 > nw) or (y_c + 100 > nh):
                                x_c = nw - 100
                                y_c = nh - 100
                            flag.append(Moving(dog, x_c, y_c, 100, 100, 1))
        # 모션을 인식하면 counting 1 증가
        counting += 1

        for obj in flag:
            frame = obj.gif.read()[1]
            if frame is not None and frame.size != 0:
                # 객체가 생선된 경우 Moving클래스에서 resize_x,y 객체 크기 조정
                obj.frame = cv2.resize(frame, (obj.resize_x, obj.resize_y))
                # way값은 랜덤생성(0~4) way값이 1일 경우 좌우반전형태로 생성 (classgo.py[moving 클래스] -> sbshso.py [FirstGo 클래스])
                if obj.way == 1:
                    obj.frame = cv2.flip(obj.frame, 1)
                image[obj.rp[obj.c][1]:obj.rp[obj.c][1] + obj.frame.shape[0],
                      obj.rp[obj.c][0]:obj.rp[obj.c][0] + obj.frame.shape[1]] = obj.frame
            reset_gif(obj.gif)

        # 현재 프레임을 화면에 표시
        cv2.imshow('Capstone_test', image)

cv2.destroyAllWindows()
cap.release()