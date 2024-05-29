from flask import Flask, request, redirect, render_template, url_for, jsonify, Response, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import datetime
import cv2
import mediapipe as mp
import os
import numpy as np
from classgo import Moving
from recognition_lib import util
from recognition_part import recognition
from tensorflow.keras.models import load_model

app = Flask(__name__)
lock = threading.Lock()

# TensorFlow warning 제거
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

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

heart_1 = cv2.VideoCapture('outpart_lib/heart_1.gif')
heart_2 = cv2.VideoCapture('outpart_lib/heart_1.gif')
heart_3 = cv2.VideoCapture('outpart_lib/heart_1.gif')

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

def generate_frames():
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

                    if detect_label:
                        for i in range(len(detect_label)):
                            label, position = detect_label[i]
                            x_c = int(position[0] * nw)
                            y_c = int(position[1] * nh)

                            # 분류 결과에 따른 로그 생성
                            app.logger.info(f"분류 결과 - id: {current_page_id}, label: {label}, position: {position}, time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", extra={'id': current_page_id, 'label': label, 'coordinate': position})

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
            
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Float)
    x_coordinate = db.Column(db.Float)
    y_coordinate = db.Column(db.Float)
    score = db.Column(db.Integer)
    stage = db.Column(db.Integer)
    time = db.Column(db.String(50), primary_key=True)
    message = db.Column(db.Text)
    func = db.Column(db.String(255))
    toggle = db.Column(db.Float)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        # coordinate를 가져옴
        coordinate = getattr(record, 'coordinate', None)
        
        # coordinate가 존재하고 리스트인 경우에만 분리
        if coordinate and isinstance(coordinate, list) and len(coordinate) == 2:
            x, y = coordinate
        else:
            # coordinate가 없거나 리스트가 아니거나 길이가 2가 아닌 경우에는 None으로 설정
            x = y = None

        log_record = {
            'id': getattr(record, 'id', None),
            'label': getattr(record, 'label', None),
            'x_coordinate': x,  # x 좌표
            'y_coordinate': y,  # y 좌표
            'score': getattr(record, 'score', None),
            'stage': getattr(record, 'stage', None),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': record.getMessage(),
            'func': record.funcName,
            'toggle': getattr(record, 'toggle', None)
        }
        return json.dumps(log_record)
    
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        with app.app_context():
            try:
                # request_info = {
                #     'method': request.method if request else None,
                #     'url': request.url if request else None,
                #     'remote_addr': request.remote_addr if request else None
                # }
                log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                coordinate = getattr(record, 'coordinate', None)
                # coordinate가 존재하고 리스트인 경우에만 분리
                if coordinate and isinstance(coordinate, list) and len(coordinate) == 2:
                    x, y = coordinate
                else:
                    # coordinate가 없거나 리스트가 아니거나 길이가 2가 아닌 경우에는 None으로 설정
                    x = y = None
                log = Log(
                    label=record.label if hasattr(record, 'label') else None,
                    x_coordinate=x,
                    y_coordinate=y,                    
                    score=record.score if hasattr(record, 'score') else None,
                    stage=record.stage if hasattr(record, 'stage') else None,
                    time=log_time,
                    message=record.getMessage(),
                    func=record.funcName,
                    toggle=toggle,
                    id = getattr(record, 'id', None)
                )
                db.session.add(log)
                db.session.commit()
                # 분류 결과를 데이터베이스에 저장한 후에도 로그로 남깁니다.
                # self.log_classification_result(record.id, record.label, record.coordinate)
            except Exception as e:
                print("An error occurred while saving log to database:", e)
                # 데이터베이스에 로그를 저장하는 동안 오류가 발생하면 파일에도 로그를 기록합니다.
                # self.handleError(record)

# def log_classification_result(self, id, label, coordinate):
#         # 분류 결과를 로그로 남깁니다.
#         log_msg = f"분류 결과 - id: {id}, label: {label}, coordinate: {coordinate}, time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#         app.logger.info(log_msg, extra={'id': id, 'label': label, 'coordinate': coordinate})

def setup_logger():
    file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    db_handler = SQLAlchemyHandler()
    db_handler.setLevel(logging.INFO)
    db_formatter = JSONFormatter()
    db_handler.setFormatter(db_formatter)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(db_handler)
    app.logger.setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').addHandler(file_handler)
    logging.getLogger('sqlalchemy').addHandler(db_handler)
setup_logger()

@app.after_request
def after_request(response):
    if response.content_type == 'application/json':
        with open('log.json', 'r') as file:
            log_data = [json.loads(line) for line in file]
        response_data = response.get_json()
        if isinstance(response_data, dict):
            response_data['logs'] = log_data
        else:
            response_data = {'data': response_data, 'logs': log_data}
        response.set_data(json.dumps(response_data))
    return response

# 글로벌 변수로 설정
toggle = 0
current_page_id = 1000
game_data = {
    '그림자 놀이터': {
        'title': '그림자 놀이터',
        'image': 'game1.png',
        'description': '손으로 동물과 모양을 만들어 보세요!',
        'id': 1
    },
    '두더지 잡기': {
        'title': '두더지 잡기',
        'image': 'game1.png',
        'description': '주어진 단어와 같은 단어를 가지고 있는 두더지를 잡아보세요!',
        'id': 2
    },
    '산성비': {
        'title': '산성비',
        'image': 'game1.png',
        'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.',
        'id': 3
    }
}

@app.route('/')
def index():
    global current_page_id
    current_page_id = 0
    # g.page_id = page_id
    app.logger.info(f"game {current_page_id}", extra={'id':current_page_id})
    # return 'random : <strong>'+str(random.random())+'</strong>'
    return render_template('index.html')

@app.route('/game/<game_name>')
def game(game_name):
    global current_page_id
    global game_data
    if game_name in game_data:
        current_page_id = game_data[game_name]['id']
        # g.page_id = page_id
        app.logger.info(f"page {current_page_id}", extra={'id':current_page_id})
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404

@app.route('/game_play/<game_name>')
def game_play(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game_video.html', game=game_data[game_name])
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

def log_status():
    if lock.acquire(blocking=False):
        try:
            with app.app_context():
                page_id = getattr(g, 'page_id', 1000)
                # 페이지 ID의 두 번째 자리 추출
                page_id_second_digit = (page_id % 1000) // 10
                # 로그를 저장할 때 페이지 ID의 두 번째 자리를 증가시킴
                page_id_second_digit += 1
                # 두 번째 자리를 0부터 다시 시작하도록 설정
                if page_id_second_digit > 10:
                    page_id_second_digit = 1
                # 수정된 페이지 ID로 재구성
                # new_page_id = (page_id // 1000) * 1000 + page_id_second_digit * 10
                # g 객체에 새로운 페이지 ID 설정
                # g.page_id = new_page_id
                app.logger.info(f"5초마다 업데이트 - log {current_page_id}", extra={'id': current_page_id})

                # page_id = getattr(g, 'page_id', 1000)
                # app.logger.info("5초마다 업데이트", extra={'id': page_id})
        finally:
            lock.release()

scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()

if __name__ == '__main__':
    app.run()

# if __name__ == '__main__':
#     app.run(debug=True)