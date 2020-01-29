"""
 * Created by filip on 23/10/2019
This script prepares non-relevant pairs of data, based on similar categories. The produced pairs serve as input to
Snorkel (to filter out possibly relevant pairs).

Input:
    * List of query IDs sorted by categories (JSON) - category_file
    * Map of similar categories, based on TF-IDF (TXT) - similar_categories_map - must be properly selected between
    HealthBoards and eHealthForum.
    * Map of forum specific categories to unified list of categories (JSON) - old_new_categories_map - must be properly
    selected between HealthBoards and eHealthForum.
    * List of queries used to create relevant pairs (we need a non-relevant example for every relevant example)
    (JSON) - used_queries_count_path
    * Annotated JSON data files - data_directory

Output:
    * Non-relevant pairs (one row is one query-document pair with all features), tab-separated

"""

import os
import json
import platform
import random
import copy
from prepareTrainingData.EntityInfo.entities_info import EntityInfo
from prepareTrainingData.make_queries_rank import extract_query, get_entity_code
from prepareTrainingData.EntityInfo.connect_to_kb import informative_entity_types

all_types = "typ_dsyn" + "\t" + "typ_patf" + "\t" + "typ_sosy" + "\t" + "typ_dora" + "\t" + "typ_fndg" + "\t" + "typ_menp" + "\t" + "typ_chem" + "\t" + "typ_orch" + "\t" + "typ_horm" + "\t" + "typ_phsu" + "\t" + "typ_medd" + "\t" + "typ_bhvr" + "\t" + "typ_diap" + "\t" + "typ_bacs" + "\t" + "typ_enzy" + "\t" + "typ_inpo" + "\t" + "typ_elii"
all_types_d = "d_typ_dsyn" + "\t" + "d_typ_patf" + "\t" + "d_typ_sosy" + "\t" + "d_typ_dora" + "\t" + "d_typ_fndg" + "\t" + "d_typ_menp" + "\t" + "d_typ_chem" + "\t" + "d_typ_orch" + "\t" + "d_typ_horm" + "\t" + "d_typ_phsu" + "\t" + "d_typ_medd" + "\t" + "d_typ_bhvr" + "\t" + "d_typ_diap" + "\t" + "d_typ_bacs" + "\t" + "d_typ_enzy" + "\t" + "d_typ_inpo" + "\t" + "d_typ_elii"
on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    # INPUT
    category_file = '/home/fadamik/Documents/category_maps_ehf_2.json'
    similar_categories_map = '/home/fadamik/Documents/similar-categories-ehf.txt'
    old_new_categories_map = '/home/fadamik/Documents/ehealthforum_map.json'
    used_queries_count_path = '/home/fadamik/Documents/used_queries_relevant.json'
    data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"

    # OUTPUT
    output_filename = "/home/fadamik/Documents/non-relevant_pairs_200k_ehf.txt"

else:
    # INPUT
    category_file = 'm:/Documents/category_maps_ehf.json'
    similar_categories_map = 'm:/Documents/similar-categories-ehf.txt'
    old_new_categories_map = 'm:/Documents/ehealthforum_map.json'
    used_queries_count_path = 'd:/downloads/json/ehealthforum/trac/used_queries_relevant_test.json'
    data_directory = "n:/ehealthforum/json-annotated/"

    # OUTPUT
    output_filename = "m:/Documents/non-relevant_pairs_200k_ehf.txt"


def read_json_file(filename: str) -> dict:
    """
    Open and parse a JSON file and return its contents.

    @param filename: Path to file to open.
    @return: Contents of JSON file as a dictionary.
    """
    with open(filename, "r", encoding="utf8") as file:
        contents = json.load(file)

    return contents


def read_similar_file(filename: str) -> dict:
    """
    Open and read the file with similar categories (tab-separated).

    @param filename: Path to the file to read
    @return: Similar categories as dictionary
    """
    similar_categories = {}

    with open(filename, 'r', encoding='utf8') as file:
        header = True
        for line in file:
            if header:
                header = False
                continue

            category, sim1, sim2, sim3 = line.split('\t')
            sim3 = sim3.replace('\n', '')

            similar_categories[category] = {'1': sim1, '2': sim2, '3': sim3}

    return similar_categories


def make_queries(query_ids: list, ef: EntityInfo) -> dict:
    """
    Extract query data from JSON files based on the query IDs and return the query data as a dictionary.

    @param query_ids: Query IDs of interest (skip the rest)
    @param ef: EntityInfo class, used to extract information about informative entities.
    @return: Key: query ID, value: query data
    """
    queries = {}

    for query_id in query_ids:
        filename = str(query_id) + ".json"

        try:
            folder = str(int(query_id, 10) // 1000)

            with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                contents = json.load(file)

        except FileNotFoundError as fe:
            folder = str(int(query_id, 10) // 10000)

            try:
                with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                    contents = json.load(file)

            except FileNotFoundError as fe:
                print("File not found:" + os.path.join(data_directory, folder, filename))
                folder = str(int(query_id, 10) // 100)

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


def find_documents(document_ids: set) -> dict:
    """
    Extract document features from JSON files based on their IDs. Return the dictionary with relevant document data.

    @param document_ids: IDs of documents of interest (skip the rest)
    @return: Dictionary, key: document ID, value: dictionary of relevant document data.
    """
    documents = {}
    for doc_id in document_ids:
        thread_id, reply_nr = doc_id.replace("EF-", "").split("r")

        reply_nr = int(reply_nr, base=10)

        filename = thread_id + ".json"

        try:
            folder = str(int(thread_id, 10) // 1000)

            with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                contents = json.load(file)

        except FileNotFoundError as fe:
            folder = str(int(thread_id, 10) // 10000)

            try:
                with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                    contents = json.load(file)

            except FileNotFoundError as fe:
                print("File not found:" + os.path.join(data_directory, folder, filename))
                folder = str(int(thread_id, 10) // 100)

                try:
                    with open(os.path.join(data_directory, folder, filename), "r", encoding="utf8") as file:
                        contents = json.load(file)

                except FileNotFoundError as fe:
                    print("File not found:" + os.path.join(data_directory, folder, filename))
                    continue

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

    return documents


def produce_training_data(selected: list, queries: dict, documents: dict, ef: EntityInfo) -> list:
    """
    Create training data by reading the full query, extracting document features in respect to the query and reading

    @param selected: List of selected queries
    @param queries: Full details of the selected queries
    @param documents: Relevant details of the selected documents.
    @param ef: EntityInfo class, used to extract information about informative entities.
    @return: List of individual training pairs with all details necessary for Snorkel processing.
    """
    training_data = []

    entity_list = ef.get_entity_relations()

    for query_id in selected:
        if query_id in queries:
            query = queries[query_id]
        else:
            continue

        if 'annotatedOriginCategory' in query:
            category_annotation = get_entity_code(query['annotatedOriginCategory'])
            if category_annotation is not None and query['annotations'] is not None:
                query['annotations'].append(category_annotation)
            elif category_annotation is not None and query['annotations'] is None:
                query['annotations'] = [category_annotation]

        for document_id in selected[query_id]:
            if document_id in documents:
                document = documents[document_id]
            else:
                break

            query_category = query['category']
            query_thread = query['threadId']
            query_text = query['text'].replace('\t', '')
            query_username = query['username']
            query_annotation_count = ""
            for index, count in enumerate(make_annotation_types(query['annotations'], ef)):
                if index > 0:
                    query_annotation_count = query_annotation_count + '\t'

                query_annotation_count = query_annotation_count + str(count)

            document_annotations = ''
            for index, annotation in enumerate(document['annotations']):
                if index > 0:
                    document_annotations += ";"
                document_annotations += annotation

            if query['annotations'] is not None:
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
            for index, count in enumerate(make_annotation_types(document['annotations'], ef)):
                if index > 0:
                    document_annotation_count = document_annotation_count + '\t'

                document_annotation_count = document_annotation_count + str(count)

            # Two 0s at the end represent a BM25 score (non-relevant queries don't have it) and BM25 relevance (0 for
            # non-relevant)
            training_item = [query_category, query_thread, query_id, query_text, query_username, query_annotations,
                             query_annotation_count,
                             document_category, document_id, document_thread, document_text, document_is_doctor_reply,
                             document_number_votes_h, document_number_votes_s, document_number_votes_t,
                             document_username, document_user_status, document_annotations, document_annotation_count,
                             relationships, '0', '0']

            training_data.append(training_item)

    return training_data


def make_annotation_types(annotations: list, ef: EntityInfo) -> list:
    """
    Extract information the type of annotation for a given entity code (e.g. C124894)

    @param annotations: List of annotations to get information about.
    @param ef: EntityInfo class, used to extract information about informative entities.
    @return: Number of each entity type (uses the list of informative entity types defined in
    relevanceRanking.connect_to_kb)
    """
    types_counts = {}

    for entity in informative_entity_types:
        types_counts[entity] = 0

    if annotations is not None:
        for annotation in annotations:
            try:
                types = ef.get_entity_types(annotation)

            except ValueError as ve:
                print("Value could not be found: " + str(annotation))
                continue

            for entity_type in types:
                types_counts[entity_type] += 1

    output_counts = []
    for entity in informative_entity_types:
        output_counts.append(types_counts[entity])

    return output_counts


def write_out_training_data(output_path: str, data: list) -> None:
    """
    Write out training pairs to a tab-separated text file.

    @param output_path: Path to the output file.
    @param data: Training pairs to be written.
    @return: None
    """
    with open(os.path.join(output_path, output_filename), "w+", encoding="utf8") as training_file:

        training_file.write(
            "query_category" + "\t" + "query_thread" + "\t" + "query_id" + "\t" + "query_text" + "\t" + "query_username" + "\t" + "query_annotations" + "\t" + all_types + "\t" +
            "document_category" + "\t" + "document_id" + "\t" + "document_thread" + "\t" + "document_text" + "\t" + "document_is_doctor_reply" + "\t" +
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


def pair_up(category_map: dict, similar_map: dict, used_queries_count: dict) -> dict:
    """
    Create pair between query IDs and document IDs based on similarity between forum categories.

    @param category_map: List of Query IDs sorted by category
    @param similar_map: Dictionary, where key: category, value: [similar category1, similar category2,
    similar category3]
    @param used_queries_count: Queries used in creating relevant pairs.
    @return: Dictionary of paired IDs in form key: Query ID, value: [List of document IDs paired with this query]
    """
    print('Started making pairs.')

    for category in category_map:
        random.shuffle(category_map[category]['documents'])

    category_map_untouched = copy.deepcopy(category_map)

    pairs = {}
    for category in category_map:
        similar_category = [similar_map[category]['1'], similar_map[category]['2'], similar_map[category]['3']]

        for query in category_map[category]['queries']:
            if query not in used_queries_count:
                continue

            for i in range(0, used_queries_count[query]):
                if len(category_map[similar_category[0]]['documents']) > 0:
                    document = category_map[similar_category[0]]['documents'].pop()
                elif len(category_map[similar_category[1]]['documents']) > 0:
                    document = category_map[similar_category[1]]['documents'].pop()
                elif len(category_map[similar_category[2]]['documents']) > 0:
                    document = category_map[similar_category[2]]['documents'].pop()
                else:
                    # print('Ran out of unique doc. Using a random similar document.')
                    document = random.choice(category_map_untouched[similar_category[0]]['documents'])

                if query not in pairs:
                    pairs[query] = [document]
                elif document in pairs[query]:
                    continue
                else:
                    pairs[query].append(document)

    return pairs


def remap_similar_categories(forum_specific: dict) -> dict:
    """
    Pairs of similar categories are created using forum-specific category names, whereas JSON files contain the unified,
    forum-independent category name. This functions converts the mapping of forum specific names to mapping of forum-
    independent names.

    @param forum_specific: Map of forum-specific similar categories.
    @return: Map of forum independent categories.
    """

    print('Started category remapping.')

    category_mapping = read_json_file(old_new_categories_map)
    new_mapping = {}

    for category in forum_specific:

        common_category = category_mapping[category]

        new_mapping[common_category] = {}
        for sim_level in forum_specific[category]:
            new_mapping[common_category][sim_level] = category_mapping[forum_specific[category][sim_level]]

    return new_mapping


if __name__ == '__main__':

    ef = EntityInfo()
    random.seed('1234')

    category_files = read_json_file(category_file)
    similar_map = read_similar_file(similar_categories_map)
    used_queries_counts = read_json_file(used_queries_count_path)

    similar_map = remap_similar_categories(similar_map)

    selected_pairs = pair_up(category_files, similar_map, used_queries_counts)

    full_queries = make_queries(list(selected_pairs.keys()), ef)

    document_ids = set()

    for query in selected_pairs:
        for post_id in selected_pairs[query]:
            document_ids.add(post_id)

    full_documents = find_documents(document_ids)
    training_data = produce_training_data(selected_pairs, full_queries, full_documents, ef)
    write_out_training_data(output_filename, training_data)
