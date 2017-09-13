import sys
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

	if func_name == 'tf':
		term_producer = TermProducer(0)
		doc_set = term_producer.build_doc_set(aurl)
		print doc_set.statistic_tf()[:pick_num]
	elif func_name == 'tfidf':
		term_producer = TermProducer(1)
		doc_set = term_producer.build_doc_set(aurl)
		print doc_set.statistic_tfidf()[:pick_num]
	else:
		print func_name + ' currently not support, please enter tf or tfidf'
	end = time()
	print('\n' + str(end-start) + 'second')

def main():
	if len(sys.argv) != 3:
		raise ValueError('number of arguments should be 2')

	pickTerm(sys.argv[1], 20, sys.argv[2])

if __name__ == "__main__":
	main()



