from flask import Flask, request, redirect, render_template, url_for
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import json

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

# RotatingFileHandler 설정
handler = RotatingFileHandler('log.json', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)

# JSON 포맷터 설정
formatter = JSONFormatter()
handler.setFormatter(formatter)

# Flask 애플리케이션에 핸들러 추가
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# @app.route('/test', methods=['POST'])
# def hello_world():
#     app.logger.info('Home page accessed')
#     return 'Hello, World!'

@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    app.logger.info('Test endpoint accessed with data: %s', data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True)


