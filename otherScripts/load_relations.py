'''
 * Created by filip on 19/11/2019
'''

import json

relations = {}

file_location = "m:/Documents/knowledge-graph/informative_edges.txt"
output_location = "m:/Documents/knowledge-graph/informative_edges.json"

with open(file_location, 'r', encoding="utf8") as file:
    for line in file:
        line_contents = line.split(',')
        edge_u = line_contents[0].replace(' ', '')
        edge_v = line_contents[1].replace(' ', '')
        type = line_contents[2].replace(' ', '').replace('\n', '')

        if edge_u not in relations:
            relations[edge_u] = {edge_v: type}
        else:
            relations[edge_u][edge_v] = type

with open(output_location, 'w+', encoding="utf8") as file:
    json.dump(relations, file)
