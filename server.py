from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from login import save_user, load_users
from game1 import check_frames, generate_frames, get_score, get_position, get_labels_positions
from game3 import predict_image
from PIL import Image
import base64
from io import BytesIO
import json

app = Flask(__name__)

# score = 0

# 글로벌 변수로 설정
toggle = 0

game_data = {
    '그림자 놀이터': {
        'title': '그림자 놀이터',
        'image': 'game1.png',
        'description': '손으로 동물과 모양을 만들어 보세요!'
    },
    '잡아라! 두더지!': {
        'title': '잡아라! 두더지!',
        'image': 'game1.png',
        'description': '주어진 단어와 같은 단어를 가지고 있는 두더지를 잡아보세요!'
    },
    '한글 놀이': {
        'title': '한글 놀이',
        'image': 'game1.png',
        'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.'
    }
}

quiz_data = [
    {'answer': '가지', 'image': 'img/game3/가지.jpeg'},
    {'answer': '나비', 'image': 'img/game3/나비.jpeg'},
    {'answer': '다리', 'image': 'img/game3/다리.jpeg'},
    {'answer': '레몬', 'image': 'img/game3/레몬.jpeg'},
    {'answer': '마늘', 'image': 'img/game3/마늘.jpeg'},
    {'answer': '바위', 'image': 'img/game3/바위.jpeg'},
    {'answer': '사슴', 'image': 'img/game3/사슴.png'},
    {'answer': '애기', 'image': 'img/game3/애기.jpeg'},
    {'answer': '자수', 'image': 'img/game3/자수.jpeg'},
    {'answer': '차고', 'image': 'img/game3/차고.jpeg'},
    {'answer': '카레', 'image': 'img/game3/카레.jpeg'},
    {'answer': '태양', 'image': 'img/game3/태양.jpeg'},
    {'answer': '팔', 'image': 'img/game3/팔.jpeg'},
    {'answer': '하늘', 'image': 'img/game3/하늘.jpeg'}
]


#########################################
########## 로그인/회원가입 화면 ##########
#########################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        users = load_users()
        if any(user['username'] == username for user in users):
            return redirect(url_for('main'))
        else:
            error = '아이디를 찾을 수 없습니다.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        if save_user(username):
            return redirect(url_for('login'))
        else:
            error = '이미 존재하는 아이디입니다.'
            return render_template('signup.html', error=error)
    return render_template('signup.html')


#############################
########## 메인화면 ##########
#############################

@app.route('/main')
def main():
    return render_template('main.html')

# 캠 잘 작동되는지 확인
@app.route('/check_video')
def check_video():
    return Response(check_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


##################################
########## 게임 대기화면 ##########
##################################

@app.route('/game/<game_name>')
def game(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404


#############################
########## 게임화면 ##########
#############################
    
@app.route('/game_play/<game_name>')
def game_play(game_name):
    global game_data
    global quiz_data
    if game_name == '그림자 놀이터':
        position, image_info = get_position()
        return render_template('1.html', game=game_data[game_name], score=get_score(), position=position, image_info=image_info)
    elif game_name == '잡아라! 두더지!':
        return render_template('2.html')
    elif game_name == '한글 놀이':
        quiz = quiz_data[0]  # 첫 번째 퀴즈 로드 (향후 로직 개선 가능)
        return render_template('3.html', game=game_data[game_name], quiz_image=quiz['image'], quiz_data=json.dumps(quiz_data))
    else:
        return "Game not found", 404


###########################
########## game1 ##########
###########################

# 게임 화면에 들어갈 mediapipe 비디오
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_position')
def current_position():
    # 여기서 실시간으로 좌표 데이터를 업데이트
    pos, img_info = get_position()
    return jsonify({
        'x': pos[0],
        'y': pos[1],
        'label': img_info
    })

@app.route('/labels_positions')
def labels_positions():
    labels_positions = get_labels_positions()  # 라벨과 좌표 정보를 가져오는 함수
    return jsonify(labels_positions)

@app.route('/get_position')
def get_position_route():
    label, x, y = get_position()
    return jsonify({'label': label, 'x': x, 'y': y})

# toggle 값을 반환하는 엔드포인트 추가
@app.route('/toggle_status')
def toggle_status():
    global toggle
    return jsonify({'toggle': toggle})


###########################
########## game2 ##########
###########################






###########################
########## game3 ##########
###########################

@app.route('/capture', methods=['POST'])
def capture_image():
    data = request.get_json()
    img_data = data['image']
    img_data = img_data.split(",")[1]
    img = Image.open(BytesIO(base64.b64decode(img_data)))
    predicted_class, predicted_prob, _ = predict_image(img)
    return jsonify({'class': predicted_class, 'probability': predicted_prob})

# @app.route('/next_quiz/<int:quiz_index>')
# def next_quiz(quiz_index):
#     if quiz_index < len(quiz_data):
#         quiz = quiz_data[quiz_index]
#         return jsonify({'image': url_for('static', filename=quiz['image']), 'index': quiz_index})
#     else:
#         return jsonify({'message': '모든 퀴즈를 완료했습니다!'}), 404


################################
########## 평가 페이지 ##########
################################

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        data = request.get_json()
        feedback = data.get('feedback')

        # 서버 콘솔에 데이터 출력
        print(f"Received feedback: {feedback}")

        return jsonify({'status': 'success', 'feedback': feedback})
    return render_template('survey.html')


if __name__ == '__main__':
    app.run(debug=True)