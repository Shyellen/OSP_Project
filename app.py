from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save('./uploads/' + secure_filename(f.filename))
        return 'success'
    return 'file uploading failed'

@app.route('/urlSending', methods=['GET', 'POST'])
def text_recv():
    if request.method == 'POST':
        inTXT = request.form['url']
        return(inTXT)
    return("url receiving failed")
