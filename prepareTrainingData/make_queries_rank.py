"""
 * Created by filip on 21/10/2019

 Makes queries and scores the document relevance in respect to those queries.

 First, random folders and files are selected. The first post in each file is extracted as a query with text, category,
 thread ID and some other data. Up to 'max_queries' are created. These are saved into a json file to future use.

 Then directory of annotated JSON files is walked through. For each post in each file, the relevance is calculated in
 respect to all queries constructed earlier. These rankings are saved to a separate file for each query in format
 "documentID    (\t)    score".
"""

import os
import json
import traceback
import random
import platform
from prepareTrainingData.EntityInfo.entities_info import EntityInfo, get_entity_code

on_server = platform.system() == "Linux"

if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/trac/relevance/"
    informative_nodes_list_location = "/home/fadamik/Documents/informative_nodes.txt"
    other_nodes_list_location = "/home/fadamik/Documents/other_nodes.txt"

else:
    starting_directory = "D:/Downloads/json/ehealthforum/json-annotated/"
    output_directory = "D:/downloads/json/ehealthforum/trac/relevance/"
    informative_nodes_list_location = "D:/downloads/json/informative-entities.txt"
    other_nodes_list_location = "D:/downloads/json/other-entities.txt"

random.seed("12346")
max_queries = 5


# Extract data for a query from a given JSON file
def extract_query(json_contents: dict, ef: EntityInfo):
    if json_contents['replyCount'] < 2:
        return None

    query = {'category': json_contents['commonCategory']}

    annotations = []
    if 'annotationsFull' in json_contents['replies'][0]:
        for annotation in json_contents['replies'][0]['annotationsFull']:
            entity = get_entity_code(annotation)

            if ef.is_informative_entity(entity):
                annotations.append(entity)

        query['annotations'] = annotations
    else:
        query['annotations'] = None

    post_text = json_contents['replies'][0]['postText']
    length = len(post_text)
    query['length'] = length
    query['text'] = post_text.replace('\t', '')
    query['username'] = json_contents['replies'][0]['createdBy']['username']

    query['threadId'] = json_contents['threadId']
    if 'annotatedOriginCategory' in json_contents:
        query['annotatedOriginCategory'] = json_contents['annotatedOriginCategory']


    return query

# Randomly loop through files and select up to 'max_queries' as queries.
def make_queries(start_dir: str, ef: EntityInfo) -> list:
    subdirs = os.listdir(start_dir)
    random.shuffle(subdirs)

    queries = []

    for directory in subdirs:
        for root, dirs, files in os.walk(os.path.join(starting_directory, directory)):
            random.shuffle(files)
            for filename in files:
                try:
                    with open(os.path.join(root, filename), "r", encoding="utf8") as file:
                        contents = json.load(file)

                except Exception as e:
                    traceback.print_exc()
                    continue

                new_query = extract_query(contents, ef)

                if new_query is not None:
                    queries.append(new_query)

                    break

            if len(queries) > max_queries:
                break

        if len(queries) > max_queries:
            break

    return queries


# Calculate the score for a given document based on provided document features.
def scoring_function(doctor_reply: bool, no_votes: int, no_entities: int, no_same_entities: int, length: int,
                     same_category: bool, same_thread: bool) -> int:
    MD_REPLY_WEIGHT = 35
    VOTE_WEIGHT = 5
    ENTITY_WEIGHT = 10
    SAME_ENTITY_WEIGHT = 15
    LENGTH_WEIGHT = 15
    SAME_CATEGORY_WEIGHT = 200
    SAME_THREAD_WEIGHT = 15

    if doctor_reply:
        is_md_reply = 1
    else:
        is_md_reply = 0

    if same_category:
        is_same_category = 1
    else:
        is_same_category = 0

    if same_thread:
        is_same_thread = 1
    else:
        is_same_thread = 0

    if length > 150:
        is_long_reply = 1
    else:
        is_long_reply = 0

    if no_votes > 5:
        no_votes = 5

    if no_entities > 3:
        no_entities = 3

    return (MD_REPLY_WEIGHT * is_md_reply +
            VOTE_WEIGHT * no_votes +
            ENTITY_WEIGHT * no_entities +
            SAME_ENTITY_WEIGHT * no_same_entities +
            LENGTH_WEIGHT * is_long_reply +
            SAME_CATEGORY_WEIGHT * is_same_category +
            SAME_THREAD_WEIGHT * is_same_thread)


# Loop through documents in a JSON file and calculate the relevance score with respect to each query for each document.
def calculate_relevance_scores(query: dict, json_contents: dict, ef: EntityInfo):
    scored_documents = {}

    for index, reply in enumerate(json_contents['replies']):
        if index == 0:
            continue

        try:
            is_same_category = query['category'] == json_contents['commonCategory']
            is_same_thread = query['threadId'] == json_contents['threadId']
            number_votes = reply['postThankYouCount'] + reply['postHelpfulCount'] + reply['postSupportCount']
            text_length = len(reply['postText'])
            is_doctor_reply = reply['mdReply']

            number_medical_entities = 0
            number_same_entities = 0

            if 'annotationsFull' in reply:
                annotations = set(get_entity_code(entity) for entity in reply['annotationsFull'])

                for entity in annotations:
                    if entity in ef.informative_entities:
                        number_medical_entities += 1
                        if entity in query['annotations']:
                            number_same_entities += 1
                    elif entity not in ef.other_entities and ef.is_informative_entity(entity):
                        number_medical_entities += 1
                        ef.update_informative_list(entity)

                        if entity in query['annotations']:
                            number_same_entities += 1

                    elif entity not in ef.other_entities:
                        ef.update_other_list(entity)

            document_score = scoring_function(is_doctor_reply, number_votes, number_medical_entities,
                                              number_same_entities, text_length, is_same_category, is_same_thread)

            document_name = "EF" + str(json_contents['threadId']) + "r" + str(index)

            scored_documents[document_name] = document_score

        except KeyError as ke:
            if 'threadId' in json_contents:
                print("KeyError in file: " + json_contents['threadId'])
            else:
                print("KeyError in unknown file.")

            return None

    return scored_documents


# Write out the relevance score to file.
def write_scores_to_file(scores: dict, output_dir: str) -> None:
    for query_name, query_values in scores.items():
        with open(os.path.join(output_dir, query_name + ".txt"), "w+", encoding="utf8") as output_file:
            for document_id, score in query_values.items():
                output_file.write(document_id + "\t" + str(score) + "\n")


# Loop through the JSON files, open and parse each file to prepare them for scoring.
def loop_all_documents(queries: list, start_dir: str, ef: EntityInfo):
    document_scores = {query['threadId']: {} for query in queries}

    processed_files = 0
    for root, dirs, files in os.walk(start_dir):
        for filename in files:
            try:
                with open(os.path.join(root, filename), "r", encoding="utf8") as file:
                    contents = json.load(file)

            except json.decoder.JSONDecodeError as jde:
                traceback.print_exc()
                continue

            except Exception as e:
                traceback.print_exc()
                continue

            if contents['replyCount'] < 2:
                continue
            else:
                for query in queries:
                    query_name = query['threadId']

                    relevance_scores = calculate_relevance_scores(query, contents, ef)
                    if relevance_scores is not None:
                        for document_id in relevance_scores:
                            document_scores[query_name][document_id] = relevance_scores[document_id]

            processed_files += 1

            if processed_files % 10000 == 0:
                print("Processed files: " + str(processed_files))
                write_scores_to_file(document_scores, output_directory)

    write_scores_to_file(document_scores, output_directory)


def main():
    entity_info = EntityInfo()

    queries = make_queries(starting_directory, entity_info)
    with open(os.path.join(output_directory, "queries.json"), "w+", encoding="utf8") as output_file:
        json_queries = []
        for query in queries:
            json_query = query
            json_query['annotations'] = list(query['annotations'])

            json_queries.append(json_query)

        json.dump(json_queries, output_file)

    print("Wrote queries to file.")

    loop_all_documents(queries, starting_directory, entity_info)

# main()
