# -*- coding: utf-8 -*-

import couchdb
import csv
import feedparser
from htmlparser import HtmlParser
from models.models import Article
import re
from urllib2 import urlopen, URLError

class Harvester():
    
    def __init__(self, db, filename):
        'Harvest articles from the list of feeds in filename.'
        self.db = db
        self.filename = filename
        feedlist = self.read_feed_list(filename)
        self.articles = self.parse_feedlist(feedlist)

    def read_feed_list(self, filename):
        '''
        Read the feed list from a CSV file. The first item of each line
        is the URL to an RSS feed.
        '''
        feedlist = []
        reader = csv.reader(open(filename, 'rb'))
        for line in reader:
            feedlist.append(line[0])
        return feedlist

    def parse_feed(self, feed):
        'Extract list of articles from the feed.'
        articles = []
        htmlparser = HtmlParser()
        for e in feed.entries[:1]: # read just the first entry while debugging
            article = Article(source=e.author, title=e.title, link=e.link)
            content = htmlparser.parse(e.link)
            article.content = re.sub(r' -.*$', '', content)
            article.put(self.db) # put article and word frequencies into couchdb
            articles.append(article)
        return articles

    def parse_feedlist(self, feedlist):
        'Parse the RSS feeds.'
        articles = []
        for url in feedlist:
            try:
                c = urlopen(url)
            except URLError:
                print 'Failed to fetch ' + url
            articles += self.parse_feed(feedparser.parse(c))
        return articles

    def __str__(self):
        print self.filename

def main():
    server = couchdb.Server()
    try:
        db = server['trendnz']
    except couchdb.http.ResourceNotFound:
        db = server.create('trendnz')

    # articles = Harvester(db, 'feed1.txt').articles
    # print articles[0].title
    # print articles[0].content
    # print articles[0].fdwords
    
    # Query CouchDB
    map_fun = """
        function(doc){
            if (doc.type == 'article')
                emit(doc.title);
        }
    """
    results = db.query(map_fun)
    for r in results:
        print r.key

    map_fun = """
        function(doc){
            if (doc.type == 'word')
                emit(doc.word, doc);
        }
    """
    results = db.query(map_fun)
    accum_word_frequencies = [(reduce(lambda t, f: t + f, [w['frequency'] for w in r.value['word_frequencies']]), r.key) for r in results]
    accum_word_frequencies.sort(reverse=True)
    for w in accum_word_frequencies:
        print "%s (%i)" % (w[1], w[0])

if __name__ == '__main__':
    main()
