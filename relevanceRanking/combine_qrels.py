'''
 * Created by filip on 16/01/2020
'''

import pandas as pd
import platform
import random

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    relevant_qrels_path = '/scratch/GW/pool0/fadamik/ehealthforum/trac/qrels_ehf_rel.txt'
    nonrelevant_qrels_path = '/scratch/GW/pool0/fadamik/ehealthforum/trac/qrels_ehf_non.txt'
    output_path = '/scratch/GW/pool0/fadamik/ehealthforum/trac/qrels_ehf_all_balanced.txt'
else:
    relevant_qrels_path = 'd:/downloads/json/ehealthforum/trac/qrels_ehf_rel_test.txt'
    nonrelevant_qrels_path = 'd:/downloads/json/ehealthforum/trac/qrels_ehf_non_test.txt'
    output_path = 'd:/downloads/json/ehealthforum/trac/qrels_ehf_all_balanced_test.txt'


def read_qrel_file(path: str, judgements=None) -> dict:
    """
     Read relevant or non-relevant qrel file at the specified location.

    @param path: Location of the file to read.
    @param judgements: Dictionary to update with new data (if exists). Default=none
    @return: Qrels as dictionary in the form:
                {query-id:
                    {'negative-judgement': [list of document ids],
                    'positive-judgement': [list of document ids]}
                }
    """
    if judgements is None:
        judgements = {}

    with open(path, 'r', encoding='utf8') as file:
        for line in file:
            query, run, document, judgement = line.replace('\n', '').split('\t')

            if query not in judgements:
                judgements[query] = {'0': [], '1': []}

            judgements[query][judgement].append(document)

    return judgements


def balance_classes(judgements: dict) -> dict:
    """
    Balance the number of relevant and non-relevant judgements for each class by removing excessive judgements.

    @param judgements: Unbalanced judgements in dictionary.
    @return: Balanced judgements in dictioary.
    """
    for query in judgements:
        if '0' not in judgements[query] or '1' not in judgements[query]:
            continue
        else:
            differece = len(judgements[query]['1']) - len(judgements[query]['0'])

            if differece > 0 :
                random.shuffle(judgements[query]['1'])
                for _ in range(0, differece):
                    judgements[query]['1'].pop()
            else:
                random.shuffle(judgements[query]['0'])
                for _ in range(0, abs(differece)):
                    judgements[query]['0'].pop()

    return judgements


def write_out(output_dict: dict, path: str) -> None:
    """
    Write the judgment dictionary to a file.

    @param output_dict: Judgment dictionary to output
    @param path: Location of output file.
    @return: None
    """
    with open(path, 'w+', encoding='utf8') as file:
        for query in output_dict:
            for judgement in output_dict[query]:
                for document in output_dict[query][judgement]:
                    file.write(query + '\t0\t' + document + '\t' + judgement + '\n')


qrels_judgements = read_qrel_file(relevant_qrels_path)
qrels_judgements = read_qrel_file(nonrelevant_qrels_path, qrels_judgements)

qrels_judgements = balance_classes(qrels_judgements)
write_out(qrels_judgements, output_path)
