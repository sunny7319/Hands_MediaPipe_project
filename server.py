from flask import Flask, render_template, Response


app = Flask(__name__)


@app.route('/')
def index():
    # return 'random : <strong>'+str(random.random())+'</strong>'
    return render_template('game.html')

if __name__ == '__main__':
    app.run(debug=True)
