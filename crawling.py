#!/usr/bin/python

#-*- coding: utf-8 -*-

import re
import requests
import numpy
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
def calCossimil(v1, v2):
	# make vector
	v1 = make_vector(0)
	v2 = make_vector(1)

	#calculate Cosine Similarity
	dotpro = numpy.dot(v1, v2)
	cossimil = dotpro / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))
	print("cos similarity = ", cossimil)

if __name__ == '__main__':
	
	url1 = u'http://groovy.apache.org/' 
	url2 = u'http://skywalking.apache.org/'

	crawling(url1)
	crawling(url2)

	calCossimil(0, 1);








