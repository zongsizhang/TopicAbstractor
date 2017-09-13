"""
documents.py
Created by Zongsi Zhang, 09/12/2017
"""
import copy
import math
import operator

class Document(object):
	"""
	One Document correspondes to a web page, it stores a dictionary of words' count

	Attributes:
		term_dict: a dictionary records terms and its count in webpage
		links: a list of url current page point out to
	"""
	def __init__(self, term_list, links=[]):
		""" constructor
		instantiate a Document with a term_list to be converted into dict
		Args:
			term_list: A list of str
			links: A list of str

		Returns: None

		Raises:
			TypeError: raise when parameter type not match
		"""
		# do type check
		if not isinstance(term_list, list):
			raise TypeError('term_list must be of type list')
		if not isinstance(links, list):
			raise TypeError('links must be of type list')
		self.term_dict = {x: term_list.count(x) for x in term_list}
		self.links = copy.deepcopy(links)

	def __init__(self, t_dict, links=[]):
		""" constructor
		instantiate a Document with a dict of word count
		Args:
			t_dict: A dict of word count
			links: A list of str

		Returns: None

		Raises:
			TypeError: raise when parameter type not match
		"""

		# do type check
		if not isinstance(t_dict, dict):
			raise TypeError('t_dict must be of type dict')
		if not isinstance(links, list):
			raise TypeError('links must be of type list')
		self.term_dict = copy.deepcopy(t_dict)
		self.links = copy.deepcopy(links)

	def set_links(self, links):
		""" set links
		Args:
			links: A list of str

		Returns: None

		Raises:
			TypeError: raise when parameter type not match
		"""
		if not isinstance(links, list):
			raise TypeError('links must be of type list')
		self.links = copy.deepcopy(links)

class DocumentSet(object):
	""" DocumentSet
	Document set hold the the document set around the web page that is to be analyzed.
	Attributes:
		self.main_doc : page to be analized
		self.env_docs : list of environment docs, environment docs are docs for pages linked by main page
	"""

	def __init__(self, main_doc):
		""" init
		Construct a DocumentSet with main document

		Args:
			main_doc: Document object of main page

		Returns: None

		Raises:
			TypeError: raise when parameter type not match

		"""
		if not isinstance(main_doc, Document):
			raise TypeError('term must be of type Document')
		self.main_doc = main_doc
		self.env_docs = []

	def add_env_page(self, env_page):
		""" Add Env Page
		append a new env_page to env_docs

		Args:
			env_page: a Document object of envrionment pages

		Returns: None

		Raises:
			TypeError: raise when parameter type not match

		"""
		if not isinstance(env_page, Document):
			raise TypeError('env_page must be of type Document')
		self.env_docs.append(env_page)

	def __count_term_in_env(self, term):
		""" Count term in environment

		calculate idf of a term in main doc

		Args:
			term: a str

		Returns: double value of idf

		Raises:
			TypeError: raise when parameter type not match

		"""

		# type check
		if not isinstance(term, str):
			raise TypeError('term must be of type str')

		total_cnt = float(len(self.env_docs)) + 1.0
		if total_cnt == 1.0:
			return 1.0
		cnt = 1.0
		for doc in self.env_docs:
			if term in doc.term_dict:
				cnt += 1.0
		return math.log(total_cnt / cnt) 

	def statistic_tf(self, pick_num = 20):
		""" Statistic TF

		calculate and sort terms in main doc by tf

		Args: None

		Returns: a dictionary in descending order of values

		Raises:

		"""
		return sorted(self.main_doc.term_dict.items(), key=operator.itemgetter(1), reverse=True)

	def statistic_tfidf(self, pick_num = 20):
		""" Statistic TF-IDF

		calculate and sort terms in main doc by tf-idf

		Args: None

		Returns: a dictionary in descending order of values

		Raises:

		"""
		# calculate df-idf for all words
		count_dict = {x: self.main_doc.term_dict[x] * self.__count_term_in_env(x) for x in self.main_doc.term_dict}
		# sort them by df and idf
		return sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)
