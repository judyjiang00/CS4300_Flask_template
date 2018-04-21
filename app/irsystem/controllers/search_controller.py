from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

import pickle
import json
import nltk
from nltk.stem.porter import *
import requests
from math import sin, cos, sqrt, atan2, radians

NUM_REGIONS = 10
NUM_PLACES_PER_REGION = 3

stemmer = PorterStemmer()

project_name = "Where Next - A Travel Destination Recommendation System"
net_id = "Wanming Hu: wh298, Smit Jain: scj39, Judy Jiang: jj353, Noah Kaplan: nk425, Tatsuhiro Koshi: tk474"

with open("data/google_place.pickle", "rb") as f:
	google_places = pickle.load(f)

with open("data/LP_raw.pickle","rb") as f:
	data = pickle.load(f)

with open("data/inv_idx.pickle","rb") as f:
	inv_idx = pickle.load(f)

with open("data/tfidf_mat.pickle","rb") as f:
	doc_mat = pickle.load(f)

with open("data/vocab_idx.pickle","rb") as f:
	vocab_idx = pickle.load(f)

with open('data/stems.pickle', 'rb') as f:
	stems = pickle.load(f)

with open('data/word_sent_idx.pickle', 'rb') as f:
	word_sent_idx = pickle.load(f)

with open('data/sent_idx.pickle', 'rb') as f:
	sent_idx = pickle.load(f)

with open('data/destination_geocode.json') as f:
	geocode = json.load(f)

with open('data/map_geo_data.json') as f:
	map_geo = json.load(f)

@irsystem.route('/', methods=['GET'])
def search():
	#query = request.args.get('search')
	output_message = ""
	activity_query = request.args.get('activity')
	location_query = request.args.get('location')
	description_query = request.args.get('description')
	system_version = request.args.get('version')

	if system_version == "v1":
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)	

		results = getPlaces(output_tupes[0] + " " + output_tupes[1])	

		return render_template('search.html', activity_query = activity_query, 
			location_query = location_query, 
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""), 
			results = results,
			map_geo = map_geo,
			version = system_version)
	else:
		# change this to the newer version of backend system
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)	

		results = getPlaces(output_tupes[0] + " " + output_tupes[1])	

		return render_template('search.html', activity_query = activity_query, 
			location_query = location_query, 
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""), 
			results = results,
			map_geo = map_geo,
			version = system_version)


def getPlaces(input_query, maxDistanceKM = -1):
	raw_query = tokenize(input_query)
	query = [stemmer.stem(w) for w in raw_query]

	accum = np.zeros(len(data))
	for q in query:
		if q in vocab_idx:
			for doc in inv_idx[q]:
				accum[doc] += doc_mat[doc, vocab_idx[q]]
	ranking = filterRegionsWithinDistance(accum.argsort()[::-1], maxDistanceKM)
	filt_ranking = []
	repeated = set()
	regions = []
	for r in ranking:
		if len(regions) == NUM_REGIONS:
			break
		region = data[r][1]
		if region not in repeated:
			filt_ranking.append(r)
			regions.append(region)
			repeated.add(region)

	# Retrieve snippets from LP descriptions
	snippets = [[] for _ in range(NUM_REGIONS)]
	MAX_SNIPPETS = 3
	query_words = set(query)
	for k, r in enumerate(filt_ranking[:NUM_REGIONS]):
		snip = snippets[k]
		sents = sent_idx[r]
		text = data[r][3]
		flags = [False] * len(sents)
		for j, stem in enumerate(stems[r]):
			if len(snip) == MAX_SNIPPETS:
				break
			if stem in query_words:
				s = word_sent_idx[r][j]
				if not flags[s]:
					flags[s] = True
					if s == len(sents) - 1:
						snip.append(text[sents[s]:])
					else:
						snip.append(text[sents[s]:sents[s+1]])
		snippets[k] = ''.join(snip)

	# The order goes as [region name, region coordinates, snippets, list of Google places]
	topPlaces = [[] for _ in range(NUM_REGIONS)]
	for i, region in enumerate(regions):
		latLong = []
		latLong.append(geocode[region.lower()]['results'][0]['geometry']['location']['lat'])
		latLong.append(geocode[region.lower()]['results'][0]['geometry']['location']['lng'])

		topPlaces[i].append(region)
		topPlaces[i].append(latLong)
		topPlaces[i].append(snippets[i])
		topPlaces[i].append(getTopPlacesInRegion(region))

	return topPlaces

def getTopPlacesInRegion(region):
	topPlaces = []
	
	sortedPlaces = sorted(google_places[region.lower()], key = lambda x: x[1], reverse = True)
	for place in sortedPlaces:
		if len(topPlaces) >= NUM_PLACES_PER_REGION:
			break
		topPlaces.append((place[0], place[2]))
	
	return topPlaces

def tokenize(sent):
	return re.findall('[a-zA-Z]+', sent)

def getUsersLatLong():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']
    return lat, lon

def distBetweenLatLongKM(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    
    return distance

def filterRegionsWithinDistance(regions, maxDistanceKM = -1):
	if maxDistanceKM == -1:
		return regions

	userLat, userLong = getUsersLatLong()
	filteredRegions = []

	for region in regions:
		lat = geocode[region.lower()]['results'][0]['geometry']['location']['lat']
		lon = geocode[region.lower()]['results'][0]['geometry']['location']['lng']
		if distBetweenLatLongKM(userLat, userLong, lat, lon) <= maxDistanceKM:
			filteredRegions.append(region)

	return filteredRegions