import pickle
import json
import nltk
from nltk.stem.porter import *
from collections import defaultdict


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

vocab_idx = {w: i for i, w in enumerate(idx_to_vocab)}

with open("data/geo_hierarchy_dict.pickle","rb") as f:
    geo_hierarchy = pickle.load(f)

with open("data/travelAdvisories.pickle","rb") as f:
    travelAdvisories = pickle.load(f)

with open("data/temperatures.pickle","rb") as f:
    temps = pickle.load(f)

with open("data/wikitravel_spots.pickle","rb") as f:
	wikitravel_spots = pickle.load(f)

with open("data/pictures.pickle") as f: 
    	pictures = pickle.load(f)

with open('data/popularity.pickle') as f:
	popularity = pickle.load(f)

region_list = geo_hierarchy.keys()
region_set = set(region_list)

country_list = []
country_to_region = {}
for region in region_list:
	country_list += (geo_hierarchy[region].keys())
	for country in geo_hierarchy[region].keys():
		country_to_region[country] = region
country_set = set(country_list)
    
location_to_doc_idx = defaultdict(list)
for idx, row in enumerate(data):
    location_to_doc_idx[row[1].lower()].append(idx)

US_syn = ['us','usa','united states','united states of america','u.s.','u.s.a', 'america']
UK_syn = ['uk','united kingdom','britain', 'u.k.']
