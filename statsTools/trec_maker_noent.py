"""
 * Created by filip on 24/09/2019

 Reads JSON files from the specified directory. Creates *.trac files containing of arbitrary document ID,
 and reply text. Writes 1000 documents per one .trac file.

 Reads file specifing used queires and creates query files for the used queries.

 Creates a query file consisting of topic number and the text of the first post in the thread. Skips queries without
 informative entities.
"""

import os
import platform
import json
import traceback
import re
from relevanceRanking.entities_info import EntityInfo, get_entity_code

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory_data = "/scratch/GW/pool0/fadamik/ehealthforum/trac/noent2/data"
    output_directory_queries = "/scratch/GW/pool0/fadamik/ehealthforum/trac/noent2/reduced-queries"
    used_queries_r_path = '/home/fadamik/Documents/used_queries_relevant_test.json'
    used_queries_n_path = '/home/fadamik/Documents/used_queries_non-relevant_test.json'

else:
    starting_directory = "D:/Downloads/json/ehealthforum/json-annotated"
    output_directory_data = "D:/Downloads/json/ehealthforum/trac/data"
    output_directory_queries = "D:/Downloads/json/ehealthforum/trac/queries"
    used_queries_r_path = 'd:/Downloads/json/ehealthforum/trac/used_queries_relevant_test.txt'
    used_queries_n_path = 'd:/Downloads/json/ehealthforum/trac/used_queries_non-relevant_test.txt'

WRITE_QUERIES = True
WRITE_DOCUMENTS = False

if WRITE_QUERIES:
    used_queries = set()

    with open(used_queries_r_path, 'r', encoding='utf8') as used_queries_file:
        contents = json.load(used_queries_file)
        used_queries.update(contents.keys())
        # for line in used_queries_file:
        #     used_queries.add(line.replace('\n', ''))

    with open(used_queries_n_path, 'r', encoding='utf8') as used_queries_file:
        contents = json.load(used_queries_file)
        used_queries.update(contents.keys())

        # for line in used_queries_file:
        #     used_queries.add(line.replace('\n', ''))

    query_file = open(os.path.join(output_directory_queries, "queries0_test.txt"), "w+", encoding="utf8")

if WRITE_DOCUMENTS:
    data_file = open(os.path.join(output_directory_data, "data1.trac"), "w+", encoding="utf8")

processed_files = 0
error_files = 0
documents_written = 0
queries_written = 0


pattern = re.compile('C[0-9]{3,}')
pattern_long = re.compile("\[\[C[0-9]+\|[\w\s]{1,}\]\]")

ef = EntityInfo()

# Walk through the input JSON data directory.
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            with open(os.path.join(root, file_name), "r", encoding="utf8") as file:
                content = json.loads(file.read())

            processed_files += 1
            if processed_files % 100 == 0:
                print("Processed files: " + str(processed_files))

            query = content['replies'][0]
            topic_no = str(content['threadId'])

            if topic_no not in used_queries:
                continue

            query_text = content['title']

            word_count = len(re.findall(r'\w+', query_text))

            if WRITE_QUERIES and word_count < 1020:
                query_file.write(
                    "<top>\n\n<num> Number: " + topic_no + "\n<title>\n" + query_text + "\n\n<desc> Description:\nNA\n\n<narr> Narrative:\nNA\n\n</top>\n")

                queries_written += 1

            # # Write out queries to a file every bunch of queries.
            # if queries_written % 3600 == 0:
            #     query_file.close()
            #     file_number = queries_written // 3600
            #     query_file = open(os.path.join(output_directory_queries, "queries" + str(file_number) + ".txt"), "w+", encoding="utf8")

            # Process all replies in the file as separate documents.
            if WRITE_DOCUMENTS:
                for index, reply in enumerate(content['replies']):
                    if index == 0:
                        continue

                    document_id = str(int(content['threadId'], base=10)) + "r" + str(index)
                    document_text = reply['postText']

                    data_file.write("<DOC>\n<DOCNO>EF-" + document_id + "</DOCNO>\n")
                    data_file.write("<TEXT>\n" + document_text + "\n</TEXT>\n")
                    data_file.write("</DOC>\n")

                    documents_written += 1

                    # Close a file (so it doesn't get too big) and open a new one every bunch of documents.
                    if documents_written % 1000 == 0:
                        data_file.close()
                        data_file = open(
                            os.path.join(output_directory_data, "data" + str(documents_written // 1000) + ".trac"),
                            "w+", encoding="utf8")

            # Write out progress every bunch of files.


        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1

if WRITE_DOCUMENTS:
    data_file.close()

if WRITE_QUERIES:
    query_file.close()
