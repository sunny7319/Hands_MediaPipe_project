from flask import Flask, g, session, request, jsonify
# from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json, os, threading, datetime
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)
lock = threading.Lock()
# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

class client_info(db.Model):
    __tablename__ = 'client_info'
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(50), unique=True)
    game1 = db.relationship('Game1', backref='client', lazy=True)
    game2 = db.relationship('Game2', backref='client', lazy=True)
    game3 = db.relationship('Game3', backref='client', lazy=True)

class Game1(db.Model):
    __tablename__ = 'game1'
    id_1 = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False, primary_key=True)
    page_1 = db.Column(db.Integer)
    label_1 = db.Column(db.Float)
    x_coordinate_1 = db.Column(db.Float)
    y_coordinate_1 = db.Column(db.Float)
    score_1 = db.Column(db.Integer)
    time_1 = db.Column(db.DateTime, primary_key=True)
    evaluation_1 = db.Column(db.Float)

class Game2(db.Model):
    __tablename__ = 'game2'
    id_2 = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False, primary_key=True)
    page_2 = db.Column(db.Integer)
    label_2 = db.Column(db.Float)
    x_coordinate_2 = db.Column(db.Float)
    y_coordinate_2 = db.Column(db.Float)
    score_2 = db.Column(db.Integer)
    stage_2 = db.Column(db.Integer)
    time_2 = db.Column(db.String(50), primary_key=True)
    evaluation_2 = db.Column(db.Float)
class Game3(db.Model):
    __tablename__ = 'game3'
    id_3 = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False, primary_key=True)
    page_3 = db.Column(db.Integer)
    label_3 = db.Column(db.Float)
    x_coordinate_3 = db.Column(db.Float)
    y_coordinate_3 = db.Column(db.Float)
    score_3 = db.Column(db.Integer)
    stage_3 = db.Column(db.Integer)
    time_3 = db.Column(db.String(50), primary_key=True)
    evaluation_3 = db.Column(db.Float)

    #아래는 json파일에서 사용자 데이터를 읽어와서 데이터베이스에 저장.
def load_user_data(file_path='users.json'):
    # 파일에서 사용자 정보를 읽어옵니다.
    with open(file_path, 'r') as file:
        client = json.load(file)
    # 읽어온 사용자 정보를 데이터베이스에 저장합니다.
    with app.app_context():
        for clients in client:
        # 사용자 정보에서 사용자 이름을 가져옵니다.
            name = clients.get('username')
            user_id = clients.get('id')
         # 이미 데이터베이스에 존재하는 사용자인지 확인합니다.
            existing_user = client_info.query.filter_by(client_name=name).first()
         # 데이터베이스에 존재하지 않는 경우에만 추가합니다.
            if not existing_user:
            # 새로운 사용자 정보를 데이터베이스에 추가합니다.
                new_user = client_info(client_id=user_id, client_name=name)
                db.session.add(new_user)
                # 변경사항을 저장합니다.
        db.session.commit()
# load_user_data 함수를 호출하여 데이터를 로드하고 데이터베이스에 저장합니다.
load_user_data()

from sqlalchemy.exc import IntegrityError

def load_game1_data(file_path='active1.json'):
    with open(file_path, 'r') as file:
        logs = json.load(file)
    
    with app.app_context():
        for entry in logs:
            id_1 = entry.get('id')
            page_1 = entry.get('page')
            label_1 = entry.get('label')
            x_coordinate_1 = entry.get('x_coordinate')
            y_coordinate_1 = entry.get('y_coordinate')
            time_1 = datetime.datetime.strptime(entry.get('time'), '%Y-%m-%d %H:%M:%S')
            score_1 = entry.get('score')
            evaluation_1 = entry.get('evaluation')

            # 새로운 로그 정보를 데이터베이스에 추가합니다.
            new_log = Game1(
                id_1=id_1, 
                page_1=page_1, 
                label_1=label_1, 
                x_coordinate_1=x_coordinate_1, 
                y_coordinate_1=y_coordinate_1, 
                time_1=time_1, 
                score_1=score_1, 
                evaluation_1=evaluation_1
            )
            db.session.add(new_log)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("An error occurred while saving logs to the database. Duplicate entry detected.")
            pass

load_game1_data()


# class JSONFormatter(logging.Formatter):
#     def format(self, record):
#         x_coordinate = getattr(record, 'x_coordinate', None)
#         y_coordinate = getattr(record, 'y_coordinate', None)
#         log_record = {
#             'id':'01',
#             'page': getattr(record, 'page', None),
#             'label': getattr(record, 'label', None),
#             'x_coordinate': x_coordinate,  # x 좌표
#             'y_coordinate': y_coordinate,  # y 좌표
#             'score': getattr(record, 'score', None),
#             'stage': getattr(record, 'stage', None),
#             'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             'message': record.getMessage(),
#             'func': record.funcName,
#             'evaluation': getattr(record, 'evaluation', None)
#         }
#         return json.dumps(log_record)
class ConditionalRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        # game1 관련 로그 조건
        if hasattr(record, 'label_1') or (hasattr(record, 'x_coordinate_1') and hasattr(record, 'y_coordinate_1')):
            super().emit(record)
        # game2 관련 로그 조건
        elif hasattr(record, 'label_2') or (hasattr(record, 'x_coordinate_2') and hasattr(record, 'y_coordinate_2')):
            super().emit(record)
        # game3 관련 로그 조건
        elif hasattr(record, 'label_3') or (hasattr(record, 'x_coordinate_3') and hasattr(record, 'y_coordinate_3')):
            super().emit(record)
# class SQLAlchemyHandler(logging.Handler):
#     def emit(self, record):
#         with app.app_context():
#             try:
#                 if hasattr(record, 'label_1') or (hasattr(record, 'x_coordinate_1') and hasattr(record, 'y_coordinate_1')):
#                     log = Game1(
#                         id_1=getattr(record, 'id_1', None),
#                         label_1=getattr(record, 'label_1', None),
#                         x_coordinate_1=getattr(record, 'x_coordinate_1', None),
#                         y_coordinate_1=getattr(record, 'y_coordinate_1', None),
#                         score_1=getattr(record, 'score_1', None),
#                         time_1=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                         page_1=getattr(record, 'page_1', None),
#                         evaluation_1=getattr(record, 'evaluation_1', None)
#                     )
#                 elif hasattr(record, 'label_2') or (hasattr(record, 'x_coordinate_2') and hasattr(record, 'y_coordinate_2')):
#                     log = Game2(
#                         id_2=getattr(record, 'id_1', None),
#                         label_2=getattr(record, 'label_2', None),
#                         x_coordinate_2=getattr(record, 'x_coordinate_2', None),
#                         y_coordinate_2=getattr(record, 'y_coordinate_2', None),
#                         score_2=getattr(record, 'score_2', None),
#                         stage_2=getattr(record, 'stage_2', None),
#                         time_2=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                         page_2=getattr(record, 'page_2', None),
#                         evaluation_2=getattr(record, 'evaluation_2', None)
#                     )
#                 elif hasattr(record, 'label_3') or (hasattr(record, 'x_coordinate_3') and hasattr(record, 'y_coordinate_3')):
#                     log = Game3(
#                         id_3=getattr(record, 'id_1', None),
#                         label_3=getattr(record, 'label_3', None),
#                         x_coordinate_3=getattr(record, 'x_coordinate_3', None),
#                         y_coordinate_3=getattr(record, 'y_coordinate_3', None),
#                         score_3=getattr(record, 'score_3', None),
#                         stage_3=getattr(record, 'stage_3', None),
#                         time_3=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                         page_3=getattr(record, 'page_3', None),
#                         evaluation_3=getattr(record, 'evaluation_3', None)
#                     )
#                 db.session.add(log)
#                 db.session.commit()
#             except Exception as e:
#                 print("An error occurred while saving log to database:", e)
#                 # 데이터베이스에 로그를 저장하는 동안 오류가 발생하면 파일에도 로그를 기록합니다.
# def setup_logger():
# # 파일 핸들러 설정
#     file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
#     file_handler.setLevel(logging.INFO)
# # file_formatter = JSONFormatter()  # JSONFormatter를 사용하려면 주석 해제
# # file_handler.setFormatter(file_formatter)
#     #DB 핸들러 설정
#     db_handler_game1 = SQLAlchemyHandler()
#     db_handler_game1.setLevel(logging.INFO)
#     # db_formatter_game1 = JSONFormatter()  # JSONFormatter를 사용하려면 주석 해제
#     # db_handler_game1.setFormatter(db_formatter_game1)
#     db_handler_game2 = SQLAlchemyHandler()
#     db_handler_game2.setLevel(logging.INFO)
#     # db_formatter_game2 = JSONFormatter()  # JSONFormatter를 사용하려면 주석 해제
#     # db_handler_game2.setFormatter(db_formatter_game2)
#     db_handler_game3 = SQLAlchemyHandler()
#     db_handler_game3.setLevel(logging.INFO)
#     # db_formatter_game3 = JSONFormatter()  # JSONFormatter를 사용하려면 주석 해제
#     # db_handler_game3.setFormatter(db_formatter_game3)
#     # 앱 로거 설정
#     app.logger.addHandler(file_handler)
#     app.logger.addHandler(db_handler_game1)
#     app.logger.addHandler(db_handler_game2)
#     app.logger.addHandler(db_handler_game3)
#     app.logger.setLevel(logging.INFO)
#     # SQLAlchemy 로거 설정
#     sqlalchemy_logger = logging.getLogger('sqlalchemy')
#     sqlalchemy_logger.addHandler(file_handler)
#     sqlalchemy_logger.addHandler(db_handler_game1)
#     sqlalchemy_logger.addHandler(db_handler_game2)
#     sqlalchemy_logger.addHandler(db_handler_game3)
def setup_logger():
    file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    sqlalchemy_logger = logging.getLogger('sqlalchemy')
    sqlalchemy_logger.addHandler(file_handler)

setup_logger()
# @app.after_request
# def after_request(response):
#     if response.content_type == 'application/json':
#         with open('log.json', 'r') as file:
#             log_data = [json.loads(line) for line in file]
#         response_data = response.get_json()
#         if isinstance(response_data, dict):
#             response_data['logs'] = log_data
#         else:
#             response_data = {'data': response_data, 'logs': log_data}
#         response.set_data(json.dumps(response_data))
#     return response

# def log_event(data):
#     app.logger.info(
#         f"game 1의 이벤트 로깅",
#         extra={
#             'id_1' : data.get('id_1'),
#             'page_1' : data.get('page_1'),
#             'label_1' : data.get('label_1'),
#             'x_coordinate' : data.get('x_coordinate'),
#             'y_coordinate' : data.get('y_coordinate'),
#             'score_1' : data.get('score_1'),
#             'evaluation_1' : data.get('evaluation_1')
#         }
#     )

# @app.route('/log_event', methods=['POST'])
# def log_event_route():
#     data = request.json

# def log_status():
#     if lock.acquire(blocking=False):
#         try:
#             with app.app_context():
#                 page_id = getattr(g, 'page_id', 999)
#                 label = getattr(g, 'label', None)
#                 x_coordinate=getattr(g, 'x_coordinate', None)
#                 y_coordinate=getattr(g, 'y_coordinate', None)
#                 if label is not None or (x_coordinate is not None and y_coordinate is not None):
#                     app.logger.info(f"조건에 따라 로그 기록 - log {page_id}", extra={'page': page_id, 'label': label, 'x_coordinate': x_coordinate, 'y_coordinate': y_coordinate})
#         finally:
#             lock.release()
# @app.route('/log_event', methods=['POST'])
# def log_event():
#     data = request.json
#     g.page_id = data.get('page_id', 999)
#     g.label = data.get('label', None)
#     g.x_coordinate = data.get('x_coordinate', None)
#     g.y_coordinate = data.get('y_coordinate', None)
#     log_status()
#     return {"status":"logged"}
def log_to_database_game1(id_1, page_1, label_1, x_coordinate_1, y_coordinate_1, score_1, evaluation_1):
        # 데이터베이스에 로그를 저장하는 코드를 작성
    try:
        new_log = Game1(
            id_1=id_1,
            page_1=page_1,
            label_1=label_1,
            x_coordinate_1=x_coordinate_1,
            y_coordinate_1=y_coordinate_1,
            score_1=score_1,
            time_1=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            evaluation_1=evaluation_1
        )
        db.session.add(new_log)
        db.session.commit()
        print(f"Game1 로그가 성공적으로 저장되었습니다: {new_log}")
    except Exception as e:
        app.logger.error(f"Game1 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다:{e}")
        print(f"Game1 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다: {e}")
def log_to_database_game2(id_2, page_2, label_2, x_coordinate_2, y_coordinate_2, score_2, evaluation_2):
        # 데이터베이스에 로그를 저장하는 코드를 작성
    try:
        new_log = Game2(
            id_2=id_2,
            page_2=page_2,
            label_2=label_2,
            x_coordinate_2=x_coordinate_2,
            y_coordinate_2=y_coordinate_2,
            score_2=score_2,
            time_2=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            evaluation_2=evaluation_2
        )
        db.session.add(new_log)
        db.session.commit()
        print(f"Game2 로그가 성공적으로 저장되었습니다: {new_log}")
    except Exception as e:
        app.logger.error(f"Game2 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다:{e}")
        print(f"Game2 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다: {e}")
def log_to_database_game3(id_3, page_3, label_3, x_coordinate_3, y_coordinate_3, score_3, evaluation_3):
        # 데이터베이스에 로그를 저장하는 코드를 작성
    try:
        new_log = Game3(
            id_3=id_3,
            page_3=page_3,
            label_3=label_3,
            x_coordinate_3=x_coordinate_3,
            y_coordinate_3=y_coordinate_3,
            score_3=score_3,
            time_3=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            evaluation_3=evaluation_3
        )
        db.session.add(new_log)
        db.session.commit()
        print(f"Game3 로그가 성공적으로 저장되었습니다: {new_log}")
    except Exception as e:
        app.logger.error(f"Game3 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다:{e}")
        print(f"Game3 데이터베이스에 로그를 저장하는 동안 오류가 발생했습니다: {e}")
@app.route('/log_game1', methods=['POST'])
def log_game1():
    id_1 =request.form.get('id_1')
    page_1 = request.form.get('page_1')
    label_1= request.form.get('label_1')
    x_coordinate_1=request.form.get('x_coordinate_1')
    y_coordinate_1=request.form.get('y_coordinate_1')
    score_1=request.form.get('score_1')
    evaluation_1 = request.form.get('evaluation_1')
    print(f"Received data: id_1={id_1}, page_1={page_1}, label_1={label_1}, x_coordinate_1={x_coordinate_1}, y_coordinate_1={y_coordinate_1}, score_1={score_1}, evaluation_1={evaluation_1}")
    log_to_database_game1(id_1,page_1,label_1, x_coordinate_1,y_coordinate_1, score_1, evaluation_1)
    return{"status":"logged"}

@app.route('/log_game2', methods=['POST'])
def log_game2():
    id_2 =request.form.get('id_2')
    page_2 = request.form.get('page_2')
    label_2= request.form.get('label_2')
    x_coordinate_2=request.form.get('x_coordinate_2')
    y_coordinate_2=request.form.get('y_coordinate_2')
    score_2=request.form.get('score_2')
    evaluation_2 = request.form.get('evaluation_2')
    print(f"Received data: id_2={id_2}, page_2={page_2}, label_2={label_2}, x_coordinate_2={x_coordinate_2}, y_coordinate_2={y_coordinate_2}, score_2={score_2}, evaluation_2={evaluation_2}")
    log_to_database_game2(id_2,page_2,label_2, x_coordinate_2 ,y_coordinate_2, score_2, evaluation_2)
    return{"status":"logged"}

@app.route('/log_game3', methods=['POST'])
def log_game3():
    id_3 =request.form.get('id_3')
    page_3 = request.form.get('page_3')
    label_3= request.form.get('label_3')
    x_coordinate_3=request.form.get('x_coordinate_3')
    y_coordinate_3=request.form.get('y_coordinate_3')
    score_3=request.form.get('score_3')
    evaluation_3 = request.form.get('evaluation_3')
    print(f"Received data: id_3={id_3}, page_3={page_3}, label_3={label_3}, x_coordinate_3={x_coordinate_3}, y_coordinate_3={y_coordinate_3}, score_3={score_3}, evaluation_3={evaluation_3}")
    log_to_database_game3(id_3,page_3, x_coordinate_3 ,y_coordinate_3, score_3, evaluation_3)
    return{"status":"logged"}


if __name__ == '__main__': app.run(debug=True)

