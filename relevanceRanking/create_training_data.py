'''
 * Created by filip on 23/10/2019
'''

import os
import json

import relevanceRanking.make_queries_rank
from relevanceRanking.connect_to_kb import connect_elasticsearch

on_server = False

if on_server:
    starting_directory = "build-attempt/anserini"
    starting_file = "run.ef-all.bm25.reduced.10.txt"
    data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
else:
    starting_directory = "d:/downloads/json/ehealthforum/trac"
    starting_file = "run.ef-all.bm25.reduced.txt"
    data_directory = "d:/downloads/json/ehealthforum/json-annotated/"


# Read file with BM25 scores and load it as dictionary.
def read_score_file(filename: str) -> dict:
    scores = {}

    with open(os.path.join(starting_directory, filename), "r", encoding="utf8") as file:
        previous_line_query = ""
        counter = 0

        for line in file:
            counter += 1

            line_contents = line.split(" ")
            query_id = line_contents[0]
            document_id = line_contents[2]
            document_score = line_contents[4]

            if not query_id == previous_line_query:
                counter = 0

            if counter > 50:
                continue
            else:
                previous_line_query = query_id

                if query_id not in scores:
                    scores[query_id] = {document_id: document_score}
                else:
                    scores[query_id][document_id] = document_score

            if len(scores) > 10:
                break

    return scores


# Load queries from JSON files based on their IDs and load them into a dictionary.
def make_queries(query_ids: list) -> dict:
    es = connect_elasticsearch()

    queries = {}

    for query_id in query_ids:
        folder = str(int(query_id, 10) // 1000)
        filename = query_id + ".json"

        try:
            with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                contents = json.load(file)
        except FileNotFoundError as fe:
            print("File not found:" + os.path.join(data_directory, folder, filename))
            continue

        query = relevanceRanking.make_queries_rank.extract_query(contents, es)
        if query:
            queries[query_id] = query

    return queries


# Extract document features from JSON files based on their IDs.
def find_documents(document_ids: set) -> dict:
    documents = {}
    for doc_id in document_ids:
        thread_id, reply_nr = doc_id.replace("EF", "").split("r")

        reply_nr = int(reply_nr, base=10)

        folder = str(int(thread_id, 10) // 1000)
        filename = thread_id + ".json"

        try:
            with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                contents = json.load(file)

                documents[doc_id] = {}

                documents[doc_id]['threadId'] = thread_id
                documents[doc_id]['category'] = contents['commonCategory']
                documents[doc_id]['mdReply'] = contents['replies'][reply_nr]['mdReply']
                documents[doc_id]['postLength'] = len(contents['replies'][reply_nr]['postText'])
                documents[doc_id]['votes-h'] = contents['replies'][reply_nr]['postHelpfulCount']
                documents[doc_id]['votes-s'] = contents['replies'][reply_nr]['postSupportCount']
                documents[doc_id]['votes-t'] = contents['replies'][reply_nr]['postThankYouCount']

                if 'annotationsFull' in contents['replies'][reply_nr]:
                    documents[doc_id]['annotations'] = []
                    for annotation in contents['replies'][reply_nr]['annotationsFull']:
                        (documents[doc_id]['annotations']
                         .append(relevanceRanking.make_queries_rank.get_entity_code(annotation)))
                else:
                    documents[doc_id]['annotations'] = []

        except FileNotFoundError as fe:
            print("File not found:" + os.path.join(data_directory, folder, filename))
            continue

    return documents


def produce_training_data(scores: dict, queries: dict, documents: dict) -> (list, list):
    training_data = []
    target_values = []

    es = connect_elasticsearch()

    for query_id in scores:
        for document_id in scores[query_id]:

            if document_id in documents and query_id in queries:
                document = documents[document_id]
                query = queries[query_id]
            else:
                continue

            is_same_category = int(query['category'] == document['category'])
            is_same_thread = int(query['threadId'] == document['threadId'])
            number_votes_t = document['votes-t']
            number_votes_s = document['votes-s']
            number_votes_h = document['votes-h']
            is_doctor_reply = int(document['mdReply'])

            text_length_factor = document['postLength'] // 150

            number_medical_entities = 0
            number_same_entities = 0

            annotations = set(document['annotations'])

            for entity in annotations:
                try:
                    if entity in relevanceRanking.make_queries_rank.informative_entities:
                        number_medical_entities += 1
                        if entity in query['annotations']:
                            number_same_entities += 1
                    elif (entity not in relevanceRanking.make_queries_rank.other_entities and
                          relevanceRanking.connect_to_kb.is_informative(entity, es)):

                        number_medical_entities += 1
                        relevanceRanking.make_queries_rank.update_informative_list(entity)

                        if entity in query['annotations']:
                            number_same_entities += 1

                    elif entity not in relevanceRanking.make_queries_rank.other_entities:
                        relevanceRanking.make_queries_rank.update_other_list(entity)

                except ValueError as ve:
                    print("The entity " + entity + " could not be evaluated. Skipping...")
                    continue

            training_item = [is_doctor_reply, number_votes_h, number_votes_s, number_votes_t, number_medical_entities,
                             number_same_entities, text_length_factor, is_same_category, is_same_thread]
            target_item = [scores[query_id][document_id]]

            training_data.append(training_item)
            target_values.append(target_item)

    return training_data, target_values


def main():
    bm25_scores = read_score_file(starting_file)

    relevanceRanking.make_queries_rank.load_entity_types()

    full_queries = make_queries(list(bm25_scores.keys()))

    document_ids = set()

    for query in bm25_scores:
        for doc_id in bm25_scores[query].keys():
            document_ids.add(doc_id)

    full_documents = find_documents(document_ids)

    print(produce_training_data(bm25_scores, full_queries, full_documents))


main()
