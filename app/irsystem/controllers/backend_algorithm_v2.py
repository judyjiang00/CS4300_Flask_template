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
	#print input_query[0]
	#print input_query[1]
	"""
	Params:
		input_query: tuple of (location query, activity query)
	Version 2 Method
	Use SVD to expand query
	"""
	activity_query = tokenize(input_query[1])
	location_query = input_query[0].split(' ')
	location_query = [ll.lower() for ll in location_query]
	query = [stemmer.stem(w) for w in activity_query]
	query_word_expaneded = [expand_word(word) for word in query]

	accum = np.zeros(len(data))
	#print query_word_expaneded
	for query_expanded in query_word_expaneded:
		for q in query_expanded:
			if q in vocab_idx:
				for doc in inv_idx[q]:
					accum[doc] += idf[q] * doc_mat[doc, vocab_idx[q]]
	q_norm = sqrt(sum((cnt * idf[q])**2 for q, cnt in Counter(query).items() if q in idf))
	raw_scores = accum / q_norm if q_norm > 0 else np.zeros_like(accum)


	ranking_distance = filterRegionsWithinDistance(accum.argsort()[::-1], maxDistanceKM) #input is idx instead of list of regions
	ranking_hierarchy_by_region = []
	#print location_query
	for ll in location_query:
		ranking_hierarchy_by_region += filterRegionWithHierarchy(ll) #list of regions
	#print ranking_hierarchy_by_region
	ranking_hierarchy = []
	for place in ranking_hierarchy_by_region:
		ranking_hierarchy += location_to_doc_idx[place]
	#TODO
	if activity_query == []:
		ranking = ranking_hierarchy
	elif location_query == ['']:
		ranking = ranking_distance
	else:
		ranking = list(set(ranking_hierarchy).intersection(set(ranking_distance)))
	#print ranking
	ranking = sorted(ranking, key=lambda x:accum[x])[::-1]
	#print ranking
	#print ranking[:20]
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
	#print regions
	snippets = get_snippets(query, filt_ranking, stems, data, sent_idx, word_sent_idx)

	regions = [r for r in regions if r != 'Yugoslavia']
	# The order goes as [region name, region coordinates, snippets, list of Google places, fact dict, score]
	topPlaces = [[] for _ in range(len(regions))]
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

	#print len(regions)
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
		for spot in spot_list:
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


def filterRegionWithHierarchy(location):
	"""
    When input is a destinaiton with higher granualrity:
    	output a list of destinations under the same region
    """
	out = []
	if location == 'asia':
		lookup_key = [i for i in region_list if 'asia' in i]
	elif location == 'india':
		lookup_key = ['indian subcontinent']
	elif location == 'australia':
		lookup_key = ['australasia']
	else:
		lookup_key = [location]


	if lookup_key[0] in region_list:
		for region in lookup_key:
			tmp_out = geo_hierarchy[region].keys()
			out += tmp_out
			for country in tmp_out:
				out += geo_hierarchy[region][country]
		out += lookup_key
		return out
	elif lookup_key[0] in country_list:
		country = lookup_key[0]
		region = country_to_region[country]
		out += geo_hierarchy[region][country]
		out = out + lookup_key
		return out
	else:
		return lookup_key

def filterRegionsWithinDistance(regionIndices, maxDistanceKM = -1):
	if maxDistanceKM == -1:
		return regionIndices

	userLat, userLong = getUsersLatLong()
	filteredRegionIndices = []

	for regionIndex in regionIndices:
		region = data[regionIndex][1]
		lat = geocode[region.lower()]['results'][0]['geometry']['location']['lat']
		lon = geocode[region.lower()]['results'][0]['geometry']['location']['lng']
		if distBetweenLatLongKM(userLat, userLong, lat, lon) <= maxDistanceKM:
			filteredRegionIndices.append(region)

	return filteredRegionIndices

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
	#print snippets
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
