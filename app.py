from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urlSending', methods=['GET', 'POST'])
def text_recv():
    if request.method == 'POST':
        url_text = request.form['url']
        return url_text
    return "url receiving failed"


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url_file = request.form['content']
        return url_file
    return "file uploading failed"
