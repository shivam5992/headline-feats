import urllib
import json

class KnowledgeGraph:
    def __init__(self, KNOWLEDGE_GRAPH_KEY):
        self.KEY = KNOWLEDGE_GRAPH_KEY

    def knowledge_graph(self, query):
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
            'query': query,
            'limit': 1,
            'indent': True,
            'key': self.KEY,
        }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())
        
        results = []
        for element in response['itemListElement']:
            mains = {}
            score = element['resultScore']
            name = element['result']['name']
            name_type = str(element["result"]['@type'])
            mains = {
            'name' : name,
            'type' : name_type,
            'score' : score
            } 
            results.append(mains)
        return results