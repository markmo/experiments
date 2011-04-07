# -*- coding: utf-8 -*-

from chunkers import LocationChunker, sub_leaves
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, ListField, DictField, Mapping
import logging
import nltk
from nltk.chunk import batch_ne_chunk
from nltk.corpus import stopwords

class Article(Document):
    
    type = TextField(default='article')
    publisher = TextField()
    publisher_location = TextField()
    published_date = DateTimeField()
    title = TextField()
    link = TextField()
    image_link = TextField()
    image_type = TextField()
    source = TextField()
    raw = TextField()
    word_frequencies = ListField(DictField(Mapping.build(
        word = TextField(),
        frequency = IntegerField()
    )))
    entity_frequencies = ListField(DictField(Mapping.build(
        entity_type = TextField(),
        entity = TextField(),
        frequency = IntegerField()
    )))

    def extract_word_frequencies(self, tokens):
        words = [w.lower() for sent in tokens for w in sent if w.isalpha() and w not in stopwords.words('english')]
        fdwords = nltk.FreqDist(words)
        self.fdwords = fdwords
        for w in self.fdwords.keys():
            frequency = self.fdwords[w]
            self.word_frequencies.append(word=w, frequency=frequency)


    def extract_entity_frequencies(self, tokens):
        pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
        loc = LocationChunker()
        
        trees = batch_ne_chunk(pos_tagged_tokens)
        entity_types = ['PERSON', 'ORGANIZATION', 'GPE', 'LOCATION', 'FACILITY']
        for entity_type in entity_types:
            entity_freq_dict = {}
            chunks = [sub_leaves(t, entity_type) for t in trees]
            for sent in chunks:
                for c in sent:
                    entity = ' '.join([w[0] for w in c])
                    entity_freq_dict[entity] = entity_freq_dict.get(entity, 0) + 1

            # A secondary attempt at extracting locations based on reference
            # to lists of place names
            if entity_type == 'LOCATION':
                for sent in pos_tagged_tokens:
                    t = loc.parse(sent)
                    chunks = sub_leaves(t, 'LOCATION')
                    for c in chunks:
                        entity = ' '.join([w[0] for w in c])
                        entity_freq_dict[entity] = entity_freq_dict.get(entity, 0) + 1

            entity_freq_list = [(entity_freq_dict[e], e) for e in entity_freq_dict.keys()]
            entity_freq_list.sort(reverse=True)
            for e in entity_freq_list:
                self.entity_frequencies.append(
                    entity_type=entity_type.lower(),
                    entity=e[1],
                    frequency=e[0])


    # Basic entity extraction, but not precise enough so using
    #  above approach instead
    # def extract_entity_frequencies(self, tokens):
    #     pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
    #     
    #     # Flatten the list since we're not using sentence structure
    #     # and sentences are guaranteed to be separated by a special
    #     # POS tuple such as ('.', '.')
    #     
    #     pos_tagged_tokens = [token for sent in pos_tagged_tokens for token in sent]
    #     
    #     all_entity_chunks = []
    #     previous_pos = None
    #     current_entity_chunk = []
    #     for (token, pos) in pos_tagged_tokens:
    #         if pos == previous_pos and pos.startswith('NN'):
    #             current_entity_chunk.append(token)
    #         elif pos.startswith('NN'):
    #             if current_entity_chunk != []:
    #                 
    #                 # Note that current_entity_chunk could be a duplicate when appended,
    #                 # so frequency analysis again becomes a consideration
    #                 
    #                 all_entity_chunks.append((' '.join(current_entity_chunk), pos))
    #             current_entity_chunk = [token]
    #         previous_pos = pos
    #     
    #     # Store the chunks as an index for the article
    #     # and account for frequency while we're at it
    #     
    #     entity_freq_dict = {}
    #     for c in all_entity_chunks:
    #         entity_freq_dict[c[0]] = entity_freq_dict.get(c[0], 0) + 1
    #     entity_freq_list = [(entity_freq_dict[e], e) for e in entity_freq_dict.keys()]
    #     entity_freq_list.sort(reverse=True)
    #     for e in entity_freq_list:
    #         self.entity_frequencies.append(entity=e[1], frequency=e[0])

    def get_content(self):
        return self.raw

    def set_content(self, content):
        self.raw = content
        if content and len(content) > 0:
            sentences = nltk.sent_tokenize(content)
            tokens = [nltk.word_tokenize(s) for s in sentences]
            self.extract_word_frequencies(tokens)
            self.extract_entity_frequencies(tokens)

    content = property(get_content, set_content)

    def __str__(self):
        print self.title

'''
    # I don't think I need to store Word as a separate document
    # I can query by word using map-reduce
    # Storing a word string many times is probably no less
    #  efficient than storing a string reference
    def put(self, db):
        'Put the article and associated word frequencies into couchdb.'
        # self.store(db) # to get auto id from couchdb
        for w in self.fdwords.keys():
            search for existing occurence of word doc in couchdb
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
'''