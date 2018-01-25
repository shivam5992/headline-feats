import pandas as pd
import numpy as np
import collections
import random

class GenerateInsights:
	def __init__(self):
		self.df1 = pd.read_csv('InsightsEngine/dictionaries/insights/DescriptiveInsights.csv')
		self.df2 = pd.read_csv('InsightsEngine/dictionaries/insights/ToneInsights.csv')
		self.thresh = 0.40

	def get_message2(self, key1, key2):
		df = self.df2.copy()
		df = df[(df['EmotionalTone']==key1) & (df['Fills']==key2)]
		storylines = list(df['Storyline'])
		random.shuffle(storylines)
		return storylines[0]

	def get_message1(self,key,value):
		results = []
		df = self.df1.copy()
		df = df[df['feature']==key]
		df = df[(df['lower']<=value) & (df['upper']>=value)]
		if len(df)>0:
			df = df.reset_index()
			for x in df.values:
				results.append(x)
		return results
		
	def flatten(self, d, parent_key = '', sep ='_'):
		items = []
		for k, v in d.items():
			new_key = parent_key + sep + k if parent_key else k
			if isinstance(v, collections.MutableMapping):
				items.extend(self.flatten(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)

	def parse_insights(self, data):
		results = self.flatten(data, parent_key='', sep='.')
		
		summary_insights1 = []
		summary_insights2 = []
		summary_insights3 = []

		for key, value in results.items():
			if type(value) == float or type(value) == int:
				key = key.split('.')[-1]

				if key in list(self.df1['feature']):      
					results = self.get_message1(key,value)

					if results:
						clean = results[0][4]
						sub = results[0][3]
						sec = results[0][5]

						insights = [_[8] for _ in results]
						suggestions = [_[9] for _ in results]
						ideals = [_[10] for _ in results]
						
						random.shuffle(insights)
						random.shuffle(suggestions)
						random.shuffle(ideals)

						ins = insights[0]
						if ins ==  np.nan or ins == "None" or ins == "" or ins == None or len(ins) == 0:
						    ins = "Great! this section is optimal"

						if clean in ["emotional", "power", "common", "uncommon"]:
							if suggestions[0] != "None":
								summary_insights1.append(suggestions[0])
							# else:
								# summary_insights1.append(insights[0])
						
						if clean in ["readability", "syllable_density"]:
							if suggestions[0] != "None":
								summary_insights2.append(suggestions[0])
							else:
								summary_insights2.append(insights[0])
						
						if clean in ["characters", "words"]:
							if suggestions[0] != "None":
								summary_insights3.append(suggestions[0])
							else:
								summary_insights3.append(insights[0])						

						sug = suggestions[0]
						if sug ==  np.nan or sug == None or str(sug) == 'None' or len(sug) == 0:
							sug = ""

						ideal = ideals[0]
						if ideal ==  np.nan or ideal == None or str(ideal) == 'None' or len(ideal) == 0:
							ideal = ""

						if "insight" not in data[sub]:
							data[sub]['insight'] = {}
						if sec not in data[sub]['insight']:
							data[sub]['insight'][clean] = {}

						data[sub]['insight'][clean] = {'insight' : ins, 'suggestion' : sug, "ideal" : ideal} 
	 	if not summary_insights1:
	 		summary_insights1.append("Your Word Balance is ideal.")

	 	random.shuffle(summary_insights1)
	 	random.shuffle(summary_insights1)
	 	random.shuffle(summary_insights1)

	 	summary_insights = []
	 	summary_insights.append(summary_insights1[0])
	 	summary_insights.append(summary_insights2[0])
	 	summary_insights.append(summary_insights3[0])
		data['descriptive_summary']['insight'] = summary_insights


		### Special Handelling for POS Tags 
		pos_ins = []
		if "insight" not in data["pos_tags"]:
			data["pos_tags"]["insight"] = "Great, Your headline has very good structure and perfect part of speech balance."
			data["pos_tags"]["suggestion"] = ""
		else:
			for pos, it in data['pos_tags']['insight'].iteritems():
				pos_ins.append([it['insight'], it['suggestion']])
			random.shuffle(pos_ins)
			data['pos_tags']['insight'] = pos_ins[0][0]
			data['pos_tags']['suggestion'] = pos_ins[0][1]

		return data

	def parse_emotional_insight(self, data):
		data['insight'] = {}
		emotional_tone = data['tone_categories'][0]['tones']
		emotional_tone = sorted(emotional_tone, key=lambda k: k['score'], reverse = True) 
	
		if emotional_tone[0]['score'] > self.thresh:
			tone_name = emotional_tone[0]['tone_name']
		else:
			tone_name = 'None'
		
		data['insight']['EmotionalTone'] = {
		'message' : self.get_message2('EmotionalTone', tone_name),
		'name' : tone_name
		} 

		social_tone = data['tone_categories'][2]['tones']
		print social_tone
		social_tone = [x for x in social_tone if x['tone_name'] != "Emotional Range"]

		social_tone = sorted(social_tone, key=lambda k: k['score'], reverse = True)


		if social_tone[0]['score'] > self.thresh:
			tone_name = social_tone[0]['tone_name']
		else:
			tone_name = 'None' 
		
		tone_name = social_tone[0]['tone_name']
		
		data['insight']['SocialTone'] = {
			'message' : self.get_message2('SocialTone', tone_name),
			'name' : tone_name 
		}   

		return data
