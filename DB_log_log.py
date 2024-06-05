from flask import Flask, g, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json, os, threading, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time, os

app = Flask(__name__)
lock = threading.Lock()

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

def load_game1_data(file_path='game1.json'):
    try:
        with open(file_path, 'r') as file:
            logs = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{file_path}'")
        return
    
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
            existing_log = Game1.query.filter_by(id_1=id_1, time_1=time_1).first()
            if existing_log is None:
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

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('game1.json'):
            print("File modified:", event.src_path)
            load_game1_data(event.src_path)

def start_file_monitoring():
    observer = Observer()
    observer.schedule(MyHandler(), path='.')
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
# 백그라운드에서 파일 모니터링을 시작합니다.
thread = threading.Thread(target=start_file_monitoring)
thread.daemon = True
thread.start()

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

def setup_logger():
    file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    sqlalchemy_logger = logging.getLogger('sqlalchemy')
    sqlalchemy_logger.addHandler(file_handler)

setup_logger()

file_monitor_thread = threading.Thread(target=start_file_monitoring)
file_monitor_thread.daemon = True
file_monitor_thread.start()

if __name__ == '__main__':
    app.run(debug=True)

