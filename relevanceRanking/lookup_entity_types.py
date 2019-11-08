'''
 * Created by filip on 08/11/2019
'''

from relevanceRanking.entities_info import EntityInfo
from relevanceRanking.connect_to_kb import get_entity_types

informative_entities = set()

with open("/home/fadamik/Documents/informative_nodes.txt", "r", encoding="utf8") as file:
    for line in file:
        informative_entities.add(line.replace("\n", ""))

ei = EntityInfo()

for entity in informative_entities:
    types = get_entity_types(entity, ei.get_es())
    ei.update_entity_types(entity, types)

ei.write_out_entity_types()
