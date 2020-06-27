from flask import Flask
from flask import render_template
from flask import request
import requests
import time
import re
import numpy
import math
from nltk import word_tokenize
from bs4 import BeautifulSoup

app = Flask(__name__)
total_result = []	# html로 리턴할 결과
sent_list = []		# url 별로 생성된 단어들 묶어놓음.
word_d = {}			# 모든 url에서 나온 단어들(단어,개수 딕셔너리)

def cal_tf_idf(senlist):
    tf_idf = {}

    idf_d = compute_idf()
    tf_d = compute_tf(senlist)
    for word, tfval in tf_d.items():
        tf_idf[word] = tfval * idf_d[word]

    #select Top10
    sorted_tfidf = sorted(tf_idf.items(), key=lambda x:x[1], reverse=True)
    sorted_tfidf = sorted_tfidf[:10]
    tf_idf = dict(sorted_tfidf)

    return tf_idf

def compute_idf():
    Dval = len(sent_list)   #num of url
    bow = set()             #build set of words

    for i in range(0, len(sent_list)):
        for tok in sent_list[i]:
            bow.add(tok)

    idf_d = {}
    for t in bow:
        cnt = 0
        for s in sent_list:
            if t in s:
                cnt += 1
            if cnt == 0:
                idf_d[t] = 0
            else:
                idf_d[t] = float(math.log(Dval / cnt))

    return idf_d

def compute_tf(senlist):
    bow = set()
    wordcount_d = {}

    for tok in senlist:
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
    for i in range(0, len(sent_list)):
        if(i != url_index):
            sim[i] = cal_Cossimil(url_index, i)

    sorted_sim = sorted(sim.items(), key=lambda x:x[1], reverse=True)
    sorted_sim = sorted_sim[:3]
    sim = dict(sorted_sim)

    return sim

#return vector for cosine similarity
def make_vector(i):
    v = []
    s = sent_list[i]
    for w in word_d.keys():
        val = 0
        for t in s:
           if t==w:
                val += 1
        v.append(val)
    return v

# calculate Cosine Similarity
def cal_Cossimil(words1, words2):
    v1 = make_vector(words1)
    v2 = make_vector(words2)

    dotpro = numpy.dot(v1, v2)
    cossimil = dotpro / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

    return cossimil

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

    l = []
    for w in words:
        if w in word_d.keys():
            word_d[w] = word_d[w] + 1
        else:
            word_d[w] = 1
            l.append(w)
    sent_list.append(l)

    return len(words)


def start_crawl(url):
    start = time.time()
    size = crawling(url)
    c_time = round(time.time() - start, 5)
    print("크롤링 한 주소:", url)
    print("크롤링 시간:", c_time)
    print("단어 수:", size)
    print("==================================")
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
        # return str(total_result)
        return render_template('result.html', result=total_result)
    return "[ERROR] Url receiving failed."


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url_file = request.form['content']
        urls = url_file.split()
        for url in urls:
            total_result.append(start_crawl(url))
        print(total_result)
        print("===========================================")
		
        l1=[]
        l2=[]
        total_result2=[]
        for i in range(0, len(sent_list)):
            sim = similarity_url(i)
            for key in sim:
                l1.append(urls[key])
       
            word = cal_tf_idf(sent_list[i])
            for key in word:
                l2.append(key)

            total_result2.append([l1, l2])
            l1 = []
            l2 = [] 

        print(total_result2)
           

        # return str(total_result)
        return render_template('result.html', result=total_result, total_result2)
    return "[ERROR] File uploading failed."
