# -*- coding: utf-8 -*-

from couchdb.mapping import Document, TextField, IntegerField, ListField, DictField, Mapping
import logging
import nltk
from nltk.corpus import stopwords

class Article(Document):
    
    type = TextField(default='article')
    source = TextField()
    title = TextField()
    link = TextField()
    raw = TextField()
    word_frequencies = ListField(DictField(Mapping.build(
        word = TextField(),
        frequency = IntegerField()
    )))

    def get_content(self):
        return self.raw

    def set_content(self, content):
        self.raw = content
        if content and len(content) > 0:
            words = nltk.word_tokenize(content)
            fdwords = nltk.FreqDist(words)
            self.fdwords = fdwords

    content = property(get_content, set_content)

    def put(self, db):
        'Put the article and associated word frequencies into couchdb.'
        self.store(db) # to get auto id from couchdb
        for w in self.fdwords.keys():
            if w.isalpha() and w not in stopwords.words('english'):
                # search for existing occurence of word doc in couchdb
                map_fun = """
                    function(doc){
                        if (doc.word == '%s')
                            emit(doc.id);
                    }
                """ % (w)
                view = db.query(map_fun)
                if len(view) > 0:
                    word = Word.load(db, view.rows[0].id)
                else:
                    word = Word(word=w)
                frequency = self.fdwords[w]
                self.word_frequencies.append(word=w, frequency=frequency)
                word.inc_frequency(self.id, frequency)
                word.store(db)
        self.store(db) # with word frequencies updated

    def __str__(self):
        print self.title

class Word(Document):
    
    type = TextField(default='word')
    word = TextField()
    word_frequencies = ListField(DictField(Mapping.build(
        article_id = TextField(),
        frequency = IntegerField()
    )))

    def inc_frequency(self, article_id, frequency):
        self.word_frequencies.append(article_id=article_id, frequency=frequency)

    def __str__(self):
        return self.word
