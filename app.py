from flask import Flask
from flask import render_template
from flask import request
import requests
import time
from bs4 import BeautifulSoup

app = Flask(__name__)
total_result = []


def crawling(url):
    res = requests.get(url)
    html = BeautifulSoup(res.content, "html.parser")

    for rm in html(["script", "style"]):
        rm.extract()

    sentences = html.get_text()
    sentences = sentences.lower()
    sentences = sentences.replace('\n', ' ')
    sentences = sentences.replace('\t', ' ')

    word = ""
    for c in sentences:
        if c.isalnum():
            word += c
        else:
            word += ' '
    word += ' '
    words = word.split()

    d = dict()
    for w in words:
        if w in d:
            d[w] = d[w] + 1
        else:
            d[w] = 1
    return d, len(words)


def start_crawl(url):
    start = time.time()
    d, size = crawling(url)
    c_time = round(time.time() - start, 5)
    print("크롤링 한 주소:", url)
    print("크롤링 시간:", c_time)
    print("단어 수:", size)
    print("==============================")
    result = [url, c_time, size]
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urlSending', methods=['GET', 'POST'])
def text_recv():
    if request.method == 'POST':
        url_text = request.form['url']
        total_result.append(start_crawl(url_text))
        return str(total_result)
        # return render_template('/result.html', result=total_result)
    return "[ERROR] Url receiving failed."


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url_file = request.form['content']
        urls = url_file.split()
        for url in urls:
            total_result.append(start_crawl(url))
        return str(total_result)
        # return render_template('/result.html', result=total_result)
    return "[ERROR] File uploading failed."
