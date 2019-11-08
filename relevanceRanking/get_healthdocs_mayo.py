'''
 * Created by filip on 01/11/2019
'''

import json
import re
from relevanceRanking.entities_info import EntityInfo, get_entity_code

with open("d:/downloads/json/mayoclinic.json", "r", encoding="utf8") as file:
    contents = json.load(file)

titles = []
for result in contents['hits']['hits']:
    titles.append(result['_source']['Title'])

print(len(titles))

# print(json.dumps(titles))

mayo_namemap = {}
with open("d:/onedrive/documents/ab germany/health_data/mayo_map.txt", "r", encoding="utf8", errors='ignore') as file:
    for line in file:
        category, mayo_name = line.split(";")
        category = category.lower()
        mayo_name = mayo_name.replace('\n', '').lower()
        mayo_namemap[category] = mayo_name

ef = EntityInfo()

# print(contents['hits']['hits'][1]['_source']['aida']['annotatedText'])

entities_by_category = {}
print("Number of titles: " + str(len(mayo_namemap)))

counter = 0

print('Values:')
print(list(mayo_namemap.values()))


for result in contents['hits']['hits']:
    print(result['_source']['Title'])
    if result['_source']['Title'].find('Abdominal') > 0:
        pass

    if result['_source']['Title'].lower() not in list(mayo_namemap.values()):
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

with open("d:/downloads/json/category_entities.json", "w+", encoding="utf8") as file:
    json.dump(entities_by_category, file)

same_entities = {}
while entities_by_category:
    category1 = entities_by_category.popitem()
    entities1 = set(category1[1])
    same_entities[category1[0]] = {}

    for category2 in entities_by_category:
        entities2 = set(entities_by_category[category2])

        same_entities[category1[0]][category2] = len(entities1.intersection(entities2))

print(same_entities)
with open("d:/downloads/json/entity_intersection.json", "w+", encoding="utf8") as file:
    json.dump(same_entities, file)
