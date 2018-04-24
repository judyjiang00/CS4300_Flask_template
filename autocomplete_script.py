from collections import OrderedDict
import pickle

# Generate trie as multi-layer dictionary
# List of regions taken from data matrix col 1 comma col 0
def save_trie(data, file):
    city_list = sorted(set(', '.join([row[1], row[0]]).lower() for row in data))
    region_trie = OrderedDict()  # This object should be pickled and stored
    for name in city_list:
        root = region_trie
        for char in name[:-1]:
            if char not in root:
                root[char] = OrderedDict()
            root = root[char]
        root[name[-1]] = name
    with open(file, 'wb') as f:
        pickle.dump(region_trie, f)


# Main search function
def search_trie(trie, query, seen=None):
    if seen is None:
        seen = set()
    output = []
    output += search_trie_util(trie, query, seen)
    if query:
        for val in trie.values():
            if type(val) is OrderedDict:
                output += search_trie(val, query, seen)
    return output


# Search trie recursively
def search_trie_util(trie, query, seen):
    output = []
    # Query has been exhaustively matched
    if not query:
        # Hit a leaf
        if type(trie) is not OrderedDict:
            if trie not in seen:
                seen.add(trie)
                output.append(trie)
            return output
        # Have a tree, recurse on children
        for val in trie.values():
            output += search_trie_util(val, query, seen)
        return output
    # More query to match, match greedily
    q = query[0]
    if type(trie) is OrderedDict and q in trie:
        output += search_trie_util(trie[q], query[1:], seen)
    return output
            