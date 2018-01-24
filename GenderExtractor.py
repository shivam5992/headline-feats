class GenderExtractor:
	def _extract_gender(self, name):
		try:
			if " " in name:
				nameis = str(name).strip().replace(" ","/")
			else:
				nameis = str(name) + "/a"
			url = "http://api.namsor.com/onomastics/api/json/gendre/" + nameis
			response = requests.post(url)
			gender = response.json()["gender"]
		except Exception as e:
			gender = "Unknown"
		return gender