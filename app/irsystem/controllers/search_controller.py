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
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = getPlaces(query)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

def getPlaces(input_query):
	raw_query = tokenize(input_query)
	query = [stemmer.stem(w) for w in raw_query]

	accum = np.zeros(len(data))
	for q in query:
		if q in vocab_idx:
			for doc in inv_idx[q]:
				accum[doc] += doc_mat[doc, vocab_idx[q]]
	ranking = accum.argsort()[::-1]
	regions = []

	for r in ranking:
		if len(regions) >= NUM_REGIONS:
			break
		regions.append(data[r][1])

	return regions

def tokenize(sent):
    return re.findall('[a-zA-Z]+', sent)