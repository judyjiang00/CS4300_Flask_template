from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

import pickle
import nltk
from nltk.stem.porter import *

NUM_REGIONS = 10
NUM_PLACES_PER_REGION = 3

stemmer = PorterStemmer()

project_name = "Where Next - A Travel Destination Recommendation System"
net_id = "Wanming Hu: wh298, Smit Jain: scj39, Judy Jiang: jj353, Noah Kaplan: nk425, Tatsuhiro Koshi: tk474"

google_place_pickle = open("data/google_place.pickle","rb")
google_places = pickle.load(google_place_pickle)

lp_raw_pickle = open("data/LP_raw.pickle","rb")
data = pickle.load(lp_raw_pickle)

inv_idx_pickle = open("data/inv_idx.pickle","rb")
inv_idx = pickle.load(inv_idx_pickle)

tfidf_mat_pickle = open("data/tfidf_mat.pickle","rb")
doc_mat = pickle.load(tfidf_mat_pickle)

vocab_idx_pickle = open("data/vocab_idx.pickle","rb")
vocab_idx = pickle.load(vocab_idx_pickle)

@irsystem.route('/', methods=['GET'])
def search():
	#query = request.args.get('search')
	output_message = ""
	activity_query = request.args.get('activity')
	location_query = request.args.get('location')
	description_query = request.args.get('description')


	if not (location_query):
		location_query = ""
	if not (description_query):
		description_query = ""
	output_tupes = (location_query, description_query)		

	return render_template('search.html', activity_query = activity_query, 
		location_query = location_query, 
		description_query= description_query,
		output_message = (output_tupes[0] == "" and output_tupes[1] == ""))

	print(getPlaces(output_tupes[0] + " " + output_tupes[1]))



def getPlaces(input_query):
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

	topPlaces = []
	for region in regions:
		topPlaces.append(getTopPlacesInRegion(region))

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