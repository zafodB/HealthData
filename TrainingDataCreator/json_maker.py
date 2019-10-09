'''
 * Created by filip on 30/09/2019
'''

import os
import json
import re
import traceback

starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated2/"
# starting_directory = "D:/Downloads/json/ehealthforum/json-annotated"
output_directory_data = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/data"
# output_directory_data = "D:/Downloads/json/ehealthforum/trac/json/data"
output_directory_maps = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/maps"
# output_directory_maps = "D:/Downloads/json/ehealthforum/trac/json/maps"
output_directory_queries = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/queries"
# output_directory_queries = "D:/Downloads/json/ehealthforum/trac/json/queries"

processed_files = 0
error_files = 0
documents_written = 0

data_file = open(os.path.join(output_directory_data, "data1.json"), "w+", encoding="utf8")
maps_file_2 = open(os.path.join(output_directory_maps, "maps2_0.txt"), "w+", encoding="utf8")
maps_file_3 = open(os.path.join(output_directory_maps, "maps3_0.txt"), "w+", encoding="utf8")
query_file = open(os.path.join(output_directory_queries, "query0.txt"), "w+", encoding="utf8")

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

            maps_file_2.write(topic_no)
            maps_file_3.write(topic_no)

            for index, reply in enumerate(content['replies']):
                # if index == 0:
                #     continue

                document_id = "EF" + str(int(content['threadId'], base=10)) + "r" + str(index)

                text = reply['postText']
                annotated_text = text
                annotations_clear = ""
                if 'annotatedText' in reply:
                    annotated_text = reply['annotatedText']
                    pattern = re.compile('\[\[C[0-9]+\|[a-zA-Z]+\]\]')

                    annotations = re.findall(pattern, annotated_text)
                    annotation_clear = ""
                    for annotation in annotations:
                        annotations_clear += annotation[2:10] + " "

                    # print(annotation_clear)

                json.dump({"id": document_id, "contents": text, "annotated-text": annotated_text,
                           "annotations": annotations_clear}, data_file)
                data_file.write('\n')

                maps_file_2.write("\t" + document_id)

                if (reply['postThankYouCount'] > 0 or reply['postHelpfulCount'] > 0 or reply['postSupportCount'] > 0 or
                        reply['mdReply']):
                    maps_file_3.write("\t" + document_id)

                documents_written += 1

                if documents_written % 1000 == 0:
                    data_file.close()
                    data_file = open(
                        os.path.join(output_directory_data, "data" + str(documents_written // 1000) + ".json"),
                        "w+", encoding="utf8")

            maps_file_2.write('\n')
            maps_file_3.write('\n')

            processed_files += 1

            if processed_files % 1000 == 0:
                query_file.close()
                query_file = open(
                    os.path.join(output_directory_queries, "query" + str(processed_files // 1000) + ".txt"),
                    "w+", encoding="utf8")

            if processed_files % 100 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1

data_file.close()
query_file.close()
maps_file_2.close()
maps_file_3 .close()
