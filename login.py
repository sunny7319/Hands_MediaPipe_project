import json
import os


# 저장된 사용자 정보를 담은 파일 경로
USER_DATA_FILE = 'users.json'

# 사용자 정보를 파일에 저장하는 함수
def save_user(username):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            users = json.load(file)
    else:
        users = []

    # 사용자명이 이미 존재하는지 확인
    if any(user['username'] == username for user in users):
        return False
    
    # 새로운 사용자 ID 생성
    new_id = get_next_id(users)
    new_user = {'id': new_id, 'username': username}
    users.append(new_user)
    
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)
    
    return True

# 사용자 정보를 파일에서 불러오는 함수
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return []

# 고유한 사용자 ID를 생성하는 함수
def get_next_id(users):
    if not users:
        return 1
    max_id = max(user['id'] for user in users)
    return max_id + 1