from flask import Flask, request, redirect, render_template, url_for, jsonify, Response, session
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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from login import app, db
# import g
app = Flask(__name__)
lock = threading.Lock()
# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pch:1001@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from login import db

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
@app.route('/random_login', methods=['POST'])
def random_login():
    username = str(uuid.uuid4())
    password = 'password'
    new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    app.logger.info(f'Random user created: {username}')
    return jsonify({'message': 'Random user created','username':username, 'user_id': new_user.id})

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    coordinate = db.Column(db.Float)
    score = db.Column(db.Integer)
    stage = db.Column(db.Integer)
    time = db.Column(db.String(50))
    message = db.Column(db.Text)
    func = db.Column(db.String(255))
    toggle = db.Column(db.Float)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'id': getattr(record, 'id', None),
            'label': getattr(record, 'label', None),
            'coordinate': getattr(record, 'coordinate', None),
            'score': getattr(record, 'score', None),
            'stage': getattr(record, 'stage', None),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': record.getMessage(),
            'func': record.funcName,
            'toggle': getattr(record, 'toggle', None)
        }
        return json.dumps(log_record)
    
from flask import current_app
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        with current_app.app_context():
            try:
                # request_info = {
                #     'method': request.method if request else None,
                #     'url': request.url if request else None,
                #     'remote_addr': request.remote_addr if request else None
                # }
                log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log = Log(
                    label=record.label if hasattr(record, 'label') else None,
                    coordinate=record.coordinate if hasattr(record, 'coordinate') else None,
                    score=record.score if hasattr(record, 'score') else None,
                    stage=record.stage if hasattr(record, 'stage') else None,
                    time=log_time,
                    message=record.getMessage(),
                    func=record.funcName,
                    toggle=toggle,
                    id=getattr(record, 'id', None)
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                print("An error occurred while saving log to database:", e)
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
    # if response.content_type == 'application/json':
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

def generate_frames():
    global toggle
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # 프레임을 좌우 반전
            frame = cv2.flip(frame, 1)
            # 손 랜드마크 추적
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(image)
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    toggle = 1
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# toggle = 0
# def generate_frames():
#     global toggle
#     cap = cv2.VideoCapture(0)
#     if cap.isOpened():
#         app.logger.info(f'width:{cap.get(3)}, height :{cap.get(4)}')  # 화면크기 1280x720를 프린트 -> DB에 저장해보세요
#                                                                         # cap.get(3) = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
#         # if success:
#         frame = cv2.flip(frame, 1)
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#         app.logger.info(f'toggle value: {toggle}')
@app.route('/')
def index():
    global current_page_id #전역 변수 선언
    current_page_id  = 1001 # 전역 변수 업데이트
    # g.page_id = page_id
    app.logger.info(f"page {current_page_id }", extra={'id':current_page_id })
    # return 'random : <strong>'+str(random.random())+'</strong>'
    return render_template('index.html')

@app.route('/game/<game_name>')
def game(game_name):
    global current_page_id #전역 변수 선언
    game_data = {
        '그림자 놀이터': {
            'title': '그림자 놀이터',
            'image': 'game1.png',
            'description': '손으로 동물과 모양을 만들어 보세요!',
            'id':1001
        },
        '두더지 잡기': {
            'title': '두더지 잡기',
            'image': 'game1.png',
            'description': '주어진 단어와 같은 단어를 가지고 있는 두더지를 잡아보세요!',
            'id':2001
        },
        '산성비': {
            'title': '산성비',
            'image': 'game1.png',
            'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.',
            'id':3001
        }
    }
    if game_name in game_data:
        current_page_id  = game_data[game_name]['id'] #원래 page_id
        # g.page_id = page_id
        app.logger.info(f"page {current_page_id }", extra={'id':current_page_id })
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404
    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return jsonify({'message' : 'Login successful', 'user_id' : user.id}), 200
        else:
            return jsonify({'message' : 'Invalid credentials'}), 401
    except SQLAlchemyError as e:
        return jsonify({'message' : 'An error occured', 'error' : str(e)}), 500
    
@app.route('/log', methods=['post'])
def log_data():
    data = request.get_json()
    label = data.get('label')
    coordinate = data.get('coordinate')
    score = data.get('score')
    stage = data.get('stage')
    time = data.get('time')
    message = data.get('message')
    func = data.get('func')
    toggle = data.get('toggle')

    user_id = session.get('user_id')
    if user_id:
        log = Log(
            label=label,
            coordinate=coordinate,
            score=score,
            stage=stage,
            time=time,
            message=message,
            func=func,
            toggle=toggle,
            user_id=user_id
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'message':'Log created successfully'}), 201
    else:
        return jsonify({'message' : 'User not logged in'}), 401
    
def log_status():
    if lock.acquire(blocking=False):
        try:
            with app.app_context():
                page_id = getattr('page_id', 1000)
                app.logger.info("5초마다 업데이트", extra={'id': current_page_id}) # 원래 page_id임
        finally:
            lock.release()
scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()
if __name__ == '__main__':
    # db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()
# if __name__ == '__main__':
#     app.run(debug=True)