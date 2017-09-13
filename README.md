# Topic Extractor

## Term Definition

- main page: page content get from url
- environment pages: page contents get from links within main page
- main doc: document created from main page
- environment docs: documents created from environment pages


## File Structure

- documents.py : Module with data structures that holding tokenization results of page content
- topicproducer.py : Module with a utility class that read and parse page contents
- picker.py : demo of how this project works

## Usage

In picker.py I wrote a fnction named pickTerm. This is a sampe about how to call the topicproducer and how to manipulate DocumentSet. 

To run picker.py, please enter two arguments, the url and functions to rank.

There are two func_name ready to use

"tf" mode will just count the term frequency of this page

"tfidf" mode will parse all linked out pages as document set and calculate tf-idf, so it's slow even though I've made all tasks done parallel. Now I set maximam environment document number to 50 and not open to be modified.

```shell
python picker.py 'http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/' 'tf'
```

## Design

### Why tf-idf

For a single page, we can only calculate its term frequency, this works for content poviders like CNN because a term with high frequency implies that it may be what the whole text is talking about. But for websites like Amazon and ebay, they have many repeated terms like 'ship', 'discount'. This type of words will exist in most pages of such site. So if we grab the pages the main page point to, we can calculate tf-idf for every words, and the rank those common words will be highly reduced.

### How to determine usable texts

General solution is to filter elements with tags like 'script' and 'style'. But according to my experiment, beautifulsoup is so strong that it will also grab contents of other resources like .css and .js file. Contents of this files can't be filtered by soupt.find_all, so I directly removed elements with tag name 'link'.

### weight of title

I consider title as the most important in tf calculation, so after counting words in body, I merge words in title into body with counts same as the maximum count in body word list. 

### multithreading

To deal with the time cost of parsing multiple pages, I take use of multi thread. I use a lock to guarantee concurrency of the list of environment documents and I take use of *grequests* to do content retreving work parallelized.

### Code Structure
Every time I design program, I try to make it as open to extension as possible. So I detached the logic of crawler and statistic works.

Since the logic of TopicProducer and DocumentSet is departed, DocumentSet can take input from any source and its statistic functions still works.

The responsibility of TopicProucer is to take url and parse it into a set of Documents. So it does http request, parsing, and natural language processing work. It will be better to detach nlp logics from it, since my nlp logic is simple now, I just make it a built-in function.

The responsibility of DocumentSet is to keep main and environment doc and do computation on them to get statistic results.

### Work flow (before statistic work)

1. parse content

	1.1 request main page

	1.2 use beautifulsoup to build xml tree

	1.3 delete elements of tag 'link'

	1.4 pour soup into a str with a filter that rejects specific filters(filters can be customized)

	1.5 send word to 2. npl logics

	1.6 if links needs to be parsed, parse and save into Document.links, go to 1.7. else end

	1.7 grab all links main page has, take first max_env_size links and fetch their content

	1.8 For every page, start a a thread from 1. parse content

	1.9 Make sure every thread done, return doc set.

2. npl logics

	2.1 in one itrate, split the big text into words, do trim on every word, filter words with only puncts and numberics.

	2.2 do stemming work, if stemverb set True, do extra stemming work on verbs

	2.3 remove stop words

	2.4 return word list

### Experiments

Take a page of ebay item as example. We pick top 20 terms

Url of this page is: http://www.ebay.com/itm/Free-People-Amelia-Purple-Mock-Neck-Mini-Dress-Size-XS-NWT-MSRP-118-OB536553/232471228501

With tf, we get following result:

[('nwt', 77), ('bid', 77), ('size', 77), ('purpl', 77), ('ob536553', 77), ('xs', 77), ('peopl', 77), ('amelia', 77), ('msrp', 77), ('mini', 77), ('dress', 77), ('mock', 77), ('neck', 77), ('el', 71), ('win', 38), ('open', 29), ('new', 28), ('window', 27), ('item', 24), ('ship', 22)]

With tf-idf, we get following result:

[('el', 275.2277942907028), ('ob536553', 215.32421414827243), ('nwt', 193.46037664193705), ('amelia', 193.46037664193705), ('msrp', 193.46037664193705), ('mock', 193.46037664193705), ('purpl', 176.50146674205712), ('xs', 176.50146674205712), ('mini', 162.6450284257166), ('win', 153.3411996762487), ('peopl', 140.78119091938123), ('dress', 140.78119091938123), ('neck', 140.78119091938123), ('size', 109.96584270316073), ('window', 55.60563354273235), ('max', 55.04555885814056), ('bidder', 48.580176782465706), ('high', 34.83581580435338), ('bid', 33.084173415596254), ('outbid', 31.454605061794606)]

We can find that in this case it decreases the rank of words like 'open', 'new' and useful words like 'neck', 'size' is promoted.

#### Time consuming:

In the case above, 

tf mode costs 0.810260057449s

tfidf mode costs 13.2314298153s

For tfidf we have 43 more pages to handle, so multi-thread does can optimize effiency.

## Dependencies

ntlk

lxml

beautifulsoup

requests

grequests

## Problems to be solved

1. Brute-force tokenization

In this project I simpy tokenize by split by blanckspace, this will break nominal phrases that may contribute a lot.

2. SSL problem

For some pages I tried, I meet the SSL cerfiticate problem.

4. all in memory

All data is in memory, this will lead to crash if huge number of pages come.









