from app.irsystem.models.helpers import *

import requests
from math import sin, cos, sqrt, atan2, radians
from collections import Counter
from itertools import product
import random
import datetime
from requests.exceptions import ConnectionError
from defs import *
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def getPlaces(input_query, max_distance):
	#print input_query[0]
	#print input_query[1]
	"""
	Params:
		input_query: tuple of (location query, activity query)
		max_distance: max distance from user's current location that query should consider (in KM)
	Version 2 Method
	Use SVD to expand query
	"""

	activity_query = tokenize(input_query[1])
	location_query = input_query[0].lower()
	queryMaxDistance = int(max_distance)

	country_flag = (location_query in country_set)
	if activity_query != []:
		query = [stemmer.stem(w) for w in activity_query]
		query_word_expanded = [expand_word(word) for word in query]
		query_word_expanded = [item for sublist in query_word_expanded for item in sublist]
		query_word_expanded = set(query_word_expanded+query)
	else:
		query = []
		query_word_expanded = []

	accum = np.zeros(len(data))
	#print query_word_expanded
	for query_expanded in query_word_expanded:
		for q in query_expanded:
			if q in vocab_idx:
				for doc in inv_idx[q]:
					accum[doc] += idf[q] * doc_mat[doc, vocab_idx[q]]
	q_norm = sqrt(sum((cnt * idf[q])**2 for q, cnt in Counter(query).items() if q in idf))
	raw_scores = accum / q_norm if q_norm > 0 else np.zeros_like(accum)

	ranking_distance = filterRegionsWithinDistance(accum.argsort()[::-1], queryMaxDistance) #input is idx instead of list of regions
	ranking_hierarchy_by_region = filterRegionWithHierarchy(location_query)
	
	ranking_hierarchy = []
	for place in ranking_hierarchy_by_region:
		ranking_hierarchy += location_to_doc_idx[place]
	#TODO
	if activity_query == []:
		ranking = list(set(ranking_hierarchy).intersection(set(ranking_distance)))
	elif location_query == ['']:
		ranking = ranking_distance
	else:
		ranking = list(set(ranking_hierarchy).intersection(set(ranking_distance)))
	
	ranking = accum.argsort()[::-1]
	
	# Filter out redundancy in regions
	filt_ranking = []
	repeated = set()
	regions = []
	scores = []
	for r in ranking:
		if len(regions) == NUM_REGIONS:
			break
		region = data[r][1]
		#print region
		#print region.lower() in country_list
		if country_flag and (region.lower() in country_set):
			continue
		elif region not in repeated:
			filt_ranking.append(r)
			regions.append(region)
			scores.append(int(round(raw_scores[r]**(1./7)*100)))  # some non-linear transformation
			repeated.add(region)
	#print regions
	snippets = get_snippets(query_expanded, filt_ranking, stems, data, sent_idx, word_sent_idx)

	regions = [r for r in regions if r != 'Yugoslavia']
	# The order goes as [region name, region coordinates, snippets, list of Google places, fact dict, score]
	topPlaces = [[] for _ in range(len(regions))]
	userLat, userLong, connected = getUsersLatLong()

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
		topPlaces[i].append(getWeatherSnippetForRegion(region.lower()))
		topPlaces[i].append(getTravelAdvisory(region))
		if connected:
			topPlaces[i].append(distBetweenLatLongKM(userLat, userLong, latLong[0], latLong[1]))
		else:
			topPlaces[i].append(-1.0)
		topPlaces[i].append(getTopQueryPlaceInRegion(region,list(query_word_expanded)))

	#print len(regions)
	return topPlaces



def getTopQueryPlaceInRegion(region,query_word_expanded):
	"""
	Final version method
	Return: list of spots that's most relevant to query based on spot description
	"""
	if query_word_expanded == []:
		return []
	try:
		concat_query = [q + " " for q in query_word_expanded]
		full_spots_list = wikitravel_spots[region]
		description = [spot[2] for spot in full_spots_list]
		#vecotrize description
		vect = TfidfVectorizer(max_df=0.8, analyzer='word', stop_words='english')
		tfidf_mat = vect.fit_transform(concat_query + description)
		cosine_sim = cosine_similarity(tfidf_mat[0:1], tfidf_mat)[0]
		top_idx = np.argsort(cosine_sim)[::-1][1:4]
		top_idx = [idx for idx in top_idx if cosine_sim[idx] != 0]
		if top_idx == []:
			return []
		spots = [full_spots_list[idx] for idx in top_idx]
		return spots
	except:
		return []


def getTopPlacesInRegion(region):
	"""
	Version 2 Method
	Return Order: [Place Name, Place Url (empty string is none), Short Description]
	Return empty list if region not in wikitravel dataset
	Data Source: Wikivoyage/WikiTravel
	"""
	try:
		full_spots_list = wikitravel_spots[region]
		out_list = []
		if len(full_spots_list) > 3:
			spot_list = random.sample(full_spots_list,3)
		else:
			spot_list = full_spots_list
		for spot in spot_list:
			out_list.append(spot)
		return out_list
	except:
		return []


def tokenize(sent):
	return re.findall('[a-zA-Z]+', sent)

def getUsersLatLong():
	try:
		send_url = 'http://freegeoip.net/json'
		r = requests.get(send_url)
		j = json.loads(r.text)
		lat = j['latitude']
		lon = j['longitude']
		return lat, lon, True
	except ConnectionError as e:
		return 0, 0, False

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


	if lookup_key[0] in region_set:
		for region in lookup_key:
			tmp_out = geo_hierarchy[region].keys()
			out += tmp_out
			for country in tmp_out:
				out += geo_hierarchy[region][country]
		out += lookup_key
		return out
	elif lookup_key[0] in country_set:
		country = lookup_key[0]
		region = country_to_region[country]
		out += geo_hierarchy[region][country]
		out = out + lookup_key
		return out
	else:
		return lookup_key

def filterRegionsWithinDistance(regionIndices, maxDistanceKM):
	if maxDistanceKM == 0:
		return regionIndices

	userLat, userLong, connected = getUsersLatLong()
	filteredRegionIndices = []

	if connected:
		for regionIndex in regionIndices:
			region = data[regionIndex][1]
			if region.lower() in geocode:
				lat = geocode[region.lower()]['results'][0]['geometry']['location']['lat']
				lon = geocode[region.lower()]['results'][0]['geometry']['location']['lng']
				if distBetweenLatLongKM(userLat, userLong, lat, lon) <= maxDistanceKM:
					filteredRegionIndices.append(regionIndex)
		return filteredRegionIndices
	else:
		return regionIndices

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

def convertCToFAndRound(c):
    return int(round(9.0/5.0 * c + 32, 0))

def getTravelAdvisory(region):
    if region in travelAdvisories:
        return travelAdvisories[region]
    else:
        return "No current travel advisory"

def getWeatherSnippetForRegion(region):
    now = datetime.datetime.now()
    nowMonth = now.strftime("%B")
    if (region, now.month-1) not in temps:
    	return ""
    else:
	    return "Average temperature in " + str(nowMonth) + ": " + str(convertCToFAndRound(temps[(region, now.month-1)][1])) + \
	        " F. Historical low and high temperatures in " + str(nowMonth) + ": " + str(convertCToFAndRound(temps[(region, now.month-1)][0])) + \
	        " F and " + str(convertCToFAndRound(temps[(region, now.month-1)][2])) + " F."

