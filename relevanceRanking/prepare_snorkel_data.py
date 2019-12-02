'''
 * Created by filip on 23/10/2019
'''

import os
import json
import platform
import random
from relevanceRanking.entities_info import EntityInfo
from relevanceRanking.make_queries_rank import make_queries, extract_query, get_entity_code
from relevanceRanking.connect_to_kb import informative_entity_types

all_types = "typ_dsyn" + "\t" + "typ_patf" + "\t" + "typ_sosy" + "\t" + "typ_dora" + "\t" + "typ_fndg" + "\t" + "typ_menp" + "\t" + "typ_chem" + "\t" + "typ_orch" + "\t" + "typ_horm" + "\t" + "typ_phsu" + "\t" + "typ_medd" + "\t" + "typ_bhvr" + "\t" + "typ_diap" + "\t" + "typ_bacs" + "\t" + "typ_enzy" + "\t" + "typ_inpo" + "\t" + "typ_elii"
all_types_d = "d_typ_dsyn" + "\t" + "d_typ_patf" + "\t" + "d_typ_sosy" + "\t" + "d_typ_dora" + "\t" + "d_typ_fndg" + "\t" + "d_typ_menp" + "\t" + "d_typ_chem" + "\t" + "d_typ_orch" + "\t" + "d_typ_horm" + "\t" + "d_typ_phsu" + "\t" + "d_typ_medd" + "\t" + "d_typ_bhvr" + "\t" + "d_typ_diap" + "\t" + "d_typ_bacs" + "\t" + "d_typ_enzy" + "\t" + "d_typ_inpo" + "\t" + "d_typ_elii"
on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/home/fadamik/build-attempt/anserini/runs.ehf.titles.1000"
    starting_file = "run.ehf.titles.1000.0.txt"
    data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory = "/home/fadamik/Documents/"
    output_filename = "training_data_snorkel_ehf_100k_titles.txt"
    query_numbers_location = '/home/fadamik/Documents/query_numbers_ehf.json'

else:
    starting_directory = "m:/build-attempt/anserini/runs.ehf.titles.1000"
    starting_file = "run.ef-all.bm25.reduced.txt"
    data_directory = "n:/ehealthforum/json-annotated/"
    output_directory = "d:/downloads/json/ehealthforum/trac"
    output_filename = "training_data_snorkel_test_rel.txt"
    query_numbers_location = 'd:/downloads/json/ehealthforum/trac/query_numbers.json'

NUMBER_OF_RESULT_FILES = 79
NUMBER_QUERIES = 200  # * number of result files
NUMBER_DOCS_PER_QUERY = 10
NUMBER_HITS_IN_FILE = 1000


# Read file with BM25 scores and load it as dictionary.
def read_score_file(query_ids: list, filename: str) -> dict:
    scores = {}

    with open(os.path.join(starting_directory, filename), "r", encoding="utf8") as file:
        for line in file:

            line_contents = line.split(" ")
            query_id = line_contents[0]
            if query_id not in query_ids:
                continue

            document_id = line_contents[2]
            doc_rank = int(line_contents[3], base=10)
            document_score = line_contents[4]

            if NUMBER_DOCS_PER_QUERY >= doc_rank:
                relevant = True
            elif NUMBER_DOCS_PER_QUERY <= doc_rank <= NUMBER_HITS_IN_FILE - NUMBER_DOCS_PER_QUERY:
                continue
            elif doc_rank > NUMBER_HITS_IN_FILE - NUMBER_DOCS_PER_QUERY:
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
        thread_id, reply_nr = doc_id.replace("EF-", "").split("r")

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
                documents[doc_id]['username'] = contents['replies'][reply_nr]['createdBy']['username']

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

    entity_list = ef.get_entity_relations()

    for query_id in scores:
        if query_id in queries:
            query = queries[query_id]
        else:
            continue

        training_data_pool = []

        if 'annotatedOriginCategory' in query:
            entity_code = get_entity_code(query['annotatedOriginCategory'])
            if entity_code is not None:
                query['annotations'].append(entity_code)

        for document_id in scores[query_id]:
            if document_id in documents:
                document = documents[document_id]
            else:
                break

            query_category = query['category']
            query_thread = query['threadId']
            query_text = query['text'].replace('\t', '')
            query_username = query['username']
            query_annotation_count = ""
            for index, count in enumerate(make_annotation_counts(query['annotations'], ef)):
                if index > 0:
                    query_annotation_count = query_annotation_count + '\t'

                query_annotation_count = query_annotation_count + str(count)

            document_annotations = ''
            for index, annotation in enumerate(document['annotations']):
                if index > 0:
                    document_annotations += ";"
                document_annotations += annotation

            if len(query['annotations']) > 0:
                query_annotations = ''
                relationships = ''
                for index, annotation in enumerate(query['annotations']):
                    if index > 0:
                        query_annotations += ";"
                    query_annotations += annotation

                    if annotation in entity_list:
                        for document_annotation in document['annotations']:
                            if document_annotation in entity_list[annotation]:
                                if not relationships == '':
                                    relationships += ','
                                relationships += entity_list[annotation][document_annotation]

            else:
                query_annotations = None
                relationships = None

            document_category = document['category']
            document_thread = document['threadId']

            document_user_status = document['userStatus']
            document_username = document['username']
            document_number_votes_t = document['votes-t']
            document_number_votes_s = document['votes-s']
            document_number_votes_h = document['votes-h']
            document_text = document['document-text'].replace('\t', '').replace('\n', '')
            document_is_doctor_reply = document['mdReply']

            document_annotation_count = ""
            for index, count in enumerate(make_annotation_counts(document['annotations'], ef)):
                if index > 0:
                    document_annotation_count = document_annotation_count + '\t'

                document_annotation_count = document_annotation_count + str(count)

            training_item = [query_category, query_thread, query_text, query_username, query_annotations,
                             query_annotation_count,
                             document_category, document_thread, document_text, document_is_doctor_reply,
                             document_number_votes_h, document_number_votes_s, document_number_votes_t,
                             document_username, document_user_status, document_annotations, document_annotation_count,
                             relationships,
                             scores[query_id][document_id]['relevant'], scores[query_id][document_id]['score']]

            training_data_pool.append(training_item)

        if len(training_data_pool) == 20:
            for item in training_data_pool:
                training_data.append(item)

    return training_data


def make_annotation_counts(annotations: list, entity_info: EntityInfo) -> list:
    types_counts = {}

    for entity in informative_entity_types:
        types_counts[entity] = 0

    for annotation in annotations:
        types = entity_info.get_entity_types(annotation)

        for entity_type in types:
            types_counts[entity_type] += 1

    output_counts = []
    for entity in informative_entity_types:
        output_counts.append(types_counts[entity])

    return output_counts


def write_out_training_data(output_path: str, data: list) -> None:
    with open(os.path.join(output_path, output_filename), "w+", encoding="utf8") as training_file:

        training_file.write(
            "query_category" + "\t" + "query_thread" + "\t" + "query_text" + "\t" + "query_username" + "\t" + "query_annotations" + "\t" + all_types + "\t" +
            "document_category" + "\t" + "document_thread" + "\t" + "document_text" + "\t" + "document_is_doctor_reply" + "\t" +
            "document_number_votes_h" + "\t" + "document_number_votes_s" + "\t" + "document_number_votes_t" + "\t" +
            "document_username" + "\t" + "document_user_status" + "\t" + "document_annotations" + "\t" + all_types_d + "\t" + "relationships_list" + "\t" +
            "bm25_relevant" + "\t" + "bm25_score" + "\n")

        for row in data:
            for index, feature in enumerate(row):
                if index > 0:
                    training_file.write('\t')
                training_file.write(str(feature))

            training_file.write('\n')

    print("Wrote training data to file: " + os.path.join(output_path, output_filename))


def main():
    ef = EntityInfo()

    random.seed(1468)

    with open(query_numbers_location, 'r', encoding='utf8') as file:
        query_numbers = json.load(file)

    bm25_scores = {}

    for i in range(NUMBER_OF_RESULT_FILES):
        print("I AM READY FOR SOME THREADS")

        print("Now reading queries from file number: " + str(i))
        selected_queries = random.sample(query_numbers[i], NUMBER_QUERIES)
        bm25_scores.update(read_score_file(selected_queries,
                                           os.path.join(starting_directory, "run.ehf.titles.1000." + str(i) + ".txt")))

    full_queries = make_queries(list(bm25_scores.keys()), ef)

    document_ids = set()
    for query in bm25_scores:
        for doc_id in bm25_scores[query].keys():
            document_ids.add(doc_id)

    full_documents = find_documents(document_ids)
    training_data = produce_training_data(bm25_scores, full_queries, full_documents, ef)
    write_out_training_data(output_directory, training_data)


main()
