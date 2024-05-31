from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from login import save_user, load_users
from game1 import check_frames, generate_frames, get_score, get_position

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
    '산성비': {
        'title': '산성비',
        'image': 'game1.png',
        'description': '제시된 알파벳과 같은 글자를 고르는 게임입니다.'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_info():
    if request.method == 'POST':
        username = request.form['username']
        users = load_users()
        if any(user['username'] == username for user in users):
            return redirect(url_for('main'))
        else:
            error = '아이디를 찾을 수 없습니다.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_info():
    if request.method == 'POST':
        username = request.form['username']
        if save_user(username):
            return redirect(url_for('login'))
        else:
            error = '이미 존재하는 아이디입니다.'
            return render_template('signup.html', error=error)
    return render_template('signup.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/game/<game_name>')
def game(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game.html', game=game_data[game_name])
    else:
        return "Game not found", 404
    
@app.route('/game_play/<game_name>')
def game_play(game_name):
    global game_data
    if game_name in game_data:
        return render_template('game_video.html', game=game_data[game_name], score=get_score(), position=get_position())
    else:
        return "Game not found", 404
    
# 게임 대기화면에 표시할 캠 미리보기
@app.route('/check_video')
def check_video():
    return Response(check_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 게임 화면에 들어갈 mediapipe 비디오
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/get_position')
# def get_position():
#     # 여기서 실시간으로 좌표 데이터를 업데이트
#     global position
#     return jsonify(position)

# toggle 값을 반환하는 엔드포인트 추가
@app.route('/toggle_status')
def toggle_status():
    global toggle
    return jsonify({'toggle': toggle})

if __name__ == '__main__':
    app.run(debug=True)