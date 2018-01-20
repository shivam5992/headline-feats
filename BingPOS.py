# -*- coding: utf-8 -*-

import requests
import json
import re


class PostTag:
    def __init__(self):
        self.VERB_TAGS = ['VB','VBG','VBN','VBP','VBZ','VBD']
        self.NOUN_TAGS = ['NN','NNP','NNPS','NNS']
        self.ADJECTIVE_TAGS = ['JJ','JJR','JJS']

        self.url = "https://api.projectoxford.ai/linguistics/v1.0/analyze"

        self.headers = {
            'content-type': "application/json",
            'ocp-apim-subscription-key': "9a09bd6d85b045f186af5a017a7b9952",
            }


    def pos_tags_percentages(self, result):
        a = {'noun':0,'verb':0,'adjective':0,'other':0}
        for each in result:
            if each in self.VERB_TAGS:
                a['verb']+=1
            elif each in self.NOUN_TAGS:
                a['noun']+=1
            elif each in self.ADJECTIVE_TAGS:
                a['adjective']+=1
            else:
                a['other'] +=1
        sumall = sum(a.values())
        for key, value in a.items():
            a[key] = round(((value+0.0)/sumall)*100,2)  
        return a

    def join_lists(self, result):
        lists = []
        for i in range(len(result)):
            lists.extend(result[i])
        return lists

   
    def post_tags(self, text):
        text = text.lower()
        data = '{"language" : "en","analyzerIds" : ["4fa79af1-f22c-408d-98bb-b7d7aeef7f04", "22a6b758-420f-4745-8a3c-46835a67c0d2"],"text" :"'+text+'"}'
        response = requests.post(self.url, headers = self.headers, data = data)
        res = json.loads(response.text)
        result = self.join_lists(res[0]['result'])
        clean_text = self.clean(text)
        return {'pos_tags_percent':self.pos_tags_percentages(result),'verb_list':self.verbs(res[1]['result'][0],clean_text)}

    def clean(self, text):
        text = ''.join(e for e in text if e.isalnum() or e ==' ')
        texts = text.split(" ")
        return texts

    '''verbs are find assuming same word are not used for more than one tag'''
    def verbs(self, result, clean_text):
        v = []
        for each in clean_text:
            if each:
                k = re.findall('[a-zA-Z]+\s'+each,result)
                if len(k)>0:
                    tag = k[0].split(each)
                    tag = tag[0].strip()
                    if tag in self.VERB_TAGS:
                        v.append(each)
        return v 

PT = PostTag()