from flask import Flask, Response, request, render_template, redirect, url_for, jsonify
from login import save_user, load_users
from check_frames import check_frames
from game1 import game1_frames, get_data_1
from game2 import game2_frames, get_data_2
from game3 import predict_image
from io import BytesIO
from PIL import Image
from DB_log import db
import base64
# import json

app = Flask(__name__)

game_data = {
    '따라해! 놀이터': {
        'title': '따라해! 놀이터',
        'description': '손으로 동물과 모양을 만들어 보세요!',
        'background': 'img/game1_background.webp'
    },
    '잡아라! 두더지': {
        'title': '잡아라! 두더지',
        'description': '주어진 단어와 같은 단어를 가지고 있는 두더지를 잡아보세요!',
        'background': 'img/game2_background.webp'
    },
    '맞춰라! 색종이': {
        'title': '맞춰라! 색종이',
        'description': '주어진 그림에 맞는 단어를 맞춰주세요!',
        'background': 'img/game3_background.png'
    }
}

# game_list = list(game_data.values())

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

# def find_game_index(title):
#     for index, game in enumerate(game_list):
#         if game['title'] == title:
#             return index
#     return None

@app.route('/game/<game_name>')
def game(game_name):
    global game_data
    # index = find_game_index(game_name)
    if game_name in game_data:
        # game = game_list[index]
        # video_file = f'game{index + 1}.mp4'
        # return render_template('game.html', game=game_data[game_name], video_file=video_file)
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
    if game_name == '따라해! 놀이터':
        return render_template('1.html')
    elif game_name == '잡아라! 두더지':
        return render_template('2.html')
    elif game_name == '맞춰라! 색종이':
        quiz = quiz_data[0]  # 첫 번째 퀴즈 로드 (향후 로직 개선 가능)
        return render_template('3.html', game=game_data[game_name], quiz_image=quiz['image'])  # , quiz_data=json.dumps(quiz_data)
    else:
        return "Game not found", 404


###########################
########## game1 ##########
###########################

# 게임 화면에 들어갈 mediapipe 비디오
@app.route('/game1_feed')
def game1_feed():
    return Response(game1_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/send_game1')
def send_game1():
    stage, quit = get_data_1()
    return jsonify({
        'stage': stage,
        'quit': quit
    })


###########################
########## game2 ##########
###########################

@app.route('/game2_feed')
def game2_feed():
    return Response(game2_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/send_game2')
def send_game2():
    time, stage, score, question, quit = get_data_2()
    return jsonify({
        'time': time,
        'stage': stage,
        'score': score,
        'question': question,
        'quit': quit
    })


###########################
########## game3 ##########
###########################

@app.route('/capture', methods=['POST'])
def capture_image():
    data = request.get_json()
    img_data = data['image']
    img_data = img_data.split(",")[1]
    img = Image.open(BytesIO(base64.b64decode(img_data)))
    predicted_class, predicted_prob = predict_image(img)
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

@app.route('/survey1', methods=['GET', 'POST'])
def survey1():
    if request.method == 'POST':
        data = request.get_json()
        feedback = data.get('feedback')

        # 서버 콘솔에 데이터 출력
        print(f"Received feedback: {feedback}")

        return jsonify({'status': 'success', 'feedback': feedback})
    return render_template('survey1.html')

@app.route('/survey2', methods=['GET', 'POST'])
def survey2():
    if request.method == 'POST':
        data = request.get_json()
        feedback = data.get('feedback')

        # 서버 콘솔에 데이터 출력
        print(f"Received feedback: {feedback}")

        return jsonify({'status': 'success', 'feedback': feedback})
    return render_template('survey2.html')

@app.route('/survey3', methods=['GET', 'POST'])
def survey3():
    if request.method == 'POST':
        data = request.get_json()
        feedback = data.get('feedback')

        # 서버 콘솔에 데이터 출력
        print(f"Received feedback: {feedback}")

        return jsonify({'status': 'success', 'feedback': feedback})
    return render_template('survey3.html')


if __name__ == '__main__':
    app.run(debug=True)