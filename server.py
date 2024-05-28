from flask import Flask, render_template, Response
import cv2
import mediapipe as mp


app = Flask(__name__)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # 손 랜드마크 추적
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(image)
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)  # 캠 최대 해상도가 1280x720 / ToDo 1 : cv2 함수로 늘려야 함
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 4000)

# def generate_frames():
#     if cap.isOpened():
#         print('width: {}, height : {}'.format(cap.get(3), cap.get(4)))  # 화면크기 1280x720를 프린트 -> DB에 저장해보세요
#                                                                         # cap.get(3) = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     while True:
#         ret, fram = cap.read()
        
#         if ret:

#             cv2.imshow('cam', cv2.flip(fram, 1))

#             key = cv2.waitKey(10)

#             if key == ord('a'):
#                 print('key "a" pressed')  # -> 이 이벤트도 DB에 저장해보세요

#             elif (key & 0xFF) == 27:  # ESC 키(27?)를 누르면 break, 캠화면 닫힘
#                 print('Closing windows')
#                 cap.release()
#                 cv2.destroyAllWindows()
#                 break
#         else:
#             print('error')

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
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
