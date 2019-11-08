'''
 * Created by filip on 23/10/2019
'''

import os
import json
import platform
from relevanceRanking.entities_info import EntityInfo
from relevanceRanking.make_queries_rank import make_queries, extract_query, get_entity_code

on_server = platform.system() == "Linux"

if on_server:
    starting_directory = "/home/fadamik/build-attempt/anserini"
    starting_file = "run.ef-all.bm25.reduced.10.txt"
    data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory = "/home/fadamik/Documents/"

else:
    starting_directory = "d:/downloads/json/ehealthforum/trac"
    starting_file = "run.ef-all.bm25.reduced.txt"
    data_directory = "d:/downloads/json/ehealthforum/json-annotated/"
    output_directory = "d:/downloads/json/ehealthforum/trac"


# Read file with BM25 scores and load it as dictionary.
def read_score_file(filename: str) -> dict:
    NUMBER_QUERIES = 10
    NUMBER_DOCS_PER_QUERY = 20

    scores = {}

    with open(os.path.join(starting_directory, filename), "r", encoding="utf8") as file:
        for line in file:

            line_contents = line.split(" ")
            query_id = line_contents[0]
            document_id = line_contents[2]
            doc_rank = int(line_contents[3], base=10)
            document_score = line_contents[4]

            if NUMBER_DOCS_PER_QUERY > doc_rank:
                relevant = True
            elif NUMBER_DOCS_PER_QUERY <= doc_rank <= 100-NUMBER_DOCS_PER_QUERY:
                continue
            elif doc_rank > 100-NUMBER_DOCS_PER_QUERY:
                relevant = False

            if query_id not in scores:
                scores[query_id] = {document_id: {'relevant': relevant, 'score': document_score}}
            else:
                scores[query_id][document_id] = {'relevant': relevant, 'score': document_score}

            if len(scores) > NUMBER_QUERIES:
                break

    return scores


# Load queries from JSON files based on their IDs and load them into a dictionary.
def make_queries(query_ids: list, ef: EntityInfo) -> dict:
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

        query = extract_query(contents, ef)
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
                documents[doc_id]['userStatus'] = contents['replies'][reply_nr]['createdBy']['status']
                documents[doc_id]['votes-h'] = contents['replies'][reply_nr]['postHelpfulCount']
                documents[doc_id]['votes-s'] = contents['replies'][reply_nr]['postSupportCount']
                documents[doc_id]['votes-t'] = contents['replies'][reply_nr]['postThankYouCount']
                documents[doc_id]['document-text'] = contents['replies'][reply_nr]['postText']

                if 'annotationsFull' in contents['replies'][reply_nr]:
                    documents[doc_id]['annotations'] = []
                    for annotation in contents['replies'][reply_nr]['annotationsFull']:
                        (documents[doc_id]['annotations']
                         .append(get_entity_code(annotation)))
                else:
                    documents[doc_id]['annotations'] = []

        except FileNotFoundError as fe:
            print("File not found:" + os.path.join(data_directory, folder, filename))
            continue

    return documents


# Create training data by reading the full query, extracting document features in respect to the query and reading
def produce_training_data(scores: dict, queries: dict, documents: dict, ef: EntityInfo) -> (list, list):
    training_data = []

    for query_id in scores:
        for document_id in scores[query_id]:

            if document_id in documents and query_id in queries:
                document = documents[document_id]
                query = queries[query_id]
            else:
                continue

            query_category = query['category']
            query_text = query['text']
            query_thread = query['threadId']

            query_annotations = ';'
            for annotation in query['annotations']:
                query_annotations += annotation + ';'

            document_user_status = document['userStatus']
            document_number_votes_t = document['votes-t']
            document_number_votes_s = document['votes-s']
            document_number_votes_h = document['votes-h']
            document_text = document['document-text']
            document_is_doctor_reply = document['mdReply']
            document_annotations = set(document['annotations'])

            # training_item = [query[]is_doctor_reply, number_votes_h, number_votes_s, number_votes_t]

            # training_data.append(training_item)

    return training_data


def write_out_training_data(output_path: str, data: list, targets: list) -> None:
    filename = "training_data_snorkel.txt"
    with open(os.path.join(output_path, filename), "w+", encoding="utf8") as training_file:
        for index, document in enumerate(data):
            # for
            pass
        json.dump(data, training_file)

    print("Wrote training data to file: " + os.path.join(output_path, filename))

    # with open(os.path.join(output_path, "targets.json"), "w+", encoding="utf8") as targets_file:
    #     json.dump(targets, targets_file)
    # print("Wrote target values to file: " + os.path.join(output_path, "targets.json"))


def main():
    ef = EntityInfo()

    bm25_scores = read_score_file(starting_file)

    full_queries = make_queries(list(bm25_scores.keys()), ef)

    document_ids = set()
    for query in bm25_scores:
        for doc_id in bm25_scores[query].keys():
            document_ids.add(doc_id)

    full_documents = find_documents(document_ids)
    training_data = produce_training_data(bm25_scores, full_queries, full_documents, ef)
    # write_out_training_data(output_directory, training_data, target_values)


main()
