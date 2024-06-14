from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from logging.handlers import RotatingFileHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import threading
import datetime
import time
import json
import os

app = Flask(__name__)
lock = threading.Lock()

db = SQLAlchemy()

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bgm:0501@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 데이터베이스 연결 상태 확인 함수
def check_db_connection():
    try:
        with db.engine.connect() as connection:
            connection.execute("SELECT 1")  # 예시로 간단한 쿼리를 실행하여 연결 상태 확인
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
    return True

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
    time_1 = db.Column(db.DateTime, primary_key=True)
    x_coordinate_1 = db.Column(db.Float)
    y_coordinate_1 = db.Column(db.Float)
    label_1 = db.Column(db.Float)
    evaluation_1 = db.Column(db.Float)
    page_1 = db.Column(db.Integer)

class Game2(db.Model):
    __tablename__ = 'game2'
    id_2 = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False, primary_key=True)
    # time_2 = db.Column(db.DateTime, primary_key=True)
    time_2 = db.Column(db.String(50), primary_key=True)
    x_coordinate_2 = db.Column(db.Float)
    y_coordinate_2 = db.Column(db.Float)
    score_2 = db.Column(db.Integer)
    stage_2 = db.Column(db.Integer)
    evaluation_2 = db.Column(db.Float)
    page_2 = db.Column(db.Integer)

class Game3(db.Model):
    __tablename__ = 'game3'
    id_3 = db.Column(db.Integer, db.ForeignKey('client_info.client_id'), nullable=False, primary_key=True)
    time_3 = db.Column(db.DateTime, primary_key=True)
    x_coordinate_3 = db.Column(db.Float)
    y_coordinate_3 = db.Column(db.Float)
    label_3 = db.Column(db.Float)
    evaluation_3 = db.Column(db.Float)


# #아래는 json파일에서 사용자 데이터를 읽어와서 데이터베이스에 저장.
# def load_user_data(file_path='users.json'):
#     # 파일이 존재하는지 확인합니다.
#     if not os.path.exists(file_path):
#         print(f"File {file_path} does not exist. Skipping data load.")
#         return    
    
#     try:
#         # 파일에서 사용자 정보를 읽어옵니다.
#         with open(file_path, 'r', encoding='utf-8') as file:
#             client = json.load(file)
#         # 읽어온 사용자 정보를 데이터베이스에 저장합니다.
#         with app.app_context():
#             for clients in client:
#             # 사용자 정보에서 사용자 이름을 가져옵니다.
#                 name = clients.get('username')
#                 user_id = clients.get('id')
#             # 이미 데이터베이스에 존재하는 사용자인지 확인합니다.
#                 existing_user = client_info.query.filter_by(client_name=name).first()
#             # 데이터베이스에 존재하지 않는 경우에만 추가합니다.
#                 if not existing_user:
#                 # 새로운 사용자 정보를 데이터베이스에 추가합니다.
#                     new_user = client_info(client_id=user_id, client_name=name)
#                     db.session.add(new_user)
#                     # 변경사항을 저장합니다.
#             db.session.commit()
#     except Exception as error:
#         print(f"An error occurred while loading user data: {error}")

# # load_user_data 함수를 호출하여 데이터를 로드하고 데이터베이스에 저장합니다.
# load_user_data()

def load_user_data(file_path='users.json'):
    # 데이터베이스 연결 상태 확인
    if not check_db_connection():
        print("Database connection is not established. Skipping function execution.")
        return  # 여기서 함수 실행을 중지하고 이후 코드를 실행하지 않음

    # 파일이 존재하는지 확인합니다.
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Skipping data load.")
        return    
    
    try:
        # 파일에서 사용자 정보를 읽어옵니다.
        with open(file_path, 'r', encoding='utf-8') as file:
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
    except Exception as error:
        print(f"An error occurred while loading user data: {error}")
load_user_data()


# def load_game1_data(file_path='game1.json'):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             logs = json.load(file)
#     except FileNotFoundError:
#         print(f"Error: File '{file_path}' not found")
#         return
#     except json.JSONDecodeError:
#         print(f"Error: Invalid JSON format in file '{file_path}'")
#         return
    
#     with app.app_context():
#         for entry in logs:
#             id_1 = entry.get('id')
#             page_1 = entry.get('page')
#             label_1 = entry.get('label')
#             x_coordinate_1 = entry.get('x_coordinate')
#             y_coordinate_1 = entry.get('y_coordinate')
#             time_1 = datetime.datetime.strptime(entry.get('time'), '%Y-%m-%d %H:%M:%S')
#             # score_1 = entry.get('score')
#             evaluation_1 = entry.get('evaluation')

#             # 새로운 로그 정보를 데이터베이스에 추가합니다.
#             existing_log = Game1.query.filter_by(id_1=id_1, time_1=time_1).first()
#     #  try:
#     #             existing_log = Game1.query.filter_by(id_1=id_1, time_1=time_1).first()
#     #         except Exception as e:
#     #             print(f"An error occurred while querying Game1 table: {e}")
#     #             continue  # Skip this entry and proceed with the next one
            
#             if not existing_log:
#                 new_log = Game1(
#                     id_1=id_1, 
#                     page_1=page_1, 
#                     label_1=label_1, 
#                     x_coordinate_1=x_coordinate_1, 
#                     y_coordinate_1=y_coordinate_1, 
#                     time_1=time_1, 
#                     evaluation_1=evaluation_1
#                 )
#                 db.session.add(new_log)
        
#         try:
#             db.session.commit()
#         except IntegrityError:
#             db.session.rollback()
#             print("An error occurred while saving logs to the database. Duplicate entry detected.")
#         except Exception as e:
#             db.session.rollback()
#             print(f"An error occurred while committing to the database: {e}")

# load_game1_data()

# 데이터베이스에 game1 데이터를 로드하는 함수
def load_game1_data(file_path='game1.json'):
    # 데이터베이스 연결 상태 확인
    if not check_db_connection():
        print("Database connection is not established. Skipping function execution.")
        return  # 여기서 함수 실행을 중지하고 이후 코드를 실행하지 않음

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
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
            evaluation_1 = entry.get('evaluation')

            # 새로운 로그 정보를 데이터베이스에 추가합니다.
            existing_log = Game1.query.filter_by(id_1=id_1, time_1=time_1).first()

            if not existing_log:
                new_log = Game1(
                    id_1=id_1, 
                    page_1=page_1, 
                    label_1=label_1, 
                    x_coordinate_1=x_coordinate_1, 
                    y_coordinate_1=y_coordinate_1, 
                    time_1=time_1, 
                    evaluation_1=evaluation_1
                )
                db.session.add(new_log)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("An error occurred while saving logs to the database. Duplicate entry detected.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while committing to the database: {e}")
load_game1_data()



# def load_game2_data(file_path='game2.json'):
#     try:
#         with open(file_path, 'r') as file:
#             logs = json.load(file)
#     except FileNotFoundError:
#         print(f"Error: File '{file_path}' not found")
#         return
#     except json.JSONDecodeError:
#         print(f"Error: Invalid JSON format in file '{file_path}'")
#         return
    
#     with app.app_context():
#         for entry in logs:
#             id_2 = entry.get('id')
#             page_2 = entry.get('page')
#             x_coordinate_2 = entry.get('x_coordinate')
#             y_coordinate_2 = entry.get('y_coordinate')
#             time_2 = datetime.datetime.strptime(entry.get('time'), '%Y-%m-%d %H:%M:%S')
#             score_2 = entry.get('score')
#             stage_2 = entry.get('stage')
#             evaluation_2 = entry.get('evaluation')

#             # 새로운 로그 정보를 데이터베이스에 추가합니다.
#             # existing_log = Game2.query.filter_by(id_2=id_2, time_2=time_2).first()
#             # 새로운 로그 정보를 데이터베이스에 추가합니다.
#             existing_log = db.session.query(Game2).filter(
#                 Game2.id_2 == id_2,
#                 func.cast(Game2.time_2, sqlalchemy.TIMESTAMP) == time_2
#             ).first()

#             if existing_log is None:
#                 new_log = Game2(
#                     id_2=id_2, 
#                     page_2=page_2, 
#                     x_coordinate_2=x_coordinate_2, 
#                     y_coordinate_2=y_coordinate_2, 
#                     time_2=time_2, 
#                     score_2=score_2, 
#                     stage_2=stage_2,
#                     evaluation_2=evaluation_2
#                 )
#                 db.session.add(new_log)
        
#         try:
#             db.session.commit()
#         except IntegrityError:
#             db.session.rollback()
#             print("An error occurred while saving logs to the database. Duplicate entry detected.")
#             pass

# load_game2_data()

# 데이터베이스에 game2 데이터를 로드하는 함수
# 데이터베이스 연결 상태 확인 함수
# def check_db_connection():
#     try:
#         with db.engine.connect() as connection:
#             connection.execute("SELECT 1")  # 예시로 간단한 쿼리를 실행하여 연결 상태 확인
#     except Exception as e:
#         print(f"Database connection error: {e}")
#         return False
#     return True

# 데이터베이스에 game2 데이터를 로드하는 함수
def load_game2_data(file_path='game2.json'):
    # 데이터베이스 연결 상태 확인
    if not check_db_connection():
        print("Database connection is not established. Skipping function execution.")
        return  # 여기서 함수 실행을 중지하고 이후 코드를 실행하지 않음

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
            id_2 = entry.get('id')
            page_2 = entry.get('page')
            x_coordinate_2 = entry.get('x_coordinate')
            y_coordinate_2 = entry.get('y_coordinate')
            time_2 = datetime.datetime.strptime(entry.get('time'), '%Y-%m-%d %H:%M:%S')
            score_2 = entry.get('score')
            stage_2 = entry.get('stage')
            evaluation_2 = entry.get('evaluation')

            # 새로운 로그 정보를 데이터베이스에 추가합니다.
            existing_log = db.session.query(Game2).filter(
                Game2.id_2 == id_2,
                func.cast(Game2.time_2, db.TIMESTAMP) == time_2
            ).first()

            if existing_log is None:
                new_log = Game2(
                    id_2=id_2, 
                    page_2=page_2, 
                    x_coordinate_2=x_coordinate_2, 
                    y_coordinate_2=y_coordinate_2, 
                    time_2=time_2, 
                    score_2=score_2, 
                    stage_2=stage_2,
                    evaluation_2=evaluation_2
                )
                db.session.add(new_log)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("An error occurred while saving logs to the database. Duplicate entry detected.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while committing to the database: {e}")
load_game2_data()


class MyHandler(FileSystemEventHandler):
    def on_modified_1(self, event):
        if event.src_path.endswith('game1.json'):
            print("File modified:", event.src_path)
            load_game1_data(event.src_path)
    def on_modified_2(self, event):
        if event.src_path.endswith('game2.json'):
            print("File modified:", event.src_path)
            load_game2_data(event.src_path)

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

file_monitor_thread = threading.Thread(target=start_file_monitoring)
file_monitor_thread.daemon = True
file_monitor_thread.start()

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
