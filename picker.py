from topicproducer import TermProducer
from topicproducer import DocumentSet
from time import time

def pickTerm(aurl, pick_num=20, func_name='tf'):
	""" Pick Term
	parse page of aurl and pick specific number of tokens according to functions

	Args:
		aurl: a str of url
		pick_num: a int number decide total number of tokens picked
		func_name: name of functions used to rank tokens

	raise:
		TypeError: raise when parameter type not correct
		ValueError: raise when parameter value not correct
	"""
	# type check
	if not isinstance(aurl, str):
		raise TypeError('aurl must be of type str')
	if not isinstance(pick_num, int):
		raise TypeError('pick_num must be of type int')
	if not isinstance(func_name, str):
		raise TypeError('func_name must be of type str')
	# value check
	if pick_num <= 0:
		raise ValueError('pick_num must be grater than 0')

	start = time()

	if func_name is 'tf':
		term_producer = TermProducer(0)
		doc_set = term_producer.build_doc_set(aurl)
		print doc_set.statistic_tf()[:pick_num]
	if func_name is 'tfidf':
		term_producer = TermProducer(1)
		doc_set = term_producer.build_doc_set(aurl)
		print doc_set.statistic_tfidf()[:pick_num]
	end = time()
	print(str(end-start) + 'second')

def main():
	pickTerm('http://www.ebay.com/itm/Free-People-Amelia-Purple-Mock-Neck-Mini-Dress-Size-XS-NWT-MSRP-118-OB536553/232471228501', 20, 'tfidf')

if __name__ == "__main__":
	main()



