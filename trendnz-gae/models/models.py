# -*- coding: utf-8 -*-

from google.appengine.ext import db
import logging
import nltk

class Article(db.Model):
    
    source = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    link = db.StringProperty(required=True)
    raw = db.TextProperty()

    def get_content(self):
        return self.raw

    def set_content(self, content):
        self.raw = content
        if content and len(content) > 0:
            words = nltk.word_tokenize(content)
            fdwords = nltk.FreqDist(words)
            self.fdwords = fdwords

    content = property(get_content, set_content)

    def save(self):
        self.put()

        # Remove existing associations
        for f in self.word_frequencies:
            f.delete()

        # Save associated word frequencies
        for w in self.fdwords.keys():
            if w.isalpha():
                q = Word.gql("where word = :word", word = w).fetch(1)
                if len(q) == 0:
                    word = Word(word=w)
                    word.put()
                else:
                    word = q[0]
                frequency = self.fdwords[w]
                WordFrequency(word=word, article=self, frequency=frequency).put()

    def __str__(self):
        print self.title

class Word(db.Model):
    
    word = db.StringProperty(required=True)
    
    def __str__(self):
        return self.word

class WordFrequency(db.Model):
    
    word = db.ReferenceProperty(Word, required=True, collection_name='word_frequencies')
    article = db.ReferenceProperty(Article, required=True, collection_name='word_frequencies')
    frequency = db.IntegerProperty()

    def __str__(self):
        return "%s: %i" % (self.word.word, self.frequency)
