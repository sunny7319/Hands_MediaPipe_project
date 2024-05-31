from flask import Flask, g, session, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json, os
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import datetime

app = Flask(__name__)
lock = threading.Lock()

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class client_info(db.Model):
    __tablename__ = 'client_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    log = db.relationship('Log', backref='client_info', lazy=True)
            
class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, db.ForeignKey('client_info.id'), nullable=False, primary_key=True)
    page = db.Column(db.Integer)
    label = db.Column(db.Float)
    x_coordinate = db.Column(db.Float)
    y_coordinate = db.Column(db.Float)
    score = db.Column(db.Integer)
    stage = db.Column(db.Integer)
    time = db.Column(db.String(50), primary_key=True)
    message = db.Column(db.Text)
    func = db.Column(db.String(255))
    toggle = db.Column(db.Float)
    evaluation = db.Column(db.Float)

def load_user_data(file_path='users.json'):
    # 파일에서 사용자 정보를 읽어옵니다.
    with open(file_path, 'r') as file:
        client = json.load(file)
    # 읽어온 사용자 정보를 데이터베이스에 저장합니다.
    with app.app_context():
        for clients in client:
        # 사용자 정보에서 사용자 이름을 가져옵니다.
            username = clients.get('username')
            user_id = clients.get('id')
         # 이미 데이터베이스에 존재하는 사용자인지 확인합니다.
            existing_user = client_info.query.filter_by(username=username).first()
        # # 데이터베이스에 존재하지 않는 경우에만 추가합니다.
            if not existing_user:
            # 새로운 사용자 정보를 데이터베이스에 추가합니다.
                new_user = client_info(id=user_id, username=username)
                db.session.add(new_user)
                # 변경사항을 저장합니다.
        db.session.commit()
# load_user_data 함수를 호출하여 데이터를 로드하고 데이터베이스에 저장합니다.
load_user_data()

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

        # # 사용자 이름 가져오기 (예: record.username)
        # username = getattr(record, 'username', None)
        # # 사용자 이름으로 데이터베이스에서 사용자 ID 가져오기
        # user_id = None
        # if username:
        #     # 사용자 정보를 users.json에서 가져옴
        #     users = load_user_data()
        #     # 사용자 이름에 해당하는 ID를 찾음
        #     for user in users:
        #         if user['username'] == username:
        #             user_id = user['id']
        #             break

        
        log_record = {
            'id':'01', 
            'page': getattr(record, 'page', None),
            'label': getattr(record, 'label', None),
            'x_coordinate': x,  # x 좌표
            'y_coordinate': y,  # y 좌표
            'score': getattr(record, 'score', None),
            'stage': getattr(record, 'stage', None),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': record.getMessage(),
            'func': record.funcName,
            'toggle': getattr(record, 'toggle', None),
            'evaluation': getattr(record, 'evaluation', None)
        }
        return json.dumps(log_record)

    
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        with app.app_context():
            try:
                log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                coordinate = getattr(record, 'coordinate', None)
                # coordinate가 존재하고 리스트인 경우에만 분리
                if coordinate and isinstance(coordinate, list) and len(coordinate) == 2:
                    x, y = coordinate
                else:
                    # coordinate가 없거나 리스트가 아니거나 길이가 2가 아닌 경우에는 None으로 설정
                    x = y = None

                # # 사용자 이름 가져오기 (예: record.username)
                # username = getattr(record, 'username', None)
                # # 사용자 이름으로 데이터베이스에서 사용자 ID 가져오기
                # user_id = None
                # if username:
                #     # 사용자 정보를 users.json에서 가져옴
                #     users = load_user_data()
                #     # 사용자 이름에 해당하는 ID를 찾음
                #     for user in users:
                #         if user['username'] == username:
                #             user_id = user['id']
                #             break

                log = Log(
                    id='01',
                    label=record.label if hasattr(record, 'label') else None,
                    x_coordinate=x,
                    y_coordinate=y,                    
                    score=record.score if hasattr(record, 'score') else None,
                    stage=record.stage if hasattr(record, 'stage') else None,
                    time=log_time,
                    message=record.getMessage(),
                    func=record.funcName,
                    # toggle=toggle,
                    page = getattr(record, 'page', None),
                    evaluation = getattr(record, 'evaluation', None)
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                print("An error occurred while saving log to database:", e)
                # 데이터베이스에 로그를 저장하는 동안 오류가 발생하면 파일에도 로그를 기록합니다.
                # self.handleError(record)

def setup_logger():
    file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    db_handler = SQLAlchemyHandler()
    db_handler.setLevel(logging.INFO)
    db_formatter = JSONFormatter()
    # db_formatter = logging.Formatter('%(message)s')
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


def log_status():
    if lock.acquire(blocking=False):
        try:
            with app.app_context():
                page_id = getattr(g, 'page_id', 999)
                # 페이지 ID의 두 번째 자리 추출
                # page_id_second_digit = (page_id % 1000) // 100
                # # 로그를 저장할 때 페이지 ID의 두 번째 자리를 증가시킴
                # page_id_second_digit += 1
                # # 두 번째 자리를 0부터 다시 시작하도록 설정
                # if page_id_second_digit > 10:
                #     page_id_second_digit = 1
                # 수정된 페이지 ID로 재구성
                # new_page_id = (page_id // 1000) * 1000 + page_id_second_digit * 10
                # g 객체에 새로운 페이지 ID 설정
                # g.page_id = new_page_id
                app.logger.info(f"5초마다 업데이트 - log {page_id}", extra={'page': page_id})

                # page_id = getattr(g, 'page_id', 1000)
                # app.logger.info("5초마다 업데이트", extra={'id': page_id})
        finally:
            lock.release()

scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()