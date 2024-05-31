from flask import Flask, g, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import datetime
import random

app = Flask(__name__)
lock = threading.Lock()

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class client_info(db.Model):
    __tablename__ = 'client_info'
    client_id = db.Column(db.Integer, primary_key=True)
    log = db.relationship('Log', backref='client_info', lazy=True)
            
class Log(db.Model):
    __tablename__ = 'log'
    client_id = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False)
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

def add_initial_client():
    with app.app_context():
        if not client_info.query.get('01'):
            client = client_info(client_id='01')
            db.session.add(client)
            db.session.commit()
add_initial_client()

def generate_client_id():
        return session.get('client_id', '01')

@app.before_request
def before_request():
    # 세션에 'userid'가 없는 경우에만 'userid'를 생성합니다.
    if 'client_id' not in session:
        session['client_id'] = generate_client_id()


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
            'client_id':'01', 
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
    # log_classification_result 메서드를 호출하여 분류 결과를 로그로 남깁니다.
        # self.log_classification_result(log_record['id'], log_record['label'], coordinate)
        
        return json.dumps(log_record)

    # def log_classification_result(self, id, label, coordinate):
    #     # 분류 결과를 로그로 남깁니다.
    #     log_msg = f"분류 결과 - id: {id}, label: {label}, coordinate: {coordinate}, time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    #     app.logger.info(log_msg, extra={'id': id, 'label': label, 'coordinate': coordinate})
    
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
                client_id = getattr(record, 'client_id', '01')  # record에서 client_id 가져오기
                log = Log(
                    client_id=client_id,
                    label=record.label if hasattr(record, 'label') else None,
                    x_coordinate=x,
                    y_coordinate=y,                    
                    score=record.score if hasattr(record, 'score') else None,
                    stage=record.stage if hasattr(record, 'stage') else None,
                    time=log_time,
                    message=record.getMessage(),
                    func=record.funcName,
                    # toggle=toggle,
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
                client_id=g.get('client_id', '01')
                if not client_info.query.filter_by(client_id=client_id).first():
                    client = client_info(client_id=client_id)
                    db.seesion.add(client)
                    db.session.commit()
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
                app.logger.info(f"5초마다 업데이트 - log {client_id}", extra={'id': client_id})

                # page_id = getattr(g, 'page_id', 1000)
                # app.logger.info("5초마다 업데이트", extra={'id': page_id})
        finally:
            lock.release()

scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()

# if __name__ == '__main__':
#     app.run()

# if __name__ == '__main__':
#     app.run(debug=True)