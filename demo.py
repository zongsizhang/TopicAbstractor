from topicproducer import TermProducer
from topicproducer import DocumentSet

p = TermProducer(1)
docset = p.build_doc_set('http://www.ebay.com/itm/BATH-BODY-WORKS-PUMPKIN-CUPCAKE-SCENTED-CANDLE-3-WICK-14-5-OZ-LARGE-FROSTING/122577295273')
print docset.statistic_tfidf()
