from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from login import save_user, load_users
from game1 import check_frames, generate_frames, get_score, get_position, get_labels_positions
from game3 import predict_image
from PIL import Image
import base64
from io import BytesIO

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
    '이미지 퀴즈쇼': {
        'title': '이미지 퀴즈쇼',
        'image': 'game1.png',
        'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.'
    }
}


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
    if game_name == '그림자 놀이터':
        position, image_info = get_position()
        return render_template('1.html', game=game_data[game_name], score=get_score(), position=position, image_info=image_info)
    elif game_name == '두더지 잡기':
        return render_template('2.html')
    elif game_name == '이미지 퀴즈쇼':
        return render_template('3.html', game=game_data[game_name])
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




if __name__ == '__main__':
    app.run(debug=True)