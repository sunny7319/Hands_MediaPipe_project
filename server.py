from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp

app = Flask(__name__)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# 글로벌 변수로 설정
toggle = 0

def generate_frames():
    global toggle
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # 프레임을 좌우 반전
            frame = cv2.flip(frame, 1)

            # 손 랜드마크 추적
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(image)
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    toggle = 1

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
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
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# toggle 값을 반환하는 엔드포인트 추가
@app.route('/toggle_status')
def toggle_status():
    global toggle
    return jsonify({'toggle': toggle})

if __name__ == '__main__':
    app.run(debug=True)