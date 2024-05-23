from flask import Flask, request, redirect, render_template, url_for
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/back')
def back():
    return redirect(url_for('index'))

# @app.route('/logs', methods=['GET'])
# def get_logs():
#     with open('log.json', 'r') as file:
#         log_data = [json.loads(line) for line in file]
#     return jsonify(log_data)

# JSON 로그 포맷터 설정
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

def setup_logger():
    # RotatingFileHandler 설정
    handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)

    # JSON 포맷터 설정
    formatter = JSONFormatter()
    handler.setFormatter(formatter)

    # Flask 애플리케이션에 핸들러 추가
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
setup_logger()

    # @app.route('/test', methods=['POST'])
    # def hello_world():
    #     app.logger.info('Home page accessed')
    #     return 'Hello, World!'

@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    app.logger.info('Test endpoint accessed with data: %s', data)
    return jsonify(data)

@app.after_request
def after_request(response):
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
    with app.app_context():
        app.logger.info("30초마다 업데이트")

scheduler = BackgroundScheduler()
scheduler.add_job(func=log_status, trigger="interval", seconds=30)
scheduler.start()

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        scheduler.shutdown()

# if __name__ == '__main__':
#     app.run(debug=True)


