### ADD MORE INTERESTS FROM WIKIPEDIA ETC 
### Check for cleaning of raw interests (as you may be loosing some information)


from cleaner.Cleaner import clean
import operator 
from collections import Counter 

class UserInterests:
	def __init__(self):
		interests = open("InsightsEngine/dictionaries/INTERESTS.txt").read().strip().split("\n")
		
		self.keywords = {}
		interests_dict = {}
		for line in interests:
			if line not in interests_dict:
				interests_dict[line] = 1
				Int, kw = line.split("	")[0].strip(), line.split("	")[1].strip()
				self.keywords[clean(kw)] = Int 


	def getUserInterests(self, sentences, limit = 100):
		corpus = []
		for each in sentences:
			corpus.extend(clean(each).split())
		_cool = Counter(corpus)
		dist = sorted(_cool.items(), key = operator.itemgetter(1), reverse = True)
		wordlist = dist[:limit]
		
		wordlist = [(u'cricket', 41), (u'virat', 21), (u'world', 20), (u'live', 18), (u'follow', 15), (u'kohli', 15), (u'love', 13), (u'news', 12), (u'life', 12), (u'fan', 11), (u'indian', 11), (u'student', 10), (u'like', 10), (u'account', 9), (u'facebook', 9), (u'cup', 8), (u'around', 8), (u'twitter', 8), (u'music', 7), (u'new', 7), (u'big', 7), (u'stand', 7), (u'asia', 6), (u'nfollow', 6), (u'turn', 6), (u'lover', 6), (u'proud', 6), (u'score', 6), (u'make', 6), (u'icc', 6), (u'update', 6), (u'time', 6), (u'odi', 5), (u'let', 5), (u'sports', 5), (u'cheeku', 5), (u'join', 5), (u'india', 5), (u'good', 5), (u'chronicle', 5), (u'get', 5), (u'best', 5), (u'media', 5), (u'international', 5), (u'official', 5), (u'tweet', 4), (u'die', 4), (u'design', 4), (u'action', 4), (u'ipl', 4)]
		total_count = sum([x[1] for x in wordlist])
		wordlist = [list(each) for each in wordlist]
		for each in wordlist:
			each.append(float(each[1]) / total_count)

		interests = {}
		for each in wordlist:
			wrd = each[0]
			imp = each[2]

			for k,v in self.keywords.iteritems():
				try:
					if " "+wrd+" " in " "+k.encode("utf8").decode("ascii", "ignore").lower()+" ":
						if v not in interests:
							interests[v] = 0
						interests[v] += 1 * imp
				except Exception as E:
					print E 
					continue
		vals = sorted(interests.items(), key=operator.itemgetter(1), reverse = True)
		return vals