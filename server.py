from flask import Flask, render_template, Response
import cv2
import mediapipe as mp

app = Flask(__name__)

# Mediapipe hands 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5)

# 웹캠 스트리밍 함수
def gen_frames():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

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
            'description': '손으로 동물이나 모양을 표현하는 놀이입니다'
        },
        '두더지 잡기': {
            'title': '두더지 잡기',
            'description': '주어진 문제에 맞는 단어를 가지고 있는 두더지를 잡는 게임입니다'
        },
        '산성비': {
            'title': '산성비',
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
