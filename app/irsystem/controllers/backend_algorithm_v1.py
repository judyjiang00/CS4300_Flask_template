from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from defs import *

def getPlaces(input_query):
	"""
	Version 1 Method
	"""
 	raw_query = tokenize(input_query)
 	query = [stemmer.stem(w) for w in raw_query]

 	accum = np.zeros(len(data))
 	for q in query:
 		if q in vocab_idx:
 			for doc in inv_idx[q]:
 				accum[doc] += doc_mat[doc, vocab_idx[q]]
 	ranking = accum.argsort()[::-1]
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
	"""
	Version 1 Method
	Return Order: [Place Name, Place Address]
	Data Source: Google Place API data
	"""
	topPlaces = []

	sortedPlaces = sorted(google_places[region.lower()], key = lambda x: x[1], reverse = True)
	for place in sortedPlaces:
		if len(topPlaces) >= NUM_PLACES_PER_REGION:
			break
		topPlaces.append((place[0], place[2]))

	return topPlaces