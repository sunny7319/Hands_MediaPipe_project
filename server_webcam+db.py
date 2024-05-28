from flask import Flask, request, redirect, render_template, url_for, jsonify, Response
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

app = Flask(__name__)
lock = threading.Lock()

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    coordinate = db.Column(db.Float)
    score = db.Column(db.Integer)
    stage = db.Column(db.Integer)
    time = db.Column(db.String(50))
    level = db.Column(db.String(50))
    message = db.Column(db.Text)
    path = db.Column(db.String(255))
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
            'level': record.levelname,
            'message': record.getMessage(),
            'path': record.pathname,
            'func': record.funcName,
            'toggle': getattr(record, 'toggle', None)
        }
        return json.dumps(log_record)
    
from flask import current_app
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        with current_app.app_context():
            try:
                request_info = {
                    'method': request.method if request else None,
                    'url': request.url if request else None,
                    'remote_addr': request.remote_addr if request else None
                }
                log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log = Log(
                    label=record.label if hasattr(record, 'label') else None,
                    coordinate=record.coordinate if hasattr(record, 'coordinate') else None,
                    score=record.score if hasattr(record, 'score') else None,
                    stage=record.stage if hasattr(record, 'stage') else None,
                    time=log_time,
                    level=record.levelname,
                    message=record.getMessage(),
                    path=record.pathname,
                    func=record.funcName,
                    toggle=toggle
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
toggle = 0
def generate_frames():
    global toggle
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        app.logger.info(f'width:{cap.get(3)}, height :{cap.get(4)}')  # 화면크기 1280x720를 프린트 -> DB에 저장해보세요
                                                                        # cap.get(3) = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    while True:
        success, frame = cap.read()
        if not success:
            break
        # if success:
        frame = cv2.flip(frame, 1)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        app.logger.info(f'toggle value: {toggle}')

@app.route('/')
def index():
    # return 'random : <strong>'+str(random.random())+'</strong>'
    return render_template('index.html')
@app.route('/game/<game_name>')
def game(game_name):
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
    if game_name in game_data:
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
def log_status():
    if lock.acquire(blocking=False):
        try:
            with app.app_context():
                app.logger.info("5초마다 업데이트")
        finally:
            lock.release()
scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()
if __name__ == '__main__':
    app.run()
# if __name__ == '__main__':
#     app.run(debug=True)