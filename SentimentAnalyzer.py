import requests
import json
import urllib
import ast

class SentimentAnalyzer:
	def rangeFixer(self, val, old_i, old_f, ii, ff):
		old_mid = float(old_i + old_f)/2
		if val >= old_mid:
			new_val = float(val - old_mid)/(old_f - old_mid)
		else:
			new_val = float(val - old_mid)/(old_mid - old_i)
		return new_val

	def analyzer(self, blob, tb = False, an = True, nl = False):
		sub_sentiment = []
		tot_sent = 0.0
		for sentences in blob.sentences:
			temp = {}
			temp['text'] = str(sentences)

			a = None
			b = None 
			c = None
			if nl:
				try:
				  a = NLTKSentiment(str(sentences)).getSentiment()
				except:
				  pass
				temp['nltkSentiment'] = a
			
			if an:
				try:
					b = AnalyzerSentiment(str(sentences)).getSentiment()
				except Exception as E:
					print E 
					pass
				temp['AnalyzerSentiment'] = b
			
			if tb:
				try:
					c = TextBlobSentiment(str(sentences)).getSentiment()
				except:
					pass
				temp['textblobSentiment'] = c

			if b:
				tot_sent += b 
			sub_sentiment.append(temp)

		try:
			total_sentiment = tot_sent/len(sub_sentiment)
		except:
			total_sentiment = 0.0
		return total_sentiment, sub_sentiment


class TextBlobSentiment:
	def rangeFixer(self, val, old_i, old_f, ii, ff):
		old_mid = float(old_i + old_f)/2
		if val >= old_mid:
			new_val = float(val - old_mid)/(old_f - old_mid)
		else:
			new_val = float(val - old_mid)/(old_mid - old_i)
		return new_val


	def getSentiment(self, tb):
		sentiment = tb.sentiment.polarity
		sentiment = self.rangeFixer(sentiment, -1,1,0,1)
		return sentiment


class AnalyzerSentiment:
	def __init__(self, text):
		self.url = "http://sentimentanalyzer.appspot.com/api/classify.json"
		self.headers = {"content-type": "application/json"}
		self.text = text

	def getSentiment(self):
		payload = { "data"  : [{'content' : self.text, 'lang' : 'en' }] }
		resp = requests.post(self.url, data = json.dumps(payload), headers = self.headers)
		val = resp.json()['data'][0]['score']
		return SentimentAnalyzer().rangeFixer(val, 0, 1,-1, 1)


class NLTKSentiment:
	def __init__(self, text):
		self.url = 'http://text-processing.com/api/sentiment/'
		self.headers = {'content-type' : 'application/json'}
		self.text = text 

	def getSentiment(self):
		data = urllib.urlencode({ "text": self.text }) 
		u = urllib.urlopen("http://text-processing.com/api/sentiment/", data)
		the_page = ast.literal_eval(u.read())
		return the_page['probability'][the_page['label']], the_page['label']

class PropheseeSentiment:
	def __init__(self, text):
		self.text_data = {"str1" : text}
		self.url = "https://54.218.46.198:8080/rest/ui/v1/sentiment/evaluate"

	def getSentiment(self):
		resp = requests.post(self.url, data = json.dumps(self.text_data))
		print resp.json()

class SentimentDrivers:
	def getSentiment(self, comment):
		blob = TextBlob(comment)
		sentiment = self.SA.analyzer(blob)
		return sentiment