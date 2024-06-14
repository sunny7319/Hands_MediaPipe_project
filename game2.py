import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from PIL import Image, ImageDraw, ImageFont
import mediapipe as mp
import numpy as np
import datetime
import random
import json
import os

# func
def is_rock_gesture(hand_landmarks, rock_gesture_sensitivity, mp_hands):
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

# DB
######################################################################
# 저장된 게임 데이터를 담은 파일 경로
GAME_DATA_FILE = 'game2.json'

# 게임 데이터를 파일에 저장하는 함수
def save_game_data(x, y, score, stage):
    print('호출됨')
    if os.path.exists(GAME_DATA_FILE) and os.path.getsize(GAME_DATA_FILE) > 0:
        with open(GAME_DATA_FILE, 'r') as file:
            game_data = json.load(file)
    else:
        game_data = []

    new_entry = {
        'id':1,
        'page':2,
        'x_coordinate': x,
        'y_coordinate': y,
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'score':score,
        'stage':stage,
        'evaluation':1
    }

    game_data.append(new_entry)
    
    with open(GAME_DATA_FILE, 'w') as file:
        json.dump(game_data, file, indent=4)
    
    return True
######################################################################

# load
font = ImageFont.truetype("./game2/font/Kyobo.ttf", 45)

imgBg = cv2.imread("./game2/img/background_cam_2.jpg")
# imgBg = cv2.resize(imgBg[:, 640:], (640, 480))  # (frame.shape[1], frame.shape[0])
imgBg = cv2.resize(imgBg, (640, 480))

imgHammer = cv2.imread("./game2/img/hammer.png", cv2.IMREAD_UNCHANGED)
imgHammer = cv2.resize(imgHammer, (150, 150))

imgMole = cv2.imread("./game2/img/mole.png", cv2.IMREAD_UNCHANGED)
imgMole = cv2.resize(imgMole, (135, 100))

img_list = []
for _, file_name in enumerate(os.listdir("./game2/img/img_gif_butterfly/")):
    temp = cv2.imread("./game2/img/img_gif_butterfly/" + file_name, cv2.IMREAD_UNCHANGED)
    temp = cv2.resize(temp, (90, 80))
    img_list.append(temp)

# init

# data


###############################################################################################
# exe

time_web = 15
stage_web = 1
score_web = 0
question_web = ''
quit = 0
x_coor_web = 0
y_coor_web = 0

def game2_frames():
    global time_web
    global stage_web
    global score_web
    global question_web
    global quit
    global x_coor_web
    global y_coor_web

    quit = 0
    x_coor = 0
    y_coor = 0

    cap = cv2.VideoCapture(0)
    segmentor = SelfiSegmentation()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    # mp_drawing = mp.solutions.drawing_utils  # .draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    gesture_sensitivity = 0.05
    click_sensitivity = 20
    time_limit = 15

    frame_count = 0
    time_clock = 0
    latency = 1  # 지연시간(ms)
    fps = 1000/latency  # float
    fps_real = fps/64  # 실제 fps는 while문 연산속도에 달려있음, 보정값으로 나눠줘야 함, 보정값과 time_clock은 비례
    stage = 1
    score = 0
    loop = 0
    x_fist = 1000  # 주먹 손 중앙(망치) 위치 init -> 화면 밖
    y_fist = 1000

    offset_list = [-30, -20, -10, 0, 10, 20, 30]
    location = [(120, 300), (250, 100), (400, 100), (520, 300)]
    random.shuffle(location)
    new_location = [(x,y) for (x,y) in location]

    quiz_data = [
        'ㅇ(이응) 받침인',
        'ㅁ(미음) 받침인',
        'ㅅ(시옷) 받침인'
    ]
    right_answer = [
        ['공주', '오징어', '성', '풍선', '엉덩이', '강', '방', '항아리'],
        ['봄바람', '구름', '감기', '밤', '점수', '곰', '힘', '염소'],
        ['비옷', '촛불', '칫솔', '깃털', '맛', '못']
    ]
    wrong_answer = [
        ['국수', '수박', '입술', '짚신', '무릎',
        '봄바람', '구름', '감기', '밤', '점수', '곰', '힘', '염소',
        '비옷', '촛불', '칫솔', '깃털', '맛', '못'],
        ['국수', '수박', '입술', '짚신', '무릎',
        '공주', '오징어', '성', '풍선', '엉덩이', '강', '방', '항아리',
        '비옷', '촛불', '칫솔', '깃털', '맛', '못'],
        ['국수', '수박', '입술', '짚신', '무릎',
        '공주', '오징어', '성', '풍선', '엉덩이', '강', '방', '항아리',
        '봄바람', '구름', '감기', '밤', '점수', '곰', '힘', '염소']
    ]
    right_answer_list = right_answer[stage-1]
    wrong_answer_list = wrong_answer[stage-1]

    temp_list_right = right_answer_list
    temp_list_wrong = wrong_answer_list

    right_answer_stage = []
    wrong_answer_stage = []

    right_answer_stage.append(random.choice(right_answer_list))
    wrong_answer_stage.append(random.choice(wrong_answer_list))
    # 중복된 보기 제거
    temp_list_right.remove(right_answer_stage[0])
    temp_list_wrong.remove(wrong_answer_stage[0])

    right_answer_stage.append(random.choice(temp_list_right))
    wrong_answer_stage.append(random.choice(temp_list_wrong))

    while cap.isOpened():
        
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        result = hands.process(img)  # 배경 지우기 등 화면효과 적용 전 화면 기준으로 손을 인식하기

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Check if the detected hand is in 'rock' gesture
                if is_rock_gesture(hand_landmarks, gesture_sensitivity, mp_hands):

                    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                    x_fist = int(middle_pip.x * 640)
                    y_fist = int(middle_pip.y * 480)

                    img = cvzone.overlayPNG(img, imgHammer, pos=[x_fist-75, y_fist-75])
                    # 주먹 중앙과 두더지 위치(new_location) x,y 좌표값 차이가 각각 click_sensitivity 미만일 때
                    if abs(x_fist - new_location[0][0]) < click_sensitivity and abs(y_fist - new_location[0][1]) < click_sensitivity:
                        x_coor = new_location[0][0]
                        y_coor = new_location[0][1]
                        score += 1  # 정답(new_loc 0,1) 일 때만 득점 / 감점요인 x
                        save_game_data(x_coor,y_coor,score,stage)
                        new_location[0] = (1000, 1000)

                    if abs(x_fist - new_location[1][0]) < click_sensitivity and abs(y_fist - new_location[1][1]) < click_sensitivity:
                        x_coor = new_location[1][0]
                        y_coor = new_location[1][1]
                        score += 1
                        save_game_data(x_coor,y_coor,score,stage)
                        new_location[1] = (1000, 1000)

                    if abs(x_fist - new_location[2][0]) < click_sensitivity and abs(y_fist - new_location[2][1]) < click_sensitivity:
                        new_location[2] = (1000, 1000)

                    if abs(x_fist - new_location[3][0]) < click_sensitivity and abs(y_fist - new_location[3][1]) < click_sensitivity:
                        new_location[3] = (1000, 1000)

        imgOut = segmentor.removeBG(img, imgBg, cutThreshold=.1)  # 손 먼저 인식하고 배경제거

        # loop = loop % 20  # for animated gif
        frame_count += 1  # for time in a game
        time_clock = time_limit - int(frame_count / int(fps_real))

        imgOverlay = cvzone.overlayPNG(imgOut, img_list[loop % 20], pos=[x_fist, y_fist - 200])  # 망치 손 위에 나비 띄우기

        for i, loc in enumerate(new_location):  # 정/오답 text 그리기
            imgOverlay = cvzone.overlayPNG(imgOverlay, imgMole, pos=[loc[0]-60, loc[1]-50])
            img_pil = Image.fromarray(imgOverlay)
            draw = ImageDraw.Draw(img_pil)

            if i < 2:  # 정답(new_loc 0,1) 2개(문제 보기 총 4개 중) text
                draw.text((loc[0]-25, loc[1]), right_answer_stage[i], font=font, fill=(0, 0, 255, 0))
            else:  # 오답 보기 text
                draw.text((loc[0]-25, loc[1]), wrong_answer_stage[i-2], font=font, fill=(0, 0, 255, 0))
            imgOverlay= np.array(img_pil)

        # text1 = "time = " + str(time_clock)
        # text2 = "stage = " + str(stage)
        # text3 = "score = " + str(score)
        # cv2.putText(imgOverlay, text1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        # cv2.putText(imgOverlay, text2, (230, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        # cv2.putText(imgOverlay, text3, (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        text4 = quiz_data[stage-1]
        # cv2.putText(imgOverlay, text4, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        time_web = time_clock
        stage_web = stage
        score_web = score
        question_web = text4
        x_coor_web = x_coor
        y_coor_web = y_coor

        ###############################################################################################
        # cv2.imshow("game2", imgOverlay)  # 화면 출력
        _, buffer = cv2.imencode('.jpg', imgOverlay)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cv2.waitKey(latency)  # 값이 커지면 전체 while문 도는 속도(프레임)를 늦춘다.

        loop += 1

        # stage(1~3) 진행 로직
        if time_clock <= 0:
            if stage >= 3:
                #################################### to survey
                cv2.waitKey(10)
                print("to survey")
                cv2.waitKey(2000)
                hands.close()  # 손 인식 & 캠 종료(이하 3줄)
                cap.release()
                cv2.destroyAllWindows()
                quit = 1
            else:  # 다음 문제 & 초기화
                frame_count = 0
                stage += 1

                right_answer_list = right_answer[stage-1]
                wrong_answer_list = wrong_answer[stage-1]

                temp_list_right = right_answer_list
                temp_list_wrong = wrong_answer_list

                right_answer_stage = []
                wrong_answer_stage = []

                right_answer_stage.append(random.choice(right_answer_list))
                wrong_answer_stage.append(random.choice(wrong_answer_list))

                temp_list_right.remove(right_answer_stage[0])
                temp_list_wrong.remove(wrong_answer_stage[0])

                right_answer_stage.append(random.choice(right_answer_list))
                wrong_answer_stage.append(random.choice(wrong_answer_list))

                random.shuffle(location)
                new_location = [(x + random.choice(offset_list),
                                 y + random.choice(offset_list)) for (x, y) in location]
            
        elif new_location[0] == (1000, 1000) and new_location[1] == (1000, 1000):  # 두 정답(new_loc 1,2)을 모두 맞췄으면
            if stage >= 3:
                #################################### to survey
                cv2.waitKey(10)
                print("to survey")
                cv2.waitKey(2000)
                hands.close()  # 손 인식 & 캠 종료(이하 3줄)
                cap.release()
                cv2.destroyAllWindows()
                quit = 1
            else:  # 다음 문제 & 초기화
                frame_count = 0
                stage += 1
                
                right_answer_list = right_answer[stage-1]
                wrong_answer_list = wrong_answer[stage-1]

                temp_list_right = right_answer_list
                temp_list_wrong = wrong_answer_list

                right_answer_stage = []
                wrong_answer_stage = []

                right_answer_stage.append(random.choice(right_answer_list))
                wrong_answer_stage.append(random.choice(wrong_answer_list))

                temp_list_right.remove(right_answer_stage[0])
                temp_list_wrong.remove(wrong_answer_stage[0])

                right_answer_stage.append(random.choice(right_answer_list))
                wrong_answer_stage.append(random.choice(wrong_answer_list))

                random.shuffle(location)
                new_location = [(x + random.choice(offset_list),
                                 y + random.choice(offset_list)) for (x, y) in location]
                
        # elif 정답이 하나라도 남고, 두 오답(new_loc 2,3)을 모두 골랐으면 -> 시간 끝날 때 까지 아무일 x

        if cv2.waitKey(latency) & 0xFF == 27:  # ESC key to exit  # & 0xFF
            break


    hands.close()
    cap.release()
    cv2.destroyAllWindows()


def get_data_2():
    return time_web, stage_web, score_web, question_web, quit