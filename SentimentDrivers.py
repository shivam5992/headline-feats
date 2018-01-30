from SentimentAnalyzer import SentimentAnalyzer
from textblob import TextBlob
import pandas as pd 
import itertools
import operator 

class SentimentDrivers:
	def __init__(self):
		self.positives = open("Engine/dependencies/positives.txt").read().strip().split("\n")
		self.negatives = open("Engine/dependencies/negatives.txt").read().strip().split("\n")

	def getDrivers(self, corpus_raw):
		blob = TextBlob(corpus_raw)
		mains = {}
		for sent in blob.sentences:
			sent = sent.strip(".")
			words = sent.split() 
			pairs = itertools.combinations(words, 2)

			for pair in pairs:
				w1 = pair[0]
				w2 = pair[1]

				if w1 not in mains and w2 not in mains:
					mains[w1] = {}
					mains[w2] = {}
				if w1 not in mains and w2 in mains:
					mains[w1] = {}
				if w1 in mains and w2 not in mains:
					mains[w2] = {}
				
				if w1 not in mains[w2]:
					mains[w2][w1] = 1
				else:
					mains[w2][w1] += 1
				if w2 not in mains[w1]:
					mains[w1][w2] = 1
				else:
					mains[w1][w2] += 1
				if w2 not in mains[w1]:
					mains[w1][w2] = 1
				else:
					mains[w1][w2] += 1

		docs = {}
		for k,v in mains.iteritems():
			vals = sorted(v.items(), key = operator.itemgetter(1), reverse = True)
			if k in self.positives:
				sentiment = "positive"
			elif k in self.negatives:
				sentiment = "negatives"
			else:
				sentiment = "neutral"

			pos_tag = TextBlob(k).tags[0][1]

			docs = {
				'key' : k,
				'sentiment' : sentiment,
				'co-occured' : vals,
				'pos_tag' : pos_tag
				}

			print docs['key'] + "\t" + docs['sentiment'] + "\t" + docs['pos_tag'] + "\t" + str(docs['co-occured'][:3])

SD = SentimentDrivers()