from flask import Flask,jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return 'hello'


@app.route('/news', methods = ['GET'])
def get_news():
    return jsonify(title='text')


