"""
 * Created by filip on 21/01/2020

 Specify the folds for Capreolus (it won't run without it). Query numbers are divided into train, dev and test part in
 each fold. Each query number should appear at least once in the train part and once in test part. Query numbers cannot
 be repeated within one fold.

 Input:     Balanced qrels file created by combine_qrels.py
 Output:    Folds file in .json. Should be included in capreolus/benchmark folder
"""

import json
import platform

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    # INPUT
    qrels_path = ''

    # OUTPUT
    folds_path = ''
else:
    # INPUT
    qrels_path = 'd:/downloads/json/ehealthforum/trac/qrels_ehf_all_balanced.txt'

    # OUTPUT
    folds_path = 'd:/Downloads/json/ehealthforum/trac/filip0folds.json'

topic_ids = set()
with open(qrels_path, 'r', encoding='utf8') as file:
    for line in file:
        query, run, document, relevance = line.split('\t')
        topic_ids.add(query)

topic_ids = list(topic_ids)

topic_ids.sort()

output = {}
NUMBER_FOLDS = 3

part_length = len(topic_ids) // NUMBER_FOLDS
splits = [topic_ids[0: part_length], topic_ids[part_length: 2 * part_length], topic_ids[2 * part_length:]]

for fold in range(0, NUMBER_FOLDS):
    fold_name = 's' + str(fold + 1)

    output[fold_name] = {'train_qids': [], 'predict': {'dev': [], 'test': []}}

    output[fold_name]['train_qids'].extend(splits[fold % NUMBER_FOLDS])
    output[fold_name]['predict']['dev'].extend(splits[(fold + 1) % NUMBER_FOLDS])
    output[fold_name]['predict']['test'].extend(splits[(fold + 2) % NUMBER_FOLDS])

with open(folds_path, 'w+') as out_file:
    json.dump(output, out_file)
    print('Wrote folds to file: ' + folds_path)
