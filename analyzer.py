import re, os
import matplotlib.pyplot as plt
import numpy as np
import statistics as st
from scipy import sparse as sp

def main():
	cwd = os.getcwd(); 
	#create list of documents
	document_list = list(); 

	#create list of wf_tupes (episode)
	wfepisodes = list(); 

	for filename in os.listdir(cwd+"/material"):
		#read files
		file = open(cwd+"/material/"+filename, "r", encoding="utf-8")
		lines = file.readlines()
		file.close()

		#create a set word_list (sw_list)
		document = ""
		set_words = set()

		#store N (number of documents)
		n_docs = 0

		#create a full list of types (set{terms})
		document_list = [tokenize(line.lower()) for line in lines]
		for doc in document_list: 
			n_docs += 1
			for word in doc:
				set_words.add(word)
		sw_list = list(set_words)

		#create an inverted index
		inv_index = inverted_index(sw_list)

		#create a (non-binary) tf-matrix
		tf_mat = np.zeros(shape = (len(document_list), len(set_words)))
		for x in range(len(document_list)):
			for y in range(len(document_list[x])):
				indx = inv_index[document_list[x][y]]
				tf_mat[x][indx] += 1

		#create a binary tf-matrix
		bin_tf = binarize_tf(tf_mat)

		#create an array of df(s) for each term
		df_col = np.sum(bin_tf, axis = 0)

		#calculate idf weights
		idf_weights = np.log(n_docs/df_col) 

		#change tf_mat into tf_idf matrix
		for x in range(len(set_words)):
			tf_mat[:, x] = np.multiply(tf_mat[:, x], idf_weights[x])

		#create a co-occurance matrix
		#coorc_mat = np.dot(tf_mat, np.transpose(tf_mat))

		#create a sorted word-frequency dictionary
		wf_dict = wf_create(tf_mat, set_words)

		#plot the top 20 tf-idf scorers
		#cream_list = zip(*sorted_wf_list[0:20])
		#plt.bar(next(cream_list), next(cream_list))
		#plt.xticks(rotation='vertical')
		#plt.show()
		
		point_list = list()
		for i in range(5, 305, 5):
			point_list.append((i, get_mean_at_k(set_words, i, wf_dict)))
		plot_iterable = zip(*point_list)
		plt.scatter(next(plot_iterable), next(plot_iterable))
		plt.ylabel("mean word length")
		plt.xlabel("subset of words with col-sum t > specified")
		plt.show()


def get_mean_at_k(words, topK, wf_dict):
	word_lengths = list()
	for word in words: 
		if wf_dict[word] > topK:
			word_lengths.append(len(word))
	return st.mean(word_lengths)

				
def tokenize(transcript): 
	regex = "([a-zA-Z]+)"; 
	matches = re.findall(regex, transcript, flags=0); 
	return matches;

def inverted_index(target):
	inv_indx = dict()
	for x in range(len(target)):
		inv_indx[target[x]] = x
	return inv_indx

"""
def binary_map(val):
	return 0 if val == 0 else 1
"""

#returns a binary version of the provided tf-matrix
def binarize_tf(mat):
	nonzero_coords = np.transpose(mat.nonzero())
	bin_tf = np.zeros(shape = mat.shape)
	for coords in nonzero_coords:
		x_coord = coords[0]
		y_coord = coords[1]
		bin_tf[x_coord][y_coord] = 1
	return bin_tf

#creates a wf_dict from a (non-binary) tf-matrix
#Precondition: terms MUST be a set
#Note: rounds for better display
def wf_create(mat, terms):
	col_mat = np.sum(mat, axis = 0)
	term_list = list(terms)
	wf_dict = dict.fromkeys(terms, 0)
	for x in range(0, len(terms)):
		wf_dict.update({term_list[x]: round(col_mat[x], 2)})
	return wf_dict

"""
#returns a matrix with some function applied to each element of the original (numpy) matrix mat
#note: O(n) but too slow because our matrix is too large and too sparse
def map_mat(mat, fun):
	x_len = mat.shape[0]
	y_len = mat.shape[1]
	mapped_mat = np.zeros(shape = mat.shape)
	for x in range (x_len):
		for y in range(y_len):
			mapped_mat[x][y] = fun(mat[x, y])
	return mapped_mat;
"""
	 
#generic method that returns a list of sorted tuples from a dictionary
def dict_sort (some_dict):
	return sorted(some_dict.items(), key=lambda x: x[1], reverse=True); 

main(); 