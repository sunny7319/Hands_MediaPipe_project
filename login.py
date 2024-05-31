from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://pch:1001@127.0.0.1/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    logs= relationship('Log', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return jsonify({'message' : 'Login successful', 'user_id' : user.id}), 200
        else:
            return jsonify({'message' : 'Invalid credentials'}), 401
    except SQLAlchemyError as e:
        return jsonify({'message' : 'An error occured', 'error' : str(e)}), 500
    
@app.route('/current_user', method=['GET'])
def current_user():
    user_id = session.get('user_id')

    if user_id:
        return jsonify({'user_id':user_id}), 200
    else:
        return jsonify({'message' : 'No user logged in'}), 401
    
if __name__ == '__main__':
    db.create_all()
    app.run()
