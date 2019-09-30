'''
 * Created by filip on 30/09/2019
'''

import os, sys

anserini_root = 'd:/documents/python/anserini'

sys.path.append(os.path.join(anserini_root, "src/main/python"))

from src.main.python.pyserini.search import pysearch

searcher = pysearch.SimpleSearcher('d:/downloads/json/ehealthforum/index/lucene-index.ehealthforum.pos+docvectors+rawdocs')

# To additionally configure search options, such as using BM25+RM3:
searcher.set_bm25_similarity(0.9, 0.4)
searcher.set_rm3_reranker(10, 10, 0.5)

hits = searcher.search('hubble space telescope')

# the docid of the 1st hit
print(hits[0].docid)

# the internal Lucene docid of the 1st hit
print(hits[0].ldocid)

# the score of the 1st hit
print(hits[0].score)

# the full document of the 1st hit
print(hits[0].content)


