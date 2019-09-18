'''
 * Created by filip on 17/09/2019
'''

import json, os
import pandas as pd
import numpy as np
import traceback

# starting_directory = "D:/Downloads/json/healthboards/html-sorted/"
starting_directory = "D:/Downloads/json/healthboards/json-sorted3/"
# starting_directory = "/scratch/GW/pool0/fadamik/healthboards/json-sorted2/"
# output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted2/"
output_directory = "D:/Downloads/json/pandas/healthboards/"

SOURCE_SAME_THREAD = 0
SOURCE_VOTES = 1
SOURCE_MD_REPLY = 2


def reduce_json(json_input):
    query_doc_pairs = []
    query = None

    if json_input["replyCount"] == 1:
        return None

    for reply in json_input["replies"]:
        if reply["postOrder"] == 0:
            query = {
                "text": reply["postText"],
                "username": reply["createdBy"]["username"],
                "status": reply["createdBy"]["status"],
                "category": json_input["commonCategory"]
            }
            break

    for reply in json_input["replies"]:
        if reply["postOrder"] == 0 or len(reply["postText"]) == 0:
            continue
        else:
            query_doc = query.copy()

            query_doc["doc-text"] = reply["postText"]
            query_doc["doc-quotes"] = reply["hasQuotes"]
            query_doc["doc-username"] = reply["createdBy"]["username"]
            query_doc["doc-status"] = reply["createdBy"]["status"]
            query_doc["doc-category"] = json_input["commonCategory"]
            query_doc["doc-thankYous"] = reply["postThankYouCount"]
            query_doc["doc-support"] = reply["postSupportCount"]
            query_doc["doc-helpful"] = reply["postHelpfulCount"]

        if reply["mdReply"]:
            query_doc['source'] = SOURCE_MD_REPLY
        elif reply["postThankYouCount"] > 0 or reply["postSupportCount"] > 0 or reply["postHelpfulCount"] > 0:
            query_doc['source'] = SOURCE_VOTES
        else:
            query_doc['source'] = SOURCE_SAME_THREAD

        query_doc['relevance'] = True

        query_doc_pairs.append(query_doc)

    return query_doc_pairs


def add_to_data_frame(existing_dataframe, data):
    for pair in data:
        existing_dataframe = existing_dataframe.append(pd.DataFrame([pair]), sort=False)

    return existing_dataframe


file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

df = pd.DataFrame(
        columns=['text', 'username', 'status', 'category', 'doc-text', 'doc-quotes', 'doc-username', 'doc-status', 'doc-category',
                 'doc-thankYous', 'doc-support', 'doc-helpful'])

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:

            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)

            output = reduce_json(file_as_json)
            if output:
                df = add_to_data_frame(df, output)

            successful_files += 1
            file_count += 1
            if file_count % 100 == 0:
                print("Processed files: " + str(file_count))
                print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
                    error_files) + ENDC)

            if file_count % 1000 == 0:
                # file = open(os.path.join(output_directory, "dataFrameOut.txt"), "w+", encoding="utf8")
                df.to_csv(os.path.join(output_directory, "dataFrameOut.txt"), sep='\t')
                print("Written out to file.")
                break

        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1

df.to_csv(os.path.join(output_directory, "dataFrameOut.txt"), sep='\t')
print(df)
