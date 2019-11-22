"""
 * Created by filip on 25/10/2019

 Contains EntityInfo class for retrieving information about named entities from the Knowledge base (built after UMLS
  corpus), such as whether an entity is informative or the entity type and relations between entities.

  Also contains utility function to extract entity codes from a string.
"""

import platform
import json
import re
from relevanceRanking.connect_to_kb import connect_elasticsearch, get_entity_types


def get_entity_code(entity):
    """
    Return the first C-code from a string.
    @param entity: String including the entity code. Can include pipes, brackets and other characters.
    @return: The C-code in form C123456
    """
    pattern = re.compile('C[0-9]{3,}')

    try:
        stripped = re.search(pattern, entity)
    except AttributeError:
        entity = entity.group()
        stripped = re.search(pattern, entity)

    if stripped is None:
        return None
    else:
        return stripped.group()


class EntityInfo:
    __informative_nodes_list_location = None
    __other_nodes_list_location = None

    __elastic_search = None

    informative_entities = None
    other_entities = None
    entity_types = None

    def __init__(self):
        on_server = platform.system() == "Linux"

        if on_server:
            self.__informative_nodes_list_location = "/home/fadamik/Documents/informative_nodes.txt"
            self.__informative_nodes_categories_location = "/home/fadamik/Documents/informative_nodes_categories.json"
            self.__other_nodes_list_location = "/home/fadamik/Documents/other_nodes.txt"
            self.__entity_relations_list_location = "/home/fadamik/Documents/knowledge-graph/informative_edges.json"

        else:
            self.__informative_nodes_list_location = "D:/downloads/json/informative_nodes.txt"
            self.__informative_nodes_categories_location = "d:/downloads/json/informative_nodes_categories.json"
            self.__other_nodes_list_location = "D:/downloads/json/other_nodes.txt"
            self.__entity_relations_list_location = "m:/Documents/knowledge-graph/informative_edges.json"

        self.__elastic_search = connect_elasticsearch()
        self.__load_entity_types()

    def __load_entity_types(self) -> None:
        """
        Load list of informative and non-informative (other) entities from the specified file for use inside the class.
        @return: None
        """
        i_entities = set()
        with open(self.__informative_nodes_list_location, "r", encoding="utf8") as file:
            for line in file:
                i_entities.add(line.replace("\n", ""))

        o_entities = set()
        with open(self.__other_nodes_list_location, "r", encoding="utf8") as file:
            for line in file:
                o_entities.add(line.replace("\n", ""))

        # entity_t = {}
        with open(self.__informative_nodes_categories_location, "r", encoding="utf8") as file:
            entity_t = json.load(file)

        print("Loaded existing entity information files")
        self.informative_entities = i_entities
        self.other_entities = o_entities
        self.entity_types = entity_t

    def update_informative_list(self, informative_entity: str) -> None:
        """
        Update the list of informative entities with a new relevant relevant entity
        @param informative_entity: New addition to the list
        @return: None
        """
        self.informative_entities.add(informative_entity)

        with open(self.__informative_nodes_list_location, "a", encoding="utf8") as file:
            file.write(informative_entity + "\n")

    def update_other_list(self, other_entity: str) -> None:
        """
        Update the list of non-informative entities with a new non-relevant entity.

        @param other_entity: A new addition to the list of "other entities"
        @return: None
        """
        self.other_entities.add(other_entity)

        with open(self.__other_nodes_list_location, "a", encoding="utf8") as file:
            file.write(other_entity + "\n")

    def update_entity_types(self, entity: str, types: set) -> None:
        """
        Update the list of entity types with new entries.
        @param entity: The entity for which the information should be updated.
        @param types: Set containing the types of the entity.
        @return: None
        """
        if entity not in self.entity_types:
            self.entity_types[entity] = types

    def write_out_entity_types(self) -> None:
        """
        Write entity types from memory into a file.
        @return: None
        """
        entity_t = {}

        for entity in self.entity_types:
            entity_t[entity] = list(self.entity_types[entity])

        with open(self.__informative_nodes_categories_location, "w+", encoding="utf8") as file:
            json.dump(entity_t, file)

    def is_informative_entity(self, entity: str) -> bool:
        """
        Return whether the given entity is relevant (whether at least one of its types is in the list of informative
        types.
        @param entity: Entity code to evaluate (without brackets or pipes, in form C123546)
        @return: True if entity is informative, False otherwise
        """

        informative = None

        if entity in self.informative_entities:
            informative = True
        if entity in self.other_entities:
            informative = False

        if informative is None:
            types = get_entity_types(entity, self.__elastic_search)

            if len(types) > 0:
                self.update_informative_list(entity)
                self.update_entity_types(entity, types)
                informative = True
            else:
                self.update_other_list(entity)
                informative = False

        return informative

    def get_entity_types(self, entity: str) -> list:
        """
        Get list of all the types of a named entity.

        @param entity: Entity to retireve the types of (without brackets or pipes, in form C123546).
        @return: List of types as 4 letter strings.
        """
        if entity not in self.entity_types:
            self.is_informative_entity(entity)

        # TODO Should be rewritten to handle unknown entity properly
        if entity in self.entity_types:
            return self.entity_types[entity]
        else:
            return ""

    def get_entity_relations(self) -> dict:
        """
        Load from file and return relationshipss between all entities (according to Knowledge base)
        @return: Dictionary with relations (form:
                entity1: {
                            entity2: [relationship-type1, relationship-type2],
                            entity3: [...]
                        }
        """
        with open(self.__entity_relations_list_location, "r", encoding="utf8") as relationship_file:
            entity_list = json.load(relationship_file)
            print("Loaded entity relations file.")

        return entity_list
