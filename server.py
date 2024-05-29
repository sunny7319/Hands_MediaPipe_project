from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import os
from classgo import Moving
from recognition_lib import util
from recognition_part import recognition
from tensorflow.keras.models import load_model

app = Flask(__name__)

# TensorFlow warning 제거
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 모델 로드 및 컴파일
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

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
def generate_frames():
    global score
    with mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5) as hands:
        counting = 1
        dict_hand = util.make_dict_hand()
        flag = []
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
                            print(f"label: {label}, position: {position}")  # position 구조 확인

                            # 예: position이 [[x, y]] 형태라면
                            if isinstance(position[0], list):
                                x_c = int(position[0][0] * nw)
                                y_c = int(position[0][1] * nh)
                            else:
                                x_c = int(position[0] * nw)
                                y_c = int(position[1] * nh)

                            if label == 0:
                                rndN = np.random.randint(1, 4)
                                nabi = [nabi_1, nabi_2, nabi_3][rndN - 1]
                                if x_c + 100 > nw or y_c + 100 > nh:
                                    x_c, y_c = nw - 100, nh - 100
                                flag.append(Moving(nabi, x_c, y_c, 100, 100, 1))

                            elif label == 1:
                                rndN = np.random.randint(1, 4)
                                cat = [cat_1, cat_2, cat_3][rndN - 1]
                                if x_c + 200 > nw or y_c + 200 > nh:
                                    x_c, y_c = nw - 200, nh - 200
                                flag.append(Moving(cat, x_c, y_c, 200, 200, 1))

                            elif label == 2:
                                rndN = np.random.randint(1, 4)
                                snail = [snail_1, snail_2, snail_3][rndN - 1]
                                if x_c + 70 > nw or y_c + 70 > nh:
                                    x_c, y_c = nw - 70, nh - 70
                                flag.append(Moving(snail, x_c, y_c, 70, 70, 1))

                            elif label == 3:
                                rndN = np.random.randint(1, 4)
                                deer = [deer_1, deer_2, deer_3][rndN - 1]
                                if x_c + 300 > nw or y_c + 300 > nh:
                                    x_c, y_c = nw - 300, nh - 300
                                flag.append(Moving(deer, x_c, y_c, 300, 300, 1))

                            elif label == 4:
                                rndN = np.random.randint(1, 4)
                                heart = [heart_1, heart_2, heart_3][rndN - 1]
                                if x_c + 100 > nw or y_c + 100 > nh:
                                    x_c, y_c = nw - 100, nh - 100
                                flag.append(Moving(heart, x_c, y_c, 100, 100, 0))

                            elif label == 5:
                                rndN = np.random.randint(1, 4)
                                duck = [duck_1, duck_2, duck_3][rndN - 1]
                                if x_c + 150 > nw or y_c + 150 > nh:
                                    x_c, y_c = nw - 150, nh - 150
                                flag.append(Moving(duck, x_c, y_c, 150, 150, 1))

                            elif label == 6:
                                rndN = np.random.randint(1, 4)
                                sun = [sun_1, sun_2, sun_3][rndN - 1]
                                if x_c + 180 > nw or y_c + 180 > nh:
                                    x_c, y_c = nw - 180, nh - 180
                                flag.append(Moving(sun, x_c, y_c, 180, 180, 0))

                            elif label == 7:
                                rndN = np.random.randint(1, 4)
                                house = [house_1, house_2, house_3][rndN - 1]
                                if x_c + 400 > nw or y_c + 400 > nh:
                                    x_c, y_c = nw - 400, nh - 400
                                flag.append(Moving(house, x_c, y_c, 400, 400, 0))

                            elif label == 8:
                                rndN = np.random.randint(1, 4)
                                tree = [tree_1, tree_2, tree_3][rndN - 1]
                                if x_c + 350 > nw or y_c + 350 > nh:
                                    x_c, y_c = nw - 350, nh - 350
                                flag.append(Moving(tree, x_c, y_c, 350, 350, 0))

                            elif label == 9:
                                rndN = np.random.randint(1, 4)
                                rock = [rock_1, rock_2, rock_3][rndN - 1]
                                if x_c + 120 > nw or y_c + 120 > nh:
                                    x_c, y_c = nw - 120, nh - 120
                                flag.append(Moving(rock, x_c, y_c, 120, 120, 0))

                            elif label == 10:
                                rndN = np.random.randint(1, 4)
                                flower = [flower_1, flower_2, flower_3][rndN - 1]
                                if x_c + 70 > nw or y_c + 70 > nh:
                                    x_c, y_c = nw - 70, nh - 70
                                flag.append(Moving(flower, x_c, y_c, 70, 70, 0))

                            elif label == 11:
                                rndN = np.random.randint(1, 4)
                                dog = [dog_1, dog_2, dog_3][rndN - 1]
                                if x_c + 100 > nw or y_c + 100 > nh:
                                    x_c, y_c = nw - 100, nh - 100
                                flag.append(Moving(dog, x_c, y_c, 100, 100, 1))

            counting += 1
            score += 1

            for obj in flag:
                frame = obj.gif.read()[1]
                if frame is not None and frame.size != 0:
                    obj.frame = cv2.resize(frame, (obj.resize_x, obj.resize_y))
                    if obj.way == 1:
                        obj.frame = cv2.flip(obj.frame, 1)
                    image[obj.rp[obj.c][1]:obj.rp[obj.c][1] + obj.frame.shape[0],
                        obj.rp[obj.c][0]:obj.rp[obj.c][0] + obj.frame.shape[1]] = obj.frame
                reset_gif(obj.gif)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# 글로벌 변수로 설정
toggle = 0

game_data = {
    '그림자 놀이터': {
        'title': '그림자 놀이터',
        'image': 'game1.png',
        'description': '손으로 동물과 모양을 만들어 보세요!'
    },
    '두더지 잡기': {
        'title': '두더지 잡기',
        'image': 'game1.png',
        'description': '주어진 단어와 같은 단어를 가지고 있는 두더지를 잡아보세요!'
    },
    '산성비': {
        'title': '산성비',
        'image': 'game1.png',
        'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_name>')
def game(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404
    
@app.route('/game_play/<game_name>')
def game_play(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game_video.html', game=game_data[game_name], score=score)
    else:
        return "Game not found", 404

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# toggle 값을 반환하는 엔드포인트 추가
@app.route('/toggle_status')
def toggle_status():
    global toggle
    return jsonify({'toggle': toggle})

if __name__ == '__main__':
    app.run(debug=True)