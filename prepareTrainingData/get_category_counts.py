"""
 * Created by filip on 13/12/2019

 Determine which query belongs to which category and save this overview to a file. This file is used as input to
 prepare_nonrelevant_data.py
"""

import json
import os
import platform

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory = "/home/fadamik/Documents/"


else:
    starting_directory = "D:/Downloads/json/ehealthforum/json-annotated"
    output_directory = "D:/Downloads/json/ehealthforum/"


category_mapping = {}
processed_files = 0


for root, dirs, files in os.walk(starting_directory):
    for file_name in files:

        try:
            with open(os.path.join(root, file_name), 'r', encoding='utf8') as file:
                # print('Now processing file: ' + os.path.join(root, file_name))
                contents = json.load(file)

                category = contents['commonCategory']
                number_replies = contents['replyCount']

                query_number = contents['threadId']

                document_numbers = []

                for index, reply in enumerate(contents['replies']):
                    if index == 0:
                        continue
                    else:
                        document_numbers.append('EF-' + str(int(contents['threadId'], base=10)) + "r" + str(index))

                if category not in category_mapping:
                    category_mapping[category] = {'queries': [query_number], 'documents': document_numbers}
                else:
                    category_mapping[category]['queries'].append(query_number)

                    category_mapping[category]['documents'] += document_numbers

            processed_files += 1
        except IndexError:
            continue

        if processed_files % 100 == 0:
            print("Processed files: " + str(processed_files))


with open(os.path.join(output_directory, 'category_maps_ehf_2.json'), 'w+', encoding='utf8') as output_file:
    json.dump(category_mapping, output_file)
