from flask import Flask, render_template, Response
import cv2


app = Flask(__name__)


# 웹캠 스트리밍 함수
def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
            'description': '손으로 동물이나 모양을 표현하는 놀이입니다'
        },
        '두더지 잡기': {
            'title': '두더지 잡기',
            'image': 'game1.png',
            'description': '주어진 문제에 맞는 단어를 가지고 있는 두더지를 잡는 게임입니다'
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
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
