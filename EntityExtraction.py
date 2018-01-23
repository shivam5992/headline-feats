# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:39:27 2016

@author: aman
"""

import nltk 

class EntityExtraction:
    
    def __init__(self):
        pass

    def entity_names(self,text):
        text = text.decode('utf-8','ignore').encode('ascii','ignore')
        entity_names = []
        chunked_sentences = self._chunked_sent(text)
        for tree in chunked_sentences:
            entity_names.extend(self._extract_entity_names(tree))
        
        return list(set(entity_names))
        
    def _extract_entity_names(self,t):
        entity_names = []
        if hasattr(t, 'label') and t.label:
            if t.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(self._extract_entity_names(child))
        return entity_names
    
    def _chunked_sent(self,text): 
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
        return chunked_sentences