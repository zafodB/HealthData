'''
 * Created by filip on 24/09/2019
'''

import pandas as pd
import os, json, traceback


df = pd.read_csv("D:/Downloads/json/ehealthforum/pairs/actual/actual-pairs-filtered2.txt", sep='\t')

file = open("D:/Downloads/json/ehealthforum/data.trac", "w+", encoding="utf8")
# file = open("D:/Downloads/json/ehealthforum/topics.txt", "w+", encoding="utf8")

queries_set = set()
query_map = {}

for index, item in df.iterrows():
    query_text = str(item['original text'])
    doc_id = "EF-" + str(index)

    if query_text not in queries_set:
        queries_set.add(query_text)
        query_map[query_text] = [doc_id]
    else:
        query_map[query_text].append(doc_id)

    file.write("<DOC>\n<DOCNO>EF-" + str(doc_id) + "</DOCNO>\n")
    file.write("<TEXT>\n" + str(item['document text']) + "\n</TEXT>\n")
    file.write("</DOC>\n")


file.close()

file = open("D:/Downloads/json/ehealthforum/topics.txt", "w+", encoding="utf8")
file_maps = open("D:/Downloads/json/ehealthforum/topic-map.txt", "w+", encoding="utf8")

for index, query in enumerate(queries_set):
    query_id = str(1000 + index)

    file_maps.write(query_id)
    for id in query_map[query]:
        file_maps.write("\t" + id)

    file_maps.write("\n")

    file.write("<top>\n\n<num> Number: " + query_id + "\n<title>\n" +
               query + "\n\n<desc> Description:\nNA\n\n<narr> Narrative:\nNA\n\n</top>\n")

    # if len(query) > 100:
    #     print(query[0:100] + str(query_map[query]))
    # else:
    #     print(query + str(query_map[query]))

file.close()
file_maps.close()
