import requests 

class WatsonAPI:
	def chunks(self, l, n):
		for i in range(0, len(l), n):
			yield l[i:i + n]

	def tone_analyzer(self, corpus):
		url = "https://tone-analyzer-demo.mybluemix.net/api/tone"
		resp = requests.post(url, data = {"text" : corpus})
		response = resp.json()
		response = response['document_tone']
		return response


	def personality_traits(self, corpus):
		url = "https://personality-insights-livedemo.mybluemix.net/api/profile/text"
		resp = requests.post(url, data = {"text" : corpus, "language": "en", "source_type":"text","accept_language":"en","include_raw":False})
		response = resp.json()
		return response


	def concepts(self, corpus):
		url = "https://alchemy-language-demo.mybluemix.net/api/entities"
		resp = requests.post(url, data = {"text" : corpus, "sentiment" : 1})
		return resp.text