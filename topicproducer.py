"""
topicproducer.py
Created by Zongsi Zhang, 09/12/2017
"""
import copy
import nltk
import math
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import defaultdict
from collections import Iterable
from nltk.corpus import wordnet
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import operator
import string
from time import sleep

class Document(object):
	"""
	Init document with a abstracted termlists, it will count all terms and make it a dictionary for future query
	"""
	def __init__(self, term_list, links=[]):
		if not isinstance(term_list, list):
			raise TypeError('term_list must be of type list')
		if not isinstance(links, list):
			raise TypeError('links must be of type list')
		self.term_dict = {x: term_list.count(x) for x in term_list}
		self.links = copy.deepcopy(links)

	def set_links(self, links):
		if not isinstance(links, list):
			raise TypeError('links must be of type list')
		self.links = copy.deepcopy(links)

	def get_count(self, term):
		if not isinstance(term, str):
			raise TypeError('term must be of type str')
		return self.term_dict.get(term, 0)

class DocumentSet(object):
	"""
	Document set hold the the document set around the web page that is to be analyzed.
	self.main_doc : page to be analized
	self.env_docs : envriontpages
	"""

	def __init__(self, main_page):
		if not isinstance(main_page, list):
			raise TypeError('main_page must be of type list')
		self.main_doc = Document(main_page)
		self.env_docs = []

	def __init__(self, main_doc):
		if not isinstance(main_doc, Document):
			raise TypeError('term must be of type str')
		self.main_doc = main_doc
		self.env_docs = []

	def add_env_page(self, env_page):
		self.env_docs.append(env_page)

	def __count_term_in_env(self, term):
		total_cnt = float(len(self.env_docs)) + 1.0
		if total_cnt == 1.0:
			return 1.0
		cnt = 1.0
		for doc in self.env_docs:
			if term in doc.term_dict:
				cnt += 1.0
		return math.log(total_cnt / cnt) 

	def statistic_tf(self):
		return sorted(self.main_doc.term_dict.items(), key=operator.itemgetter(1), reverse=True)

	def statistic_tfidf(self):
		# calculate df-idf for all words
		count_dict = {x: self.main_doc.term_dict[x] * self.__count_term_in_env(x) for x in self.main_doc.term_dict}
		# sort them by df and idf
		return sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)

class TermProducer(object):
	"""
	A Util class take use of beautifulsoup and NLTK to parse webpage and do nlp process
	__weburl : the url of page to be handled
	__dindex : depth of link out to build environment, set to 0 to 
	"""
	def __init__(self, __dindex):
		self.__dindex = __dindex
		self.__tag_filter = ['style', 'script', 'head', 'media', 'meta', '[document]', 'href']

	def build_word_list(self, texts, stop_words = set(nltk.corpus.stopwords.words('english')), puncts = set(string.punctuation), stemmer = SnowballStemmer('english')):
		# remove redundant space, remove words with puncts
		words = list(filter( lambda w : w != 'None' and len(w) != 0 and all((c not in puncts or c == '-') for c in w) , texts.split() ))
		# stem words using nltk stemmer and encode to utf-8 to skip 'u prefix
		tokens = list(map( lambda w : stemmer.stem(w.lower()).encode('utf-8'), words ))
		# stem verbs
		tokens = [WordNetLemmatizer().lemmatize(w,'v').encode('utf-8') for w in tokens]
		# remove stop words
		tokens = list(filter( lambda w : not w in stop_words , tokens))

		return Document(tokens)

	def set_custom_tag_filter(filters):
		self.__tag_filter.append(filters)

	def __tag_visible(self, e):
		return e.parent.name not in self.__tag_filter and not isinstance(e, Comment)

	def __url_filter(self, input):
		return input.startswith('http') and not input.endswith('home')

	def __parse_to_doc(self, aurl, cur_depth, depth):
		if not isinstance(aurl, str):
			raise TypeError('aurl must be of type str')
		if not isinstance(cur_depth, int):
			raise TypeError('cur_depth must be of type int')
		if not isinstance(depth, int):
			raise TypeError('depth must be of type int')
		if cur_depth > depth:
			raise ValueError('cur_depth must be no larger than depth')
		content = requests.get(aurl, timeout = 5)
		content.raise_for_status()
		soup = BeautifulSoup(content.text, 'lxml')
		page_content = str(soup.html.find_all(text=self.__tag_visible))
		doc = self.build_word_list(page_content)
		# if cur_depth < depth, continue psarsing to next level of link tree
		if cur_depth < depth:
	        # leave for extension to environment
			link_elements = list(filter(lambda a : a.has_attr('href'), soup.find_all('a') ))
			#extract all links from current page
			links = list(map( lambda a : a['href'], link_elements ))
			# filter not useful pages
			links = list(filter( self.__url_filter , links ))
			# filter itself
			links = list(filter( lambda link : link != aurl , links ))
			doc.set_links(links)
		return doc

	def build_doc_set(self, aurl):
		# do parameter check
		if not isinstance(aurl, str):
			raise TypeError('aurl must be of type str')

		# build main page of doc set
		docset = DocumentSet(self.__parse_to_doc(aurl, 0, self.__dindex))
		tovisit = docset.main_doc.links
		for link in tovisit:
			sleep(3)
			docset.add_env_page(self.__parse_to_doc(link,1,self.__dindex))
		return docset
		





