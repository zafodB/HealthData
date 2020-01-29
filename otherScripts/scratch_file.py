'''
 * Created by filip on 29/11/2019
'''

# %%

import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, average_precision_score

df_valid = pd.read_csv("d:/downloads/json/ehealthforum/trac/validation_df2.txt", sep="\t", header=0)
df_valid = df_valid.drop('Unnamed: 0', axis=1)


doc_column_list = [
    'd_typ_dsyn',  # disease or syndrome
    'd_typ_patf',  # pathological function
    'd_typ_sosy',  # sign or syndrome
    'd_typ_dora',  # daily or recreational activity
    'd_typ_fndg',  # finding
    'd_typ_menp',  # mental process
    'd_typ_chem',  # chemical
    'd_typ_orch',  # organic chemical
    'd_typ_horm',  # hormone
    'd_typ_phsu',  # pharmacological substance
    'd_typ_medd',  # medical device
    'd_typ_bhvr',  # behaviour
    'd_typ_diap',  # diagnostic procedure
    'd_typ_bacs',  # biologically active substance
    'd_typ_enzy',  # enzyme
    'd_typ_inpo',  # injury or poisoning
    'd_typ_elii',  # element, ion or isotope
]

query_column_list = [
    'typ_dsyn',  # disease or syndrome
    'typ_patf',  # pathological function
    'typ_sosy',  # sign or syndrome
    'typ_dora',  # daily or recreational activity
    'typ_fndg',  # finding
    'typ_menp',  # mental process
    'typ_chem',  # chemical
    'typ_orch',  # organic chemical
    'typ_horm',  # hormone
    'typ_phsu',  # pharmacological substance
    'typ_medd',  # medical device
    'typ_bhvr',  # behaviour
    'typ_diap',  # diagnostic procedure
    'typ_bacs',  # biologically active substance
    'typ_enzy',  # enzyme
    'typ_inpo',  # injury or poisoning
    'typ_elii',  # element, ion or isotope
]


def calculate_overlap_coef(x):
    try:
        document_annotations = set(x['document_annotations'])
        query_annotations = set(x['query_annotations'])
    except TypeError:  # This is raised if document_annotations is 'nan'
        return 0

    smaller = document_annotations if len(document_annotations) < len(query_annotations) else query_annotations

    if len(smaller) == 0:
        return 0
    else:
        return len(document_annotations.intersection(query_annotations)) / len(smaller)


def calculate_jaacard(x):
    try:
        document_annotations = set(x['document_annotations'])
        query_annotations = set(x['query_annotations'])
    except TypeError:  # This is raised if document_annotations is 'nan'
        return 0

    if len(document_annotations.union(query_annotations)) == 0:
        return 0
    else:
        return len(document_annotations.intersection(query_annotations)) / len(
            document_annotations.union(query_annotations))


def entity_type_overlap(x):
    doc_entities = set()
    query_entities = set()

    for column in doc_column_list:
        if x[column] > 0:
            # print(column[2:])
            doc_entities.add(column[2:])

    for column in query_column_list:
        if x[column] > 0:
            query_entities.add(column)

    return len(doc_entities.intersection(query_entities))


def entity_type_overlap_fraction(x):
    doc_entities = set()
    query_entities = set()

    for column in doc_column_list:
        if x[column] > 0:
            # print(column[2:])
            doc_entities.add(column[2:])

    for column in query_column_list:
        if x[column] > 0:
            query_entities.add(column)

    if len(doc_entities) + len(query_entities) == 0:
        return 0
    else:
        return len(doc_entities.intersection(query_entities)) / (len(doc_entities) + len(query_entities) )


def entity_type_overlap_jacc(x):
    doc_entities = set()
    query_entities = set()

    for column in doc_column_list:
        if x[column] > 0:
            # print(column[2:])
            doc_entities.add(column[2:])

    for column in query_column_list:
        if x[column] > 0:
            query_entities.add(column)

    if len(doc_entities.union(query_entities)) == 0:
        return 0
    else:
        return len(doc_entities.intersection(query_entities)) / (len(doc_entities.union(query_entities)) )

df_valid['entity_overlap_coef'] = df_valid.apply(calculate_overlap_coef, axis=1)
df_valid['entity_jacc'] = df_valid.apply(calculate_jaacard, axis=1)
df_valid['entity_type_overlap_jacc'] = df_valid.apply(entity_type_overlap_jacc, axis=1)

plt.hist(df_valid['entity_jacc'], bins=8)
# plt.hist(df_valid['entity_jacc'], bins=8)
plt.show()
