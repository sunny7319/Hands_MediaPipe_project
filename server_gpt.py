from flask import Flask, request, redirect, render_template

app = Flask(__name__)

nextId = 4
topics = [
    {'id': 1, 'title': 'HTML', 'body': 'HTML is ...'},
    {'id': 2, 'title': 'CSS', 'body': 'CSS is ...'},
    {'id': 3, 'title': 'JavaScript', 'body': 'JavaScript is ...'}
]

def getContents():
    return topics

@app.route('/')
def index():
    return render_template('index.html', topics=getContents())

@app.route('/read/<int:id>/')
def read(id):
    topic = next((topic for topic in topics if topic['id'] == id), None)
    return render_template('read.html', topic=topic, topics=getContents())

@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html', topics=getContents())
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
    topic = next((topic for topic in topics if topic['id'] == id), None)
    if request.method == 'GET':
        return render_template('update.html', topic=topic, topics=getContents())
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        for topic in topics:
            if id == topic['id']:
                topic['title'] = title
                topic['body'] = body
                break
        url = '/read/' + str(id) + '/'
        return redirect(url)

@app.route('/delete/<int:id>/', methods=['POST'])
def delete(id):
    global topics
    topics = [topic for topic in topics if topic['id'] != id]
    return redirect('/')

app.run(port=5001, debug=True)
