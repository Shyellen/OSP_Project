from flask import Flask, render_template, request
import requests
import time
import operator
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

es_host = "127.0.0.1"
es_port = "9200"
es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout=30)
es_id = 0

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
    size = 0
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
    print("==============================")
    print("크롤링 한 주소:", url)
    print("단어 수:", size)
    print("크롤링 시간:", c_time)
    print("==============================")
    result = [url, size, c_time]
    es_data_add(d, result)
    return result


def es_data_add(word_dict, result):
    global es_id
    word_dict = dict(sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True))
    data = {
        "url": result[0],
        "size": result[1],
        "crawl_time": result[2],
        "words": list(word_dict.keys()),
        "frequencies": list(word_dict.values())
    }
    es_id += 1
    es.index(index='web', doc_type='word', id=es_id, body=data)
    # result = es.search(index='web')
    # print("=========== result ===========")
    # print(result)


def redundancy_check(url):
    for data in total_result:
        if data[0] == url:
            return False
    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urlSending', methods=['GET', 'POST'])
def text_recv():
    if request.method == 'POST':
        url_text = request.form['url']
        if redundancy_check(url_text):
            total_result.append(start_crawl(url_text))
            return render_template('result.html', result=total_result)
    return "<h1>[ERROR]</h1> This is a duplicate URL: %s" % url_text


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url_file = request.form['content']
        urls = url_file.split()
        for url in urls:
            if redundancy_check(url):
                total_result.append(start_crawl(url))
        return render_template('result.html', result=total_result)
    return "[ERROR] Duplicate URL exists. Outputs results except this."
