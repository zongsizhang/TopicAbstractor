"""
topicproducer.py
Created by Zongsi Zhang, 09/12/2017
"""
import grequests
import nltk
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import defaultdict
from collections import Iterable
from documents import Document
from documents import DocumentSet
from nltk.corpus import wordnet
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import string
from time import sleep
import threading

class TermProducer(object):
	""" TermProducer

	A Util class take use of beautifulsoup and NLTK to parse webpage and do nlp process

	Attributes:
		__weburl : the url of page to be handled
		__dindex : depth of link out to build environment, set to 0 to 
	"""

	def __init__(self, dindex):
		""" init

		instantiate a TermProducer object with the depth of link out

		Args:
			dindex : int number represents depth of link out to env docs

		Returns: None

		Raises:

		"""
		# do parameter check
		if not isinstance(dindex, int):
			raise TypeError('dindex must be of type int')
		if not dindex >= 0:
			raise ValueError('dindex must be no less than 0')

		self.__dindex = dindex
		self.__tag_filter = ['style', 'script', 'head', 'media', 'meta', '[document]', 'href', 'link']

	def build_word_list(self, texts, stop_words = set(nltk.corpus.stopwords.words('english')), puncts = set(string.punctuation), stemmer = SnowballStemmer('english'), stemverb=False):
		""" init

		instantiate a TermProducer object with the depth of link out

		Args:
			texts: raw texts get from web page
			stop_words: a set str represents stop words
			puncts: a set of str represents puncts
			stemmer: a nltk stemmer to stem words
			stemverb: a bool that determine if stem words, stemming verb will lead to much more time costs

		Returns: a stemmed word list

		Raises:

		"""
		# type check
		if not isinstance(texts, str):
			raise TypeError("texts must be of type str")
		if not isinstance(stop_words, Iterable):
			raise TypeError('stop_words must be iterable')
		if not  isinstance(puncts, Iterable):
			raise TypeError('puncts must be iterable')
		# remove redundant space, remove words with puncts and numerics
		words = list(filter( lambda w : w != None and len(w) > 1 and not w.isdigit() and all((c not in puncts or c is '-') for c in w) , texts.split() ))
		# stem words using nltk stemmer and encode to utf-8 to skip 'u prefix
		tokens = list(map( lambda w : stemmer.stem(w.lower()).encode('utf-8'), words ))
		# stem verbs
		if stemverb:
			tokens = [WordNetLemmatizer().lemmatize(w,'v').encode('utf-8') for w in tokens]
		# remove stop words
		tokens = list(filter( lambda w : not w in stop_words , tokens))
		return tokens

	def set_custom_tag_filter(filters):
		""" Set Custom Tag Filter

		add more customized filters of tags for specific websites

		Args:
			filters: list of str

		Returns: None

		Raises:
			TypeError: raise when parameter type not match
		"""
		# type check
		if not isinstance(filters, list) or not all(isinstance(x, str) for x in filters):
			raise TypeError('filters must be a list of str')

		self.__tag_filter.append(filters)

	def __tag_visible(self, e):
		""" Tag Visible

		check if this element is visible to web browser user

		Args:
			e : an element of xml tree

		Returns: a boolean value whether this element is classified visible

		Raises:
			ValueError: raise when Parameter value not correct
		"""
		if e is None:
			raise ValueError('e must not be none')
		return e.parent.name not in self.__tag_filter and not isinstance(e, Comment)

	def __url_filter(self, input):
		""" URL Filter

		filter out links that we have no interests

		Args:
			input: a str of url

		Returns: a boolean whether is true or not

		Raises:
			ValueError: raise when Parameter value not correct
		"""
		return input.startswith('http')

	def __parse_to_doc(self, content, cur_depth, depth):
		""" Parse to Doc

		parse the content of webpage and return a Document object

		Args:
			content: content of webpage
			cur_depth: int value of current depth of out link
			depth: int value of max depth of out link

		Returns: a Document object

		Raises:
			TypeError: raise when parameter type not match
			ValueError: raise when parameter value not correct
		"""
		if not isinstance(cur_depth, int):
			raise TypeError('cur_depth must be of type int')
		if not isinstance(depth, int):
			raise TypeError('depth must be of type int')
		if cur_depth > depth:
			raise ValueError('cur_depth must be no larger than depth')
		# build soup parser
		soup = BeautifulSoup(content, 'lxml')
		# remove links to other resource files
		for e in soup.find_all('link'):
			e.extract()
		# get word list of title
		title_content = str(soup.find_all('title'))
		# get word list of body
		page_content = ''
		if not soup.body is None:
			page_content = str(soup.body.find_all(text=self.__tag_visible))
		# build word dict
		t_dict = {x: page_content.count(x) for x in self.build_word_list(page_content)}
		# by default, set tf of title to the maximum counts of words in body
		max_count = 1
		if len(t_dict) is not 0:
			max_count = max(t_dict.values())

		for word in self.build_word_list(title_content):
			t_dict[word] = max_count
		doc = Document(t_dict)

		# if cur_depth < depth, continue psarsing to next level of link tree
		if cur_depth < depth:
	        # leave for extension to environment
			link_elements = list(filter(lambda a : a.has_attr('href'), soup.find_all('a') ))
			#extract all links from current page
			links = list(map( lambda a : a['href'], link_elements ))
			# filter not useful pages
			links = list(filter( self.__url_filter , links ))
			# set links of doc
			doc.set_links(links)
		return doc

	lock = threading.Lock()

	def build_env_docs(self, content, cur_depth, depth, env_docs):
		""" Build Env Docs

		a thread safe function that parse content of page and append document to docset.env_docs

		Args:
			content: text content of web page
			cur_depth: int value of current depth of out link
			depth: int value of max depth of out link
			env_docs: the env_docs object to be appended

		Returns: None

		Raises:
			TypeError: raise when parameter type not match
			ValueError: raise when parameter value not correct
		"""
		# type check
		if not isinstance(env_docs, list):
			raise TypeError('env_docs must be of type list')
		if not isinstance(cur_depth, int):
			raise TypeError('cur_depth must be of type int')
		if not isinstance(depth, int):
			raise TypeError('depth must be of type int')
		if cur_depth > depth:
			raise ValueError('cur_depth must be no larger than depth')
		doc = self.__parse_to_doc(content, cur_depth, depth)
		TermProducer.lock.acquire()
		try:
			env_docs.append(doc)
		finally:
			TermProducer.lock.release()

	def build_doc_set(self, aurl, max_env_size=50):
		""" build Document Set

		Take an url and build a documentset for it

		Args:
			aurl: str, url of the page to be parsed
			max_env_size: int, maximum number of out link pages to be parsed, set to avoid too many pages costs too much time

		Returns: A DocumentSet object

		Raises:
			TypeError: raise when parameter type not match
		"""
		# do parameter check
		if not isinstance(aurl, str):
			raise TypeError('aurl must be of type str')
		if not isinstance(max_env_size, int):
			raise TypeError('max_env_size must be of type int')

		# build main page of doc set
		content = requests.get(aurl, timeout = 3)
		content.raise_for_status()
		docset = DocumentSet(self.__parse_to_doc(content.text, 0, self.__dindex))

		# if depth is zero, don't need to parse environment pages
		if(self.__dindex is 0):
			return docset
		'''
		start building env pages
		'''
		tovisit = docset.main_doc.links[:max_env_size]
		rs = (grequests.get(u) for u in tovisit)
		threads = []
		# use grequest to parallelly retrieve pages
		for response in grequests.map(rs):
			if not response is None:
				thread = threading.Thread(target=self.build_env_docs, args=(response.content, 1, 1, docset.env_docs))
				threads.append(thread)

		# start and join threads to make sure results correct
		for t in threads:
			t.start()

		for t in threads:
			t.join()
		
		return docset
		





