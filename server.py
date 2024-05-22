from flask import Flask
import random
from flask import request

app = Flask(__name__)


topics = [
    {'id': 1, 'title': 'HTML', 'body': 'HTML is ...'},
    {'id': 2, 'title': 'CSS', 'body': 'CSS is ...'},
    {'id': 3, 'title': 'JavaScript', 'body': 'JavaScript is ...'}
]


def template(contents, content):
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

    return template(getContents(), f'<h2>{title}</h2>{body}')


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
        title = request.form['title']
        body = request.form['body']
        return title + ',' + body




app.run(port=5001, debug=True)