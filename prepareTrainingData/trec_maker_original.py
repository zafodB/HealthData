"""
 * Created by filip on 24/09/2019

 Reads JSON files from the specified directory. Creates *.trac files containing of arbitrary document ID,
 reply text and other information. Writes 1000 documents per 1 .trac file.

 Creates a query file consisting of topic number and the text of the first post in the thread.

 Creates a map file mapping queries to documents.
"""

import os
import platform
import json
import traceback
import re
from prepareTrainingData.EntityInfo.entities_info import EntityInfo, get_entity_code

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory_data = "/scratch/GW/pool0/fadamik/ehealthforum/trac/data"
    output_directory_maps = "/scratch/GW/pool0/fadamik/ehealthforum/trac/maps"
    output_directory_queries = "/scratch/GW/pool0/fadamik/ehealthforum/trac/queries"

else:
    starting_directory = "D:/Downloads/json/ehealthforum/json-annotated"
    output_directory_data = "D:/Downloads/json/ehealthforum/trac/data"
    output_directory_maps = "D:/Downloads/json/ehealthforum/trac/maps"
    output_directory_queries = "D:/Downloads/json/ehealthforum/trac/queries"


processed_files = 0
error_files = 0
documents_written = 0
queries_written = 0

data_file = open(os.path.join(output_directory_data, "data1.trac"), "w+", encoding="utf8")
maps_file_2 = open(os.path.join(output_directory_maps, "topic-map2.txt"), "w+", encoding="utf8")
maps_file_3 = open(os.path.join(output_directory_maps, "topic-map3.txt"), "w+", encoding="utf8")
query_file = open(os.path.join(output_directory_queries, "queries0.txt"), "w+", encoding="utf8")

pattern = re.compile('C[0-9]{3,}')
pattern_long = re.compile("\[\[C[0-9]+\|[\w\s]{1,}\]\]")

ef = EntityInfo()

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            content = json.loads(file.read())
            file.close()

            query = content['replies'][0]
            topic_no = str(content['threadId'])

            entities_string = ""

            if 'annotationsFull' in query:
                for annotation in query['annotationsFull']:
                    entity = re.search(pattern, annotation)

                    if ef.is_informative_entity(entity.group()):
                        entities_string += ' ' + entity.group()

            query_text = content['title'] + entities_string

            word_count = len(re.findall(r'\w+', query_text))

            if word_count > 1020:
                print("too many words")
                continue

            query_file.write(
                "<top>\n\n<num> Number: " + topic_no + "\n<title>\n" + query_text + "\n\n<desc> Description:\nNA\n\n<narr> Narrative:\nNA\n\n</top>\n")
            # print("Wrote query")
            queries_written += 1

            if queries_written % 3600 == 0:
                query_file.close()
                file_number = queries_written // 3600
                query_file = open(os.path.join(output_directory_queries, "queries" + str(file_number) + ".txt"), "w+", encoding="utf8")

            maps_file_2.write(topic_no)
            maps_file_3.write(topic_no)

            for index, reply in enumerate(content['replies']):
                if index == 0:
                    continue

                document_id = str(int(content['threadId'], base=10)) + "r" + str(index)

                if 'annotatedText' not in reply:
                    document_text = reply['postText']
                else:
                    document_text = pattern_long.sub(get_entity_code, reply['annotatedText'])

                data_file.write("<DOC>\n<DOCNO>EF-" + document_id + "</DOCNO>\n")
                data_file.write("<TEXT>\n" + document_text + "\n</TEXT>\n")
                data_file.write("</DOC>\n")

                maps_file_2.write("\t" + document_id)

                if (reply['postThankYouCount'] > 0 or reply['postHelpfulCount'] > 0 or reply['postSupportCount'] > 0 or
                        reply['mdReply']):
                    maps_file_3.write("\t" + document_id)

                documents_written += 1

                if documents_written % 1000 == 0:
                    data_file.close()
                    data_file = open(
                        os.path.join(output_directory_data, "data" + str(documents_written // 1000) + ".trac"),
                        "w+", encoding="utf8")

            maps_file_2.write('\n')

            processed_files += 1

            # if processed_files % 1000 == 0:
            #     query_file.close()
            #     query_file = open(
            #         os.path.join(output_directory_queries, "topic" + str(processed_files // 1000) + ".txt"),
            #         "w+", encoding="utf8")

            # if processed_files % 100000 == 0:
            #     maps_file.close()
            #     maps_file = open(os.path.join(output_directory_maps, "map-qrels" + str(processed_files // 100000) + ".txt"),
            #                      "w+", encoding="utf8")

            if processed_files % 100 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1

data_file.close()
query_file.close()
maps_file_2.close()
