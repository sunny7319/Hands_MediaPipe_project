from flask import Flask, request, redirect, render_template, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json
from apscheduler.schedulers.background import BackgroundScheduler
import threading #여기 추가됨 -찬혁
import datetime 


app = Flask(__name__)
lock = threading.Lock() #여기 추가됨 -찬혁

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # 기존 SQLAlchemy 인스턴스 가져오기

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(50))
    level = db.Column(db.String(50))
    message = db.Column(db.Text)
    path = db.Column(db.String(255))
    func = db.Column(db.String(255))
    line = db.Column(db.Integer)
    request = db.Column(db.String(255))
    ip = db.Column(db.String(50))
    
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'path': record.pathname,
            'func': record.funcName,
            'line': record.lineno,
            'request': request.method + " " + request.url if request else None,
            'ip': request.remote_addr if request else None,
        }
        return json.dumps(log_record)
    
from flask import current_app
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        with current_app.app_context():
        # 데이터베이스에 로그를 저장하는 코드 작성
            try:
                request_info = {
                    'method': request.method if request else None,
                    'url': request.url if request else None,
                    'remote_addr': request.remote_addr if request else None
                }
                log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간을 문자열로 포맷팅합니다

                log = Log(
                    time=log_time,
                    level=record.levelname,
                    message=record.getMessage(),
                    path=record.pathname,
                    func=record.funcName,
                    line=record.lineno,
                    request=json.dumps(request_info),
                    ip=request_info['remote_addr']
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                print("An error occurred while saving log to database:", e)


def setup_logger():
        print("setup_logger 함수가 호출되었습니다.")

        # RotatingFileHandler 설정
        file_handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)

        # SQLAlchemyHandler 설정
        db_handler = SQLAlchemyHandler()
        db_handler.setLevel(logging.INFO)
        db_formatter = JSONFormatter()
        db_handler.setFormatter(db_formatter)

        # # Flask 애플리케이션에 핸들러 추가
        app.logger.addHandler(file_handler)
        app.logger.addHandler(db_handler)
        app.logger.setLevel(logging.INFO)

        # SQLAlchemy 로거에도 핸들러 추가
        logging.getLogger('sqlalchemy').addHandler(file_handler)
        logging.getLogger('sqlalchemy').addHandler(db_handler)

setup_logger()

@app.after_request
def after_request(response):
    print("after_request 함수가 호출되었습니다.")
    if response.content_type == 'application/json':
        # log.json 파일에서 로그 데이터 읽어오기
        with open('log.json', 'r') as file:
            log_data = [json.loads(line) for line in file]
        # 응답 데이터에 로그 데이터 추가
        response_data = response.get_json()
        if isinstance(response_data, dict):
            response_data['logs'] = log_data
        else:
            response_data = {'data': response_data, 'logs': log_data}
        response.set_data(json.dumps(response_data))
    return response

# 주기적으로 로그 상태를 기록하는 함수
def log_status(): #여기 추가됨 -찬혁
    if lock.acquire(blocking=False):
        try:
            print("log_status 함수가 호출되었습니다.")
            with app.app_context():
                app.logger.info("5초마다 업데이트")
        finally:
            lock.release()

# 백그라운드 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=5)
scheduler.start()

@app.route('/')
def index():
    # return 'random : <strong>'+str(random.random())+'</strong>'
    return render_template('game.html')

if __name__ == '__main__':
    app.run()