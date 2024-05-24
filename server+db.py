from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 데이터베이스 연결
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_hana:0701@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)

# Initialize the database
with app.app_context():
    db.init_app(app)
    db.create_all()

nextId = 4
topics = [
    {'id': 1, 'title': 'HTML', 'body': 'HTML is ...'},
    {'id': 2, 'title': 'CSS', 'body': 'CSS is ...'},
    {'id': 3, 'title': 'JavaScript', 'body': 'JavaScript is ...'}
]


def template(contents, content, id=None):
    contextUI = ''
    if id != None:
        contextUI = f'''
            <li><a href="/update/{id}/">update</a><li>
            <li><form action="/delete/{id}/" method="POST"><input type="submit" value="delete"><form></li>
        '''
    return f'''<!doctype html>
    <html>
        <body>
            <h1><a href="/">WEB</a></h1>
            <ol>
                {contents}
            </ol>
            {content}
            <ul>
                <li><a href="/create/">create</a></li>
                {contextUI}
            </ul>
        </body>
    </html>
    '''


def getContents():
    liTags = ''
    for topic in topics:
        liTags = liTags + f'<li><a href="/read/{topic["id"]}/">{topic["title"]}</a></li>'
    
    return liTags


@app.route('/')
def index():
    return template(getContents(), '<h2>Welcome</h2>Hello, Web')


@app.route('/read/<int:id>/')
def read(id):
    title = ''
    body = ''
    for topic in topics:
        if id == topic['id']:
            title = topic['title']
            body = topic['body']
            break

    return template(getContents(), f'<h2>{title}</h2>{body}', id)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method =='GET':
        content = '''
            <form action="/create/" method="POST">
                <p><input type="text" name="title" placeholder="title"></p>
                <p><textarea name="body" placeholder="body"></textarea></p>
                <p><input type="submit" value="create"></p>
            </form>
        '''
        return template(getContents(), content)
    
    elif request.method == 'POST':
        global nextId
        title = request.form['title']
        body = request.form['body']
        newTopic = {'id': nextId, 'title': title, 'body': body}
        topics.append(newTopic)
        url = '/read/' + str(nextId) + '/'
        nextId += 1
        return redirect(url)


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update(id):
    if request.method =='GET':
        title = ''
        body = ''
        for topic in topics:
            if id == topic['id']:
                title = topic['title']
                body = topic['body']
                break
        content = f'''
            <form action="/update/{id}/" method="POST">
                <p><input type="text" name="title" placeholder="title" value="{title}"></p>
                <p><textarea name="body" placeholder="body">{body}</textarea></p>
                <p><input type="submit" value="update"></p>
            </form>
        '''
        return template(getContents(), content)
    
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        for topic in topics:
            if id == topic['id']:
                title = topic['title']
                body = topic['body']
                break
        url = '/read/' + str(id) + '/'
        return redirect(url)
    

@app.route('/delete/<int:id>/', methods=['POST'])
def delete(id):
    for topic in topics:
        if id == topic['id']:
            topics.remove(topic)
            break
    return redirect('/')

@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        # Create example topics
        topics = [
            {'title': 'HTML 기본 구조', 'body': 'HTML 문서의 기본적인 구조와 태그들에 대해 알아봅니다.'},
            {'title': 'CSS 선택자', 'body': 'CSS에서 사용되는 다양한 선택자의 종류와 각각의 역할에 대해 학습합니다.'},
            {'title': 'JavaScript 변수', 'body': 'JavaScript에서 변수를 선언하고 활용하는 방법에 대해 배웁니다.'},
            {'title': 'Python 함수', 'body': 'Python에서 함수를 정의하고 호출하는 방법에 대해 알아봅니다.'}
        ]

        # Add topics to the database
        for topic_data in topics:
            new_topic = Topic(title=topic_data['title'], body=topic_data['body'])
            db.session.add(new_topic)
        db.session.commit()

        return "Example topics added to the database"

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
if __name__ == "__main__":  
    app.run(port=5001, debug=True)