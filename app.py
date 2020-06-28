from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import urllib.request
import requests
import operator
import numpy
import time
import math


app = Flask(__name__)

es_host = "127.0.0.1"
es_port = "9200"
es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout=30)
es_id = 0

total_result    = []
word_list       = []
word_dict       = {}
url_error_message = "<h1>[ERROR]</h1><h2>Input data is invalid.</h2>" \
                "1. Input may have been added as a duplicate.<br>" \
                "2. Input may not be url.<br>" \
                "3. Input may not be valid."

cnt = -1

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
        if c.isalpha():
            word += c
        else:
            word += ' '
    word += ' '
    words = word.split()

    word_list.append(words)

    for w in words:
        if w not in word_dict.keys():
            word_dict[w] = 0
        word_dict[w] += 1

    return word_list, len(words)


def start_crawl(url):
    global cnt
    start = time.time()
    w_list, size = crawling(url)
    c_time = round(time.time() - start, 5)
    print("==============================")
    print("크롤링 한 주소:", url)
    print("단어 수:", size)
    print("크롤링 시간:", c_time)
    print("==============================")
    cnt += 1
    result = [url, size, c_time, cnt]
    es_data_add(w_list, result)
    return result


def es_data_add(w_list, result):
    global es_id
    data = {
        "url": result[0],
        "size": result[1],
        "crawl_time": result[2],
        "words": w_list
    }
    es_id += 1
    es.index(index='web', doc_type='word', id=es_id, body=data)


def url_validation(url):
    for data in total_result:
        if data[0] == url:
            print("[ERROR] This is a duplicate URL: %s" % url)
            return -1
    try:
        res = urllib.request.urlopen(url)
    except ValueError as err:
        print("[ERROR] This is not an URL: %s" % url)
        return -2
    if res.status != 200:
        print("[ERROR] This is an invalid URL: %s" % url)
        return -3
    return 0


def cal_tf_idf(w_list):
    tf_idf = {}

    idf_d = compute_idf()
    tf_d = compute_tf(w_list)
    for word, tfval in tf_d.items():
        tf_idf[word] = tfval * idf_d[word]

    sorted_tfidf = sorted(tf_idf.items(), key=lambda x:x[1], reverse=True)
    sorted_tfidf = sorted_tfidf[:10]
    tf_idf = dict(sorted_tfidf)

    return tf_idf


def compute_idf():
    Dval = len(word_list)   #num of url
    bow = set()             #build set of words

    for i in range(0, len(word_list)):
        for tok in word_list[i]:
            bow.add(tok)
    
    idf_d = {}
    for t in bow:
        cnt = 0
        for s in word_list:
            if t in s:
                cnt += 1
        idf_d[t] = float(math.log(Dval / cnt))

    return idf_d


def compute_tf(w_list):
    bow = set()
    wordcount_d = {}

    for tok in w_list:
        if tok not in wordcount_d.keys():
            wordcount_d[tok] = 0
        wordcount_d[tok] += 1
        bow.add(tok)

    tf_d = {}
    for word, count in wordcount_d.items():
        tf_d[word] = float( count / len(bow))

    return tf_d

def similarity_url(url_index):
    sim = {}
    for i in range(0, len(word_list)):
        if i != url_index:
            sim[i] = cal_Cossimil(url_index, i)

    sorted_sim = sorted(sim.items(), key=lambda x:x[1], reverse=True)
    sorted_sim = sorted_sim[:3]
    sim = dict(sorted_sim)
    print(sim)

    return sim


def cal_Cossimil(words1, words2):
    v1 = make_vector(words1)
    v2 = make_vector(words2)

    dotpro = numpy.dot(v1, v2)
    cossimil = float(dotpro / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2)))

    return cossimil


def make_vector(i):
    v = []
    s = word_list[i]
    for w in word_dict.keys():
        val = 0
        for t in s:
            if t == w:
                val += 1
        v.append(val)
    return v


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urlSending', methods=['GET', 'POST'])
def text_recv():
    if request.method == 'POST':
        url_text = request.form['url']
        if url_validation(url_text) == 0:
            total_result.append(start_crawl(url_text))
            return render_template('result.html', result=total_result)
    return url_error_message


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url_file = request.form['content']
        urls = url_file.split()
        for url in urls:
            if url_validation(url) == 0:
                total_result.append(start_crawl(url))
        return render_template('result.html', result=total_result)
    return url_error_message


@app.route('/get_similarity', methods=['GET', 'POST'])
def sim_cal():
    if request.method == 'POST':
        target = int(request.form['url_j'])
        sim_list = []
        sim_st = ""
        sim = similarity_url(target)
        for key in sim:
            sim_list.append(total_result[key][0])
        print(sim_list)
        sim_st = "  ".join(sim_list)
        return render_template('result.html', sim_result=sim_st)
    return "Similarity Error"


@app.route('/get_tfidf', methods=['GET', 'POST'])
def tfidf_cal():
    if request.method == 'POST':
        target = int(request.form['url_i'])
        tfidf_list = []
        tfidf_st = ""
        word = cal_tf_idf(word_list[target])
        for key in word:
            tfidf_list.append(key)
        print(tfidf_list)
        tfidf_st = "  ".join(tfidf_list)
        return render_template('result.html', tfidf_result=tfidf_st)
    return "tfidf Error"
