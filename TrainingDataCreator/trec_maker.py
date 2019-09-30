"""
 * Created by filip on 24/09/2019

 Reads JSON files from the specified directory. Creates *.trac files containing of arbitrary document ID,
 reply text and other information. Writes 1000 documents per 1 .trac file.

 Creates a query file consisting of topic number and the text of the first post in the thread.

 Creates a map file mapping queries to documents.
"""


import os, json, traceback

starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3/"
# starting_directory = "D:/Downloads/json/ehealthforum/json-sorted"
output_directory_data = "/scratch/GW/pool0/fadamik/ehealthforum/trac/data"
# output_directory_data = "D:/Downloads/json/ehealthforum/"
output_directory_maps = "/scratch/GW/pool0/fadamik/ehealthforum/trac/maps"
# output_directory_maps = "D:/Downloads/json/ehealthforum/trac/maps"
output_directory_queries = "/scratch/GW/pool0/fadamik/ehealthforum/trac/queries"
# output_directory_queries = "D:/Downloads/json/ehealthforum/trac/queries"

processed_files = 0
error_files = 0
documents_written = 0

data_file = open(os.path.join(output_directory_data, "data1.trac"), "w+", encoding="utf8")
maps_file = open(os.path.join(output_directory_maps, "topic-map1.txt"), "w+", encoding="utf8")
query_file = open(os.path.join(output_directory_queries, "topic1.txt"), "w+", encoding="utf8")

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            content = json.loads(file.read())
            file.close()

            query = content['replies'][0]
            topic_no = str(content['threadId'])

            query_file.write("<top>\n\n<num> Number: " + topic_no + "\n<title>\n" + query[
                'postText'] + "\n\n<desc> Description:\nNA\n\n<narr> Narrative:\nNA\n\n</top>\n")

            maps_file.write(topic_no)

            for index, reply in enumerate(content['replies']):
                if index == 0:
                    continue

                document_id = "EF-" + str(int(content['threadId'], base=10) * 10 + index)

                data_file.write("<DOC>\n<DOCNO>EF-" + document_id + "</DOCNO>\n")
                data_file.write("<TEXT>\n" + str(reply['postText']) + "\n</TEXT>\n")
                data_file.write("<doctitle>" + content['title'] + "</doctitle>")
                data_file.write("</DOC>\n")

                maps_file.write("\t" + document_id)

                documents_written += 1

                if documents_written % 1000 == 0:
                    data_file.close()
                    data_file = open(
                        os.path.join(output_directory_data, "data" + str(documents_written // 1000) + ".trac"),
                        "w+", encoding="utf8")

            maps_file.write('\n')

            processed_files += 1

            if processed_files % 1000 == 0:
                query_file.close()
                query_file = open(
                    os.path.join(output_directory_queries, "data" + str(processed_files // 1000) + ".trac"),
                    "w+", encoding="utf8")

            if processed_files % 100000 == 0:
                maps_file.close()
                maps_file = open(os.path.join(output_directory_maps, "data" + str(processed_files // 100000) + ".trac"),
                                 "w+", encoding="utf8")

            if processed_files % 100 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1

data_file.close()
query_file.close()
maps_file.close()
