'''
 * Created by filip on 01/11/2019
'''

import json
import re
from relevanceRanking.entities_info import EntityInfo, get_entity_code

with open("/GW/D5data-10/Neural_Health_Semantic_Search/mayoclinic_hits.json", "r", encoding="utf8") as file:
    contents = json.load(file)

titles = []
for result in contents['hits']['hits']:
    titles.append(result['_source']['Title'])

print(len(titles))

# print(json.dumps(titles))

mayo_namemap = {}
with open("/home/fadamik/Documents/mayo_map.csv", "r", encoding="utf8") as file:
    for line in file:
        category, mayo_name = line.split(",")
        mayo_namemap[category] = mayo_name

ef = EntityInfo()

# print(contents['hits']['hits'][1]['_source']['aida']['annotatedText'])

entities_by_category = {}
print("Number of titles: " + len(mayo_namemap))

counter = 0
for result in contents['hits']['hits']:
    if result['_source']['Title'] not in mayo_namemap.values():
        continue

    entities_all = re.findall('\[\[C\d+\|[a-zA-Z]+\]\]', result['_source']['aida']['annotatedText'])
    entities = []
    for entity in entities_all:
        entity_code = get_entity_code(entity)

        if ef.is_informative_entity(entity_code):
            entities.append(entity_code)

    category = result['_source']['Title']
    entities_by_category[category] = entities

    counter += 1
    print("Now processed categories: " + str(counter))

with open("/home/fadamik/Documents/category_entities.json", "w+", encoding="utf8") as file:
    json.dump(entities_by_category, file)
