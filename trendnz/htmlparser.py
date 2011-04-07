# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import nltk
from urllib2 import urlopen, URLError

class HtmlParser():
    
    def parse(self, url):
        try:
            page = urlopen(url)
        except URLError:
            print 'Failed to fetch ' + url
        try:
            soup = BeautifulSoup(page)
        except HTMLParser.HTMLParseError:
            print 'Failed to parse ' + url

        body = soup.find(True, 'articleBody')
        if body and len(body) > 1:
            contents = []
            paras = body.findAll('p')
            for p in paras:
                # p.string returns None if there are multiple child elements
                # under the P tag
                for c in p.contents:
                    if c.string and len(c.string) > 0:
                        text = nltk.clean_html(c.string)
                        contents.append(text.strip())
        return '\n'.join(contents)
