'''
Python Class to perform operations on a bulkier text and extract a number of insights 
corpus - list of sentences 
'''

from SentimentAnalyzer import TextBlobSentiment
from textstat.textstat import textstat 
from collections import Counter
from textblob import TextBlob
from langdetect import detect
from BingPOS import PT
from cleaner import Cleaner 
import operator 
import requests
import datetime
import calendar
import string 
import time

punctuation = string.punctuation


class TextGripUtility:
	def __init__(self):
		self.SA = TextBlobSentiment()

	## Sentiment
	def annotate_sentiment(self, blob):
		## Find sentiment of the text
		sentiment = self.SA.getSentiment(blob)
		sentiment = round(sentiment, 2)

		## Bucket the score into Grade and Tag
		if sentiment <= -0.7:
			sentiment_tag =  'Strongly Negative'
			content_analyzer_grade = 'A+'
		elif sentiment > -0.7 and sentiment < -0.2:
			sentiment_tag =  'Moderately Negative'
			content_analyzer_grade = 'A'
		elif sentiment >= 0.7:
			sentiment_tag =  'Strongly Positive'
			content_analyzer_grade = 'A+'
		elif sentiment > 0.2 and sentiment < 0.7:
			sentiment_tag =  'Moderately Positive'
			content_analyzer_grade = 'A'
		else:
			sentiment_tag =  'Neutral'
			content_analyzer_grade = 'B'


		sentiment_per = (((sentiment - (-1)) * (100 - 0)) / (1 - (-1))) + 0

		## Prepare Response
		sentiment_response = {
			'sentiment' : sentiment,
			'tag' : sentiment_tag,
			'sentiment_per' : sentiment_per,
			'grade' : content_analyzer_grade
		}
		return sentiment_response

	## Sarcasm
	def text_scarsam(self, sentence):

		words = len(sentence.split())
		chars = len(sentence.replace(" ",""))

		if words < 4 or chars < 3:
			sarcasm = {
				'sarcasm': 0,
				'tag' : "Not Sarcastic",
				'grade' : "B",
				'sarcasm_per' : 0
			}
			return sarcasm

		try:
			sentence = sentence.replace(" ","+")
			url = "http://127.0.0.1:5001/_compute?sentence="
			resp = requests.get(url)
			sarcasm_value = resp.json()['result'] 
		except Exception as E:
			print E 
			try:
				sentence = sentence.replace(" ","+")
				url = "http://www.thesarcasmdetector.com/_compute?sentence="+sentence
				resp = requests.get(url)
				sarcasm_value = resp.json()['result'] 
			except Exception as E2:
				print "EE", E2
				sarcasm_value = 0

		## Bucket the scores and Grade 
		if sarcasm_value >= 75 or sarcasm_value <= -75:
			sarcasm_tag = "Highly Sarcastic"
			analyzer_grade = 'A+'
		elif (sarcasm_value < 75 and sarcasm_value >= 25) or (sarcasm_value > -75 and sarcasm_value <= -25):
			sarcasm_tag = "Moderately Sarcastic"
			analyzer_grade = "A"
		else:
			sarcasm_tag = "Not Sarcastic"
			analyzer_grade = "B"

		sarcasm_per = sarcasm_value
		if sarcasm_value < 0:
			sarcasm_per = -1 * sarcasm_value

		sarcasm = {
			'sarcasm': sarcasm_value,
			'tag' : sarcasm_tag,
			'grade' : analyzer_grade,
			'sarcasm_per' : sarcasm_per
		}

		return sarcasm


	## Cleaning
	def clean_corpus(self, sentences):
		wordlist = []
		for sent in sentences:
			cleaned = Cleaner.clean(sent)
			words = cleaned.split()
			wordlist.extend(words)
		corpus = " ".join(wordlist)
		return corpus

	def generate_ngrams(self, corpus, n):
		corpus = corpus.split(' ')
		output = []
		for i in range(len(corpus)-n+1):
			output.append(" ".join(corpus[i:i+n]))
		return output

	def annotate_language(self, sentence):
		try: 
			lan = detect(sentence)
		except Exception as E:
			lan = "Misc"
		return lan

	def clean_comment(self, comment):
		return Cleaner.clean(comment) # Move this to Self 

	def get_total_engagements(self, stats):
		return sum(stats.values())

	def parse_fb_time(self,created_time):
		date = created_time.split("T")[0].replace("-","")
		hour = created_time.split("T")[1].split(":")[0]
		day = datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:])).weekday()
		day = calendar.day_name[day]
		resp = {
			'date' : date,
			'hour' : hour,
			'day' : day
		}			
		return resp

	def parse_cTs(self, cTs):
		created_time = str(time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(cTs/1000.)))
		date = created_time.split("T")[0].replace("-","")
		hour = created_time.split("T")[1].split(":")[0]
		
		day = datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:])).weekday()
		day = calendar.day_name[day]
		resp = {
			'date' : date,
			'hour' : hour,
			'day' : day
		}			
		return resp

	def get_entitiy_used(self, comment_text,entity):
		hashtags = []
		for word in comment_text.split():
			if word.startswith(entity):
				hashtags.append(word)
		return hashtags

	def get_post_sentence_length(self, post):
		blob = TextBlob(post)
		return len(blob.sentences)


	def getGrade(self, score):
		if score > 9:
			grade = "A+"
		elif score >= 8:
			grade = "A"
		elif score >= 6:
			grade = "B+"
		elif score >= 5:
			grade = "B"
		elif score >= 4:
			grade = "C"
		elif score >= 3:
			grade = "D"
		else:
			grade = "F"
		return grade


class TextGrip:
	def __init__(self):
		self.calais_url = "https://api.thomsonreuters.com/permid/calais"
		self.headers = {'X-AG-Access-Token' : 'Fkzi7dBqweT3T9zogBTmE5U9qwFdx5TY', 'Content-Type' : 'text/raw', 'outputFormat' : 'application/json', 'omitOutputtingOriginalText' : 'true'}


		self.tgu = TextGripUtility()
		self.stopwords = open("InsightsEngine/dictionaries/stopwords.txt").read().strip().split("\n")
		self.emoticons = open("InsightsEngine/dictionaries/emoticons.txt").read().strip().split("\n")
		self.meta_data = {
			'power' : open("InsightsEngine/dictionaries/power.txt").read().strip().split("\n"),
			'emotional' : open("InsightsEngine/dictionaries/emotional.txt").read().strip().split("\n"),
			'common' : open("InsightsEngine/dictionaries/common.txt").read().strip().split("\n"),
			'uncommon' : open("InsightsEngine/dictionaries/uncommon.txt").read().strip().split("\n"),
			'pos_tags' : open("InsightsEngine/dictionaries/pos_tags.txt").read().strip().split("\n"),
			
			# 'both' : open("InsightsEngine/dictionaries/both.txt").read().strip().split("\n"),
			# 'positives' : open("InsightsEngine/dictionaries/positives.txt").read().strip().split("\n"),
			# 'negatives' : open("InsightsEngine/dictionaries/negatives.txt").read().strip().split("\n"),
		}

		self.both = []
		self.all_tags = ['common_tag', "noun", "verb", "adverb", "adjective", "special"]
		self.pos_dic = {}
		for line in self.meta_data['pos_tags']:
			content = line.split(" ")
			pos = content[0]
			POS = content[1]
			self.pos_dic[pos] = POS

		self.meta_keywords = {}
		for category, data in self.meta_data.iteritems():
			for each in data:
				term = each
				if term not in self.meta_keywords:
					self.meta_keywords[term] = []
				self.meta_keywords[term].append(category)

		for x,y in self.meta_keywords.iteritems():
			if len(y) > 1:
				if y == ['uncommon', 'common']:
					self.meta_keywords[x] = ["uncommon"]

			if "emotional" in self.meta_keywords[x] and "power" in self.meta_keywords[x]:
				self.meta_keywords[x] = ["power", "emotional"]
				self.both.append(x)

			self.meta_keywords[x] = list(set(self.meta_keywords[x]))


	def get_pos_tag(self, word):
		blob = TextBlob(word).tags
		return blob

	def get_complete_postags(self,listofsentences):
		complete = {}
		for sent in listofsentences:
			sent_pos = self.get_pos_tag(sent)
			for tags in sent_pos:
				
				word = TextGripUtility().clean_comment(tags[0])
				if not word:
					continue

				if word not in complete:
					complete[word] = []
				if tags[1] not in complete[word]:
					complete[word].append(tags[1])
		return complete

	def get_post_words(self, post_words, key):
		return [x for x in post_words if x in self.meta_data[key]]


	def top_ngrams(self, cleaned_corpus, n = 2):
		ngrams = self.tgu.generate_ngrams(cleaned_corpus, n)
		ngrams = [x for x in ngrams if x.strip() in ngrams]
		ngrams = Counter(ngrams)
		ngrams_dist = sorted(ngrams.items(), key=operator.itemgetter(1), reverse = True)
		return ngrams_dist

	def getWordBalanceGrade(self, balance):
		score = 0

		emo = balance['emotional']['percentage']
		power = balance['power']['percentage']
		comm = balance['common']['percentage']
		uncomm = balance['uncommon']['percentage']


		if emo == 0 and power == 0:
			score += 0
		elif emo < 5 and power < 5:
			score += 2
		elif emo >= 5:
			score += 5
		elif power >= 5:
			score += 5
		else:
			score += 5


		# Out of 3
		if comm > 0 and comm <= 50:
			score += 3
		elif comm > 50:
			score += 2


		# Out of 2
		score += 1
		if uncomm > 0:
			score += 1

		grade = self.tgu.getGrade(score)
		return grade, score

	def count_occurrences(self, word, sentence):
		if " " in word.strip():
			return sentence.lower().count(word)
		else:
			return sentence.lower().split().count(word)


	def vocabulary_analysis(self, cleaned_corpus, text):
		len_wrds = len(text.split())
		emos = []

		balance = {}
		for all_keys in self.meta_data.keys():
			balance[all_keys] = []

		text = text.lower()
		words = text.split()
		covered = []
		for word in self.meta_keywords:
			if " "+word+" " in " "+text+" ":
				for tag in self.meta_keywords[word]:
					if word not in balance[tag]:
						actual_count = self.count_occurrences(word,text)
						for i in range(actual_count):
							balance[tag].append(word)

							if word in self.both:
								emos.append(word)

						covered.append(word)

			else:
				cln_wrd = Cleaner.clean(word)
				if cln_wrd != "" and cleaned_corpus != "" and " "+cln_wrd+" " in " "+cleaned_corpus+" ":
					for tag in self.meta_keywords[word]:
						if word not in balance[tag] and word.lower().strip() in text.lower().strip():
							actual_count = self.count_occurrences(cln_wrd,cleaned_corpus)
							for i in range(actual_count):
								balance[tag].append(word)
								
								if word in self.both:
									emos.append(word)

							covered.append(word)
		
		visited = []
		for key, values in balance.iteritems():
			vals = Counter(values)
			vals = sorted(vals.items(), key = operator.itemgetter(1), reverse = True)
			
			for ww in vals:
				if ww[0] not in visited:
					visited.append(ww[0])

			cnts = round((float(sum([x[1] for x in vals]) * 100)/ len_wrds) ,2)

			balance[key] = {}
			value_words = ["".join(a for a in x[0] if a not in punctuation) for x in vals]
			balance[key]['values'] = list(set(value_words))
			balance[key]['percentage'] = cnts
			balance[key][key+'_count'] = sum([x[1] for x in vals])


		word_balance_grade, score = self.getWordBalanceGrade(balance)
		balance['grade'] = word_balance_grade
		balance['score'] = score

		other = []
		cln_words = cleaned_corpus.split()
		for wd in words:
			wd = "".join(a for a in wd if a not in punctuation)
			if wd and wd not in covered:
				other.append(wd)
		# print other 
		other_per = float(len(other)) * 100/ len_wrds

		# other_per = 100 - balance['common']['percentage'] - balance['uncommon']['percentage'] - balance['emotional']['percentage'] - balance['power']['percentage']
		# if other_per < 0:
			# other_per = 0

		balance['other'] = {}
		balance['other']['percentage'] = other_per
		balance['other']['values'] = other

		balance['common']['common_count'] = balance['common']['percentage']

		# if emos:
		# 	balance['emotional']['values'].extend(emos)
		# 	balance['emotional']['emotional_count'] += len(emos)

		return balance


	def mentioned_distribution(self, corpus, mentioned):
		mentioned = [x.lower() for x in mentioned]
		dist = {}
		for word in mentioned:
			if word not in dist:
				dist[word] = 0
			dist[word] = corpus.count(word)
		dist = sorted(dist.items(), key = operator.itemgetter(1), reverse = True)
		return dist   

	def optimism_pessimism(self, vocab):
		pos_count = sum([x[1] for x in vocab['positives']])
		neg_count = sum([x[1] for x in vocab['negatives']])
		total = sum([x[1] for x in vocab['all']])

		optimism = round((float(pos_count) / (1+total) * 100),2)
		pessimism = round((float(neg_count) / (1+total) * 100),2)
		return optimism, pessimism

	def emoticon_distribution(self, corpus_raw):
		dist = {}
		for emoline in self.emoticons:
			emo = emoline.split(" :")
			if len(emo) <= 1:
				continue

			emoji = emo[0].strip().strip("'").strip('"')
			sentiment = emo[1].strip().strip("'").strip('"')
			
			cnt = corpus_raw.count(emoji)
			if emoji not in dist:
				dist[emoji] = cnt 
		
		dist = sorted(dist.items(), key = operator.itemgetter(1), reverse = True)
		dist = [x for x in dist if x[1] > 0 and len(x[0]) > 1]

		# Fix Ambiguous Emojis
		ambiguous = ["--"]
		for i, emo in enumerate(dist):
			emoji = emo[0]
			
			temp = dist[:i] + dist[i+1:]
			for tmp_emo in temp:
				temoji = tmp_emo[0]

				if emo[1] == tmp_emo[1]:
					if temoji.lower() in emoji.lower() or emoji.lower() in temoji.lower():
						if len(temoji.lower()) < len(emoji.lower()):
							ambiguous.append(temoji)
						else:
							ambiguous.append(emoji)

		dist = [x for x in dist if x[0] not in ambiguous]
		return dist 


	def getBlobPosTags(self, blob):
		tags = [self.pos_dic[tag[1]] if tag[1] in self.pos_dic else "common_tag" for tag in blob.tags]
		
		words_len = len(tags)
		pos_tags_percentage = dict(Counter(tags))
		for tag,freq in pos_tags_percentage.iteritems():
			pos_tags_percentage[tag] = round(float(freq) / words_len,2) * 100

		for y in self.all_tags:
			if y not in pos_tags_percentage:
				pos_tags_percentage[y] = 0

		res = {
			'pos_tags_percent' : pos_tags_percentage,
			'verb_list' : []
		}
		return res

		

	def pos_tags_distribution(self, blob, text):
		try:
			resp = PT.post_tags(text)
		except Exception as E:
			print E
			resp = self.getBlobPosTags(blob)
		
		verb_list = resp['verb_list']
		pos_tags_percentage = resp['pos_tags_percent']

		## Pos tag grade 
		score = 0
		if pos_tags_percentage['noun'] > 0:
			score += 1 
		if pos_tags_percentage['verb'] > 0:
			score += 1 
		if pos_tags_percentage['adjective'] > 0:
			score += 1 
		if score == 3:
			grade = "A+"
		elif score == 2:
			grade = "A"
		elif score == 1:
			grade = "B"
		else:
			grade = "C"

		pos_tags_percentage['grade'] = grade
		pos_tags_percentage['score'] = score
		pos_tags_percentage['verb_list'] = verb_list
		return pos_tags_percentage

	def phrases(self, proper_corpus):
		blob = TextBlob(proper_corpus)
		noun_phrases = blob.noun_phrases
		nps = Counter(noun_phrases)
		dist = sorted(nps.items(), key = operator.itemgetter(1), reverse = True)
		dist = [x for x in dist if len(x[0].split()) > 1]
		return dist

	def openCalisAPI(self, corpus):
		response = requests.post(self.calais_url, data = corpus, headers = self.headers)
		calis = response.json()
		keys = ['_typeGroup', '_type', 'name', 'score', 'relevance']

		for each in calis:
			for key, value in calis[each].iteritems():
				print key, value

	def top_questions_asked(self, sentences_proper):
		mains = {}
		for sentence in sentences_proper:
			blob = TextBlob(sentence)
			for sent in blob.sentences:
				try:
					words = self.tgu.clean_comment(sent).split()

					# Questions 			
					if len(words) > 3 and sent.endswith("?"):					
						ques = str(sent)
						if ques not in mains:
							mains[ques] = 0
						mains[ques] += 1
	
				except Exception as E:
					continue

				
		dist = sorted(mains.items(), key = operator.itemgetter(1), reverse = True)
		return dist

	def comphrensive_comment(self, sentences_proper):
		mains = {}

		for sentence in sentences_proper:
			blob = TextBlob(sentence)
			slen = len(blob.sentences)

			words = self.tgu.clean_comment(sentence).split()
			wlen = len(words)

			if wlen > 10:
				mains[sentence] = {}
				mains[sentence]["slen"] = slen
				mains[sentence]["wlen"] = wlen

		dicts = [{k: v} for (k,v) in mains.items()]
		dicts.sort(key = lambda d: (d.values()[0]['slen'], d.values()[0]['wlen'],), reverse = True)
		sente = []
		for each in dicts:
			delta = len(str([each.keys()[0]])) - len(each.keys()[0])
			if float(delta) / len(each.keys()[0]) < 1:
				sente.append(each.keys()[0])
		return sente

	def readability_grade(self, readability):
		score = 0

		FRE = readability['flesch_reading_ease']
		ASPW = readability['avg_syllables_per_word']
		ALPW = readability['avg_letter_per_word']

		# Out of 6
		if FRE >= 90:
			score += 6
		elif FRE >= 80 and FRE < 90:
			score += 5
		elif FRE >= 70 and FRE < 80:
			score += 4
		elif FRE >= 60 and FRE < 70:
			score += 3
		elif FRE >= 50 and FRE < 60:
			score += 2
		elif FRE >= 50 and FRE < 60:
			score += 1
		else:
			score += 0


		### Out of 3
		if ASPW <= 2:
			score += 3
		elif ASPW >= 2 and ASPW < 4:
			score += 2
		elif ASPW >= 4 and ASPW < 5:
			score += 1
		else:
			score += 0


		### Out of 1
		if ALPW <= 6:
			score += 1
		else:
			score += 0

		grade = self.tgu.getGrade(score)
		return grade, score



	def readability_analysis(self, text):
		words = text.split()
		wrd_dic = {}
		for wrd in words:
			wrd = "".join(a for a in wrd if a not in punctuation)
			wrd_dic[wrd] = textstat.syllable_count(wrd)
		wrd_dic = [b for b in wrd_dic if wrd_dic[b] >= 5]
		
		flesch_reading_ease = textstat.flesch_reading_ease(text)

		if flesch_reading_ease > 100:
			flesch_reading_ease = 100
		elif flesch_reading_ease < 0:
			flesch_reading_ease = 0

		syllable_count = textstat.syllable_count(text)
		avg_syllables_per_word = textstat.avg_syllables_per_word(text)
		avg_letter_per_word = textstat.avg_letter_per_word(text)

		readability = {
			"flesch_reading_ease" : flesch_reading_ease,
			"avg_syllables_per_word" : avg_syllables_per_word,
			"syllable_count" : syllable_count,
			"avg_letter_per_word" : avg_letter_per_word,
		}

		grade, score = self.readability_grade(readability)
		readability['grade'] = grade
		readability['score'] = score
		readability['difficult_words'] = wrd_dic
		return readability



	def text_analysis(self, blob, headline):
		words_len = len(headline.split())
		character_len = len(headline)

		try:
			hts = [x for x in headline.split() if str(x).startswith("#")]
		except Exception as E:
			hts = []
			print E 
			
		ht_score = 0
		if len(hts) == 0:
			ht_score = 0
		elif len(hts) == 1:
			ht_score = 7
		elif len(hts) == 2:
			ht_score = 8
		elif len(hts) == 3:
			ht_score = 9
		elif len(hts) > 3:
			ht_score = 10

		words_len_score = 0
		if words_len > 4 and words_len <= 9:
			words_len_score = 10

		elif words_len > 9 and words_len <= 12:
			words_len_score = 9

		elif words_len > 12 and words_len <= 15:
			words_len_score = 8

		elif words_len > 15 and words_len <= 20:
			words_len_score = 7

		elif words_len > 20 and words_len <= 30:
			words_len_score = 6

		elif words_len > 2 and words_len <= 4:
			words_len_score = 5

		elif words_len <= 2 or words_len > 30:
			words_len_score = 4



		grade = self.tgu.getGrade(words_len_score)
		res = {
			'words_len' : words_len,
			'words_per' : words_len_score*10,
		
			'character_len' : character_len,
			'char_per' : words_len_score*10,
		
			'ht_len' : len(hts),
			'ht_per' : ht_score*10,

			'score' : words_len_score,
			'grade' : grade,
		}
		return res

	def getSummary(self, grades):
		summary = {}
		good_grades = [x for x in grades if grades[x].startswith("A")]
		mod_grades = [x for x in grades if grades[x].startswith("B")]
		poor_grades = [x for x in grades if x not in mod_grades + good_grades]

		summary['good_sections'] = good_grades
		summary['moderate_sections'] = mod_grades
		summary['poor_sections'] = poor_grades

		if len(summary['good_sections']) == 1:
			good = "The analysis of " + good_grades[0] + " shows a good and optimal grade."
		elif len(summary['good_sections']) > 1:
			good = "Best sections of your content are - " + ", ".join(good_grades) 
		else:
			good = "None of the sections are optimal as suggested by content analyzer, Scroll down below for the detailed analysis and insights."


		if len(summary['moderate_sections']) == 1:
			mod = "The " + mod_grades[0] + " section is decently good, but it can still be improved"
		elif len(summary['moderate_sections']) > 1:
			mod = "The sections - " + mod_grades[0] + " shows a decent performance, but there is a still scope for improvement."
		else:
			mod = None


		if len(summary['poor_sections']) == 1:
			poor = "The analysis of " + poor_grades[0] + " needs to be improved, as one of the poor grade is observed. Scroll down below for the detailed report and analysis"
		elif len(summary['poor_sections']) > 1:
			poor = "The analysis shows that " + poor_grades[0] + " needs to be improved, since a lower grade in obtained"
		else:
			poor = None

		summary['good_text'] = good
		summary['mod_text'] = mod
		summary['poor_text'] = poor

		return summary

	def annotate_features(self, text):
		features = {}

		# Cleaning and Processing
		cleaned = self.tgu.clean_comment(text)
		text_blob = TextBlob(text)
		cleaned_blob = TextBlob(cleaned)
		
		## Text Readability
		readability = self.readability_analysis(text)	
		
		## Word Balance
		word_balance = self.vocabulary_analysis(cleaned, text)
		
		## Text Stats
		text_stats = self.text_analysis(cleaned_blob, text)

		## Pos Tags
		postags = self.pos_tags_distribution(text_blob, text)
		
		## Sarcasm
		sarcasm = self.tgu.text_scarsam(text)

		## Sentiment
		sentiment = self.tgu.annotate_sentiment(cleaned_blob)

		# Summary
		all_grades = {
			'Sentiment' : sentiment['grade'],
			'Pos Tags' : postags['grade'],
			'Word Balance'	: word_balance['grade'],
			'Readability' : readability['grade'],
			'Text Statistics' : text_stats['grade']
		}	
		# descriptive_summary = self.getSummary(all_grades)

		# Overall Grade
		scr = word_balance['score'] * 0.6	+ readability['score'] * 0.2 + text_stats['score'] * 0.2
		descriptive_grade = self.tgu.getGrade(scr)

		features = {
			'readability' : readability,
			'word_balance' : word_balance,
			'text_stats' : text_stats,
			'pos_tags' : postags,
			'sarcasm' : sarcasm,
			'sentiment' : sentiment,
			'descriptive_grade' : descriptive_grade,
			'descriptive_summary' : {}
		}

		return features 