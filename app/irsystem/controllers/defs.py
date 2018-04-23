import pickle
import json
import nltk
from nltk.stem.porter import *

NUM_REGIONS = 10
NUM_PLACES_PER_REGION = 3

stemmer = PorterStemmer()

def tokenize(sent):
	return re.findall('[a-zA-Z]+', sent)

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

with open('data/fact_data.pickle') as f:
	fact_data = pickle.load(f)

with open('data/idf.pickle') as f:
	idf = pickle.load(f)

with open('data/words_compressed.pickle') as f:
	words_compressed = pickle.load(f)

with open('data/idx_to_vocab.pickle') as f:
	idx_to_vocab = pickle.load(f)

with open('data/wikitravel_place.pickle') as f:
	wikitravel_place = pickle.load(f)