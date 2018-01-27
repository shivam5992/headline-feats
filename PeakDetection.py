import numpy as np
import peakutils
from operator import itemgetter

class PeakDetection:
	def detect_peaks(self, oneD):
		cb = np.array(oneD)
		indexes = peakutils.indexes(cb, thres=0.02/max(cb), min_dist=0)

		mains = []
		for index in indexes:
			left = oneD[index] - oneD[index - 1]
			right = oneD[index] - oneD[index + 1] 

			doc = {
			'index' : index,
			'left' : left,
			'right' : right,
			'both' : left + right
			}
			mains.append(doc)
		newlist = sorted(mains, key = lambda user: (user['both'], user['left'], user['right']), reverse = True)
		indexes = [x['index'] for x in newlist][:3]
		return indexes

	def correlation(self, indexes, oneD):

		#### Event Level Correlations 
		# Date + Keyword ====> News 
		# Date + Keyword ====> Google Trends

		#### What so special about this Date 
		## By analysing the data , find out the features that lead to this anamoly + this rise 
		## -- All posts that lead to this number ?
		## Difference in Current posts vs previous day

		# Count - Hashtags | Words etc
		# Sentiment - Hashtags | Words | Users | Influencers etc 

		# - EDA Insights

		'''
		Why engagements were higher 
		'''




PD = PeakDetection()