from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, render_template, url_for
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

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

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'path': record.pathname,
            'func': record.funcName,
            'line': record.lineno,
            'request': request.method + " " + request.url if request else None,
            'ip': request.remote_addr if request else None,
        }
        return json.dumps(log_record)
    
class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        # 데이터베이스에 로그를 저장하는 코드 작성
        try:
            request_info = {
                'method': request.method if request else None,
                'url': request.url if request else None,
                'remote_addr': request.remote_addr if request else None
            }
            log = Log(
                # time=self.formatTime(record, self.datefmt),
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

    # Flask 애플리케이션에 핸들러 추가
    app.logger.addHandler(file_handler)
    app.logger.addHandler(db_handler)
    app.logger.setLevel(logging.INFO)

    # SQLAlchemy 로거에도 핸들러 추가
    logging.getLogger('sqlalchemy').addHandler(file_handler)
    logging.getLogger('sqlalchemy').addHandler(db_handler)

setup_logger()


@app.after_request
def after_request(response):
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
def log_status():
    with app.app_context():
        app.logger.info("10초마다 업데이트")

# 백그라운드 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=10)
scheduler.start()

# Initialize the database
# with app.app_context():
#     db.init_app(app)
#     db.create_all()

nextId = 4
topics = [
    {'id': 1, 'title': 'HTML', 'body': 'HTML is ...'},
    {'id': 2, 'title': 'CSS', 'body': 'CSS is ...'},
    {'id': 3, 'title': 'JavaScript', 'body': 'JavaScript is ...'}
]


def template(contents, content, id=None):
    contextUI = ''
    if id != None:
        contextUI = f'''
            <li><a href="/update/{id}/">update</a><li>
            <li><form action="/delete/{id}/" method="POST"><input type="submit" value="delete"><form></li>
        '''
    return f'''<!doctype html>
    <html>
        <body>
            <h1><a href="/">WEB</a></h1>
            <ol>
                {contents}
            </ol>
            {content}
            <ul>
                <li><a href="/create/">create</a></li>
                {contextUI}
            </ul>
        </body>
    </html>
    '''


def getContents():
    liTags = ''
    for topic in topics:
        liTags = liTags + f'<li><a href="/read/{topic["id"]}/">{topic["title"]}</a></li>'
    
    return liTags


@app.route('/')
def index():
    return template(getContents(), '<h2>Welcome</h2>Hello, Web')


@app.route('/read/<int:id>/')
def read(id):
    title = ''
    body = ''
    for topic in topics:
        if id == topic['id']:
            title = topic['title']
            body = topic['body']
            break

    return template(getContents(), f'<h2>{title}</h2>{body}', id)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method =='GET':
        content = '''
            <form action="/create/" method="POST">
                <p><input type="text" name="title" placeholder="title"></p>
                <p><textarea name="body" placeholder="body"></textarea></p>
                <p><input type="submit" value="create"></p>
            </form>
        '''
        return template(getContents(), content)
    
    elif request.method == 'POST':
        global nextId
        title = request.form['title']
        body = request.form['body']
        new_topic = Topic(title=title, body=body)  # 새로운 Topic 객체 생성
        db.session.add(new_topic)
        db.session.commit()
        nextId = new_topic.id + 1  # 다음 ID 업데이트
        url = '/read/' + str(nextId) + '/'
        return redirect(url)


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update(id):
    if request.method =='GET':
        title = ''
        body = ''
        for topic in topics:
            if id == topic['id']:
                title = topic['title']
                body = topic['body']
                break
        content = f'''
            <form action="/update/{id}/" method="POST">
                <p><input type="text" name="title" placeholder="title" value="{title}"></p>
                <p><textarea name="body" placeholder="body">{body}</textarea></p>
                <p><input type="submit" value="update"></p>
            </form>
        '''
        return template(getContents(), content)
    
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        for topic in topics:
            if id == topic['id']:
                title = topic['title']
                body = topic['body']
                break
        url = '/read/' + str(id) + '/'
        return redirect(url)
    

@app.route('/delete/<int:id>/', methods=['POST'])
def delete(id):
    for topic in topics:
        if id == topic['id']:
            topics.remove(topic)
            break
    return redirect('/')


@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    app.logger.info('Test endpoint accessed with data: %s', data)
    return jsonify(data)

@app.route('/load_logs', methods=['GET'])
def load_logs():
    try:
        with open('log.json', 'r') as file:
            log_data = json.load(file)
        
        for record in log_data:
            log_entry = Log(
                time=record.get('time'),
                level=record.get('level'),
                message=record.get('message'),
                path=record.get('path'),
                func=record.get('func'),
                line=record.get('line'),
                request=record.get('request'),
                ip=record.get('ip')
            )
            db.session.add(log_entry)
        db.session.commit()

        return "Logs loaded successfully into the database"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# Flask 애플리케이션 실행
if __name__ == '__main__':
    try:
        # 데이터베이스 초기화
        # with app.app_context():
            # db.init_app(app)
            # db.create_all()
        app.run(debug=True)
    finally:
        pass
# @app.route('/test_db', methods=['GET'])
# def test_db():
#     try:
#         # Create example topics
#         topics = [
#             {'title': 'HTML 기본 구조', 'body': 'HTML 문서의 기본적인 구조와 태그들에 대해 알아봅니다.'},
#             {'title': 'CSS 선택자', 'body': 'CSS에서 사용되는 다양한 선택자의 종류와 각각의 역할에 대해 학습합니다.'},
#             {'title': 'JavaScript 변수', 'body': 'JavaScript에서 변수를 선언하고 활용하는 방법에 대해 배웁니다.'},
#             {'title': 'Python 함수', 'body': 'Python에서 함수를 정의하고 호출하는 방법에 대해 알아봅니다.'}
#         ]

#         # Add topics to the database
#         for topic_data in topics:
#             new_topic = Topic(title=topic_data['title'], body=topic_data['body'])
#             db.session.add(new_topic)
#         db.session.commit()

#         return "Example topics added to the database"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

    
# if __name__ == "__main__":  
#     app.run(port=5001, debug=True)