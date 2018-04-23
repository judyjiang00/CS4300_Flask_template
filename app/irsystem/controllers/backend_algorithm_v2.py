from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

import requests
from math import sin, cos, sqrt, atan2, radians
from collections import Counter
from itertools import product
import random
from defs import *

def getPlaces(input_query, maxDistanceKM = -1):
	"""
	Version 2 Method
	Use SVD to expand query
	"""
	raw_query = tokenize(input_query)
	query = [stemmer.stem(w) for w in raw_query]
	query_word_expaneded = [expand_word(word) for word in query]
	#query_expanded_list = [q for q in product(*query_word_expaneded)]

	accum = np.zeros(len(data))
	for query_expanded in query_word_expaneded:
		for q in query_expanded:
			if q in vocab_idx:
				for doc in inv_idx[q]:
					accum[doc] += idf[q] * doc_mat[doc, vocab_idx[q]]
	q_norm = sqrt(sum((cnt * idf[q])**2 for q, cnt in Counter(query).items() if q in idf))
	raw_scores = accum / q_norm if q_norm > 0 else np.zeros_like(accum)


	ranking = filterRegionsWithinDistance(accum.argsort()[::-1], maxDistanceKM)
	# Filter out redundancy in regions
	filt_ranking = []
	repeated = set()
	regions = []
	scores = []
	for r in ranking:
		if len(regions) == NUM_REGIONS:
			break
		region = data[r][1]
		if region not in repeated:
			filt_ranking.append(r)
			regions.append(region)
			scores.append(int(round(raw_scores[r]**(1./7)*100)))  # some non-linear transformation
			repeated.add(region)

	snippets = get_snippets(query, filt_ranking, stems, data, sent_idx, word_sent_idx)

	# The order goes as [region name, region coordinates, snippets, list of Google places, fact dict, score]
	topPlaces = [[] for _ in range(NUM_REGIONS)]
	for i, region in enumerate(regions):
		latLong = []
		latLong.append(geocode[region.lower()]['results'][0]['geometry']['location']['lat'])
		latLong.append(geocode[region.lower()]['results'][0]['geometry']['location']['lng'])

		topPlaces[i].append(region)
		topPlaces[i].append(latLong)
		topPlaces[i].append(snippets[i])
		topPlaces[i].append(getTopPlacesInRegion(region))
		topPlaces[i].append(fact_data[region])
		topPlaces[i].append(scores[i])

	return topPlaces


def getTopPlacesInRegion(region):
	"""
	Version 2 Method
	Return Order: [Place Name, Place Url (empty string is none), Short Description]
	Return empty list if region not in wikitravel dataset
	Data Source: Wikivoyage/WikiTravel
	"""
	try:
		full_spots_list = wikitravel_place[region]
		if len(full_spots_list) > 3:
			spot_list = random.sample(full_spots_list,3)
		else:
			spot_list = full_spots_list
		out_list = [[spot[2],spot[3],spot[-1]] for spot in spot_list]
		return out_list
	except:
		return []


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

def get_snippets(query, ranking, stems, data, sent_idx, word_sent_idx):
	# Retrieve snippets from LP descriptions
	snippets = [[] for _ in range(NUM_REGIONS)]
	MAX_SNIPPETS = 3
	query_words = set(query)
	for k, rank in enumerate(ranking):
		snip = snippets[k]
		sents = sent_idx[rank]
		text = data[rank][3]
		flags = [False] * len(sents)
		for j, stem in enumerate(stems[rank]):
			if len(snip) == MAX_SNIPPETS:
				break
			if stem in query_words:
				s = word_sent_idx[rank][j]
				if not flags[s]:
					flags[s] = True
					if s == len(sents) - 1:
						snip.append(text[sents[s]:])
					else:
						snip.append(text[sents[s]:sents[s+1]])
		snippets[k] = ''.join(snip)
	return snippets


def expand_word(w, n_expansion=2):
	if w not in vocab_idx:
		return [w]
	else:
		idx = vocab_idx[w]
		sims = words_compressed.dot(words_compressed[idx,:])
		asort = np.argsort(-sims)[:n_expansion+1]
		out = [idx_to_vocab[i] for i in asort]
		return out