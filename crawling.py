#!/usr/bin/python

#-*- coding: utf-8 -*-

import re
import requests
import numpy
import math
import time
from nltk import word_tokenize
from bs4 import BeautifulSoup

word_d = {}		#all words of URLs
sent_list = []	#crawling word lists per URL

# remove unique character
def hfilter(s):
	return re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》\u00a9]', '', s)

# crawling url
def crawling(url):
	res = requests.get(url)

	soup = BeautifulSoup(res.content, "html.parser")
	script_tag = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'a', 'td'])

	sentences=[]    #remove html tag
	for script in script_tag:
		text = re.sub('[\t\n]', '', script.get_text())
		sentences.append(text)

	process_new_sentence(sentences)


# save sentences to sent_list
def process_new_sentence(sentences):
	#make filterd sentences to list
	tokenized=[]
	for sen in sentences:
		filteredSen = hfilter(sen)
		for word in word_tokenize(filteredSen):
			if(word.isalpha()):
				tokenized.append(word)

	#save sentence list of URL
	sent_list.append(tokenized)

	#make words dictionary
	for word in tokenized:
		if word not in word_d.keys():
			word_d[word] = 0
		word_d[word] += 1

	#for debug
	#	for key, value in word_d.items():
	#		print(key, value )


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
	# make vector
	v1 = make_vector(words1)
	v2 = make_vector(words2)

	#calculate Cosine Similarity
	dotpro = numpy.dot(v1, v2)
	cossimil = dotpro / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

	return cossimil

#get similarity top3 of url
def similarity_url(index):
	sim = {}

	for i in range(0, len(sent_list)):
		if(i != index):
			sim[i] = cal_Cossimil(index, i)

	sorted_sim = sorted(sim.items(), key=lambda x:x[1], reverse=True)
	sorted_sim = sorted_sim[:3]

	sim = dict(sorted_sim)
	
	return sim

	



def compute_idf():
	Dval = len(sent_list)	#num of url
	bow = set()				#build set of words

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

def cal_tf_idf(senlist):
	tf_idf = {}

	idf_d = compute_idf()

	tf_d = compute_tf(senlist)
	for word, tfval in tf_d.items():
		tf_idf[word] = tfval * idf_d[word]
		#print(word, tf_idf)
	#print("")

	#select Top10
	sorted_tfidf = sorted(tf_idf.items(), key=lambda x:x[1], reverse=True)
	sorted_tfidf = sorted_tfidf[:10]
	tf_idf = dict(sorted_tfidf)
	
	return tf_idf




if __name__ == '__main__':
	
	urls = [u'http://groovy.apache.org/' , u'http://skywalking.apache.org/', 
			u'http://allura.apache.org/' , u'http://knox.apache.org/', 
			u'http://whimsical.apache.org/']

	i=0
	for url in urls:
		start = time.time()
		crawling(url)
		cTime = round(time.time() - start, 5)
		print(url)
		print("크롤링 시간	:" , cTime, "	단어 수 : ", len(sent_list[i]))
		i += 1

	print("=============================================")


	for i in range(0, len(sent_list)):
		print( i, "번 url과 유사한 top3")
		sim = similarity_url(i)		#url인덱스:유사도 정렬된 top3 딕셔너리
		for key in sim:
			print(urls[key])
		print("-------------------------------------------")	
			
	
	print("============================================")
	for i in range(0, len(sent_list)):
		print( i , "번째 url의 top10 단어")
		word = cal_tf_idf(sent_list[i])		#단어:tfidf값 정렬된 top10 딕셔너리
		for key in word:
			print(key)

	




