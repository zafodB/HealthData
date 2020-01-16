'''
 * Created by filip on 13/01/2020
'''

import os
import json

query_numbers = []

with open('/scratch/GW/pool0/fadamik/ehealthforum/trac/noent2/queries/queries0.txt') as file:
# with open('d:/downloads/json/ehealthforum/trac/queries/topic1.txt') as file:
    for line in file:
        if line[0:5] == '<num>':
            query_number = line.split(': ')[1].replace('\n', '')
            # print(query_number)
            query_numbers.append(query_number)

with open('/home/fadamik/Documents/query_numbers_ehf.json', 'w+') as output:
# with open('d:/downloads/json/ehealthforum/query_numbers_ehf.json', 'w+') as output:
    json.dump(query_numbers, output)
