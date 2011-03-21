# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import csv
# import customserializer # serialize time.struct_time dates in objects to use json.dumps to view
import feedparser
# import json
import nltk
import operator
import re
import urllib2

# Run python harvest.py from the command line

def getwords(html):
    "Returns a list of words from HTML content with the tags stripped out."
    
    # Remove all the HTML tags
    txt = re.compile(r'<[^>]+>').sub('', html)
    
    # Split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    
    # Convert to lowercase
    return [word.lower() for word in words if word != '']

feedlist = [] # a list of feeds read from a file
articles = [] # a list of articles across all feeds

# Crawl RSS feeds to fetch a list of articles for the day.
# Each feed contains only the summary text (first few sentences).
# Therefore, need to use the link attribute in each feed to crawl
# the website and parse the HTML content for text.
# The RSS feed is in effect a useful sitemap of the articles for the day
# instead of attempting to crawl and distinguish all links from the
# home page.

# Read in feeds from a CSV file. Each link is to an RSS feed.
# Just using the NZ Herald National news feed for now
reader = csv.reader(open('feed1.txt', 'rb'), delimiter=",")
for line in reader:
    feedlist.append(line[0])

# Parse the RSS feed
for feed in feedlist:
    try:
        c = urllib2.urlopen(feed)
    except urllib2.URLError:
        print 'Failed to fetch ' + feed

    d = feedparser.parse(c)
    for e in d.entries:
        article = {}
        article['source'] = e.author
        article['title'] = e.title
        article['link'] = e.link
        articles.append(article)

# Parse the full HTML content from the website page referenced by the
# article's link.
for article in articles:
    try:
        page = urllib2.urlopen(article['link'])
    except urllib2.URLError:
        print 'Failed to fetch ' + article['link']

    try:
        soup = BeautifulSoup(page)
    except HTMLParser.HTMLParseError:
        print 'Failed to parse ' + article['link']

    
    wc = {} # a dictonary of word counts by word
    words = getwords(article['title'])
    print "Parsing...%s" % (article['title'])
    article_body = soup.find(True, 'articleBody')
    
    if article_body and len(article_body) > 1:
        content = []
        paras = article_body.findAll('p')
        for p in paras:
            # p.string returns None if there are multiple child elements
            # under the P tag
            for c in p.contents:
                if c.string and len(c.string) > 0:
                    content.append(c.string)
                    words.extend(getwords(c.string))

    for word in words:
        wc.setdefault(word, 0)
        wc[word] += 1
    article['content'] = " ".join(content)
    article['words'] = words
    article['wc'] = wc

# Get a TF-IDF score for each word in each article
all_words = [word for article in articles for word in article['words']]
tc = nltk.TextCollection(all_words)

for article in articles:
    # Calculate TF-IDF scores
    tf_idf_scores = {}
    for word in article['words']:
        # NLTK method for calculating TF-IDF
        tf_idf_scores[word] = tc.tf_idf(word, article['words'])
    article['tf_idf_scores'] = tf_idf_scores
    
    # Extract Entities
    sentences = nltk.tokenize.sent_tokenize(article['content'])
    tokens = [nltk.tokenize.word_tokenize(s) for s in sentences]
    pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
    
    # Flatten the list since we're not using sentence structure
    # and sentences are guaranteed to be separated by a special
    # POS tuple such as ('.', '.')
    
    pos_tagged_tokens = [token for sent in pos_tagged_tokens for token in sent]
    
    all_entity_chunks = []
    previous_pos = None
    current_entity_chunk = []
    for (token, pos) in pos_tagged_tokens:
        if pos == previous_pos and pos.startswith('NN'):
            current_entity_chunk.append(token)
        elif pos.startswith('NN'):
            if current_entity_chunk != []:
                
                # Note that current_entity_chunk could be a duplicate when appended,
                # so frequency analysis again becomes a consideration
                
                all_entity_chunks.append((' '.join(current_entity_chunk), pos))
            current_entity_chunk = [token]
        previous_pos = pos
        
    # Store the chunks as an index for the document
    # and account for frequency while we're at it...
    
    article['entities'] = {}
    for c in all_entity_chunks:
        article['entities'][c] = article['entities'].get(c, 0) + 1
        

# Printing sample results to see if I am getting what I expected
# Looks like TF-IDF may not be that useful unles the corpus is
# much larger, and I am perhaps using a search technique for the
# wrong purpose.

# For each article, print the top 5 words based on TF-IDF score
print "\n"
for article in articles:
    scores = article['tf_idf_scores']
    sorted_scores = sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True)
    print "%s: %s" % (article['title'][0:30].ljust(30), ", ".join([score[0] for score in sorted_scores[0:5]]))

# Print more detail for one of the articles.
# For each word in the article, print its frequency in the article,
# followed by its TF-IDF score
print "\n"
print articles[1]['title']
print articles[1]['content']
scores = articles[1]['tf_idf_scores']
sorted_scores = sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True)
for score in sorted_scores:
    print "%s %4i, %.5f" % (score[0].ljust(20), articles[1]['wc'][score[0]], score[1])

for article in articles:
    print "%s: %s" % (article['title'][0:30].ljust(30), ", ".join([entity for (entity, pos) in article['entities'] if entity.istitle()]))
