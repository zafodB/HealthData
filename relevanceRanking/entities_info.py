'''
 * Created by filip on 25/10/2019
'''

import platform
from relevanceRanking.connect_to_kb import connect_elasticsearch, is_informative


def get_entity_code(entity: str) -> str:
    pipe_index = entity.find('|')

    if pipe_index == -1:
        return entity
    else:
        return entity[:pipe_index].replace('[', '')


class EntityInfo:
    __starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    __output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/trac/relevance/"
    __informative_nodes_list_location = "/home/fadamik/Documents/informative_nodes.txt"
    __other_nodes_list_location = "/home/fadamik/Documents/other_nodes.txt"

    __elastic_search = None

    informative_entities = None
    other_entities = None

    def __init__(self):
        on_server = platform.system() == "Linux"

        if on_server:
            self.__starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
            self.__output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/trac/relevance/"
            self.__informative_nodes_list_location = "/home/fadamik/Documents/informative_nodes.txt"
            self.__other_nodes_list_location = "/home/fadamik/Documents/other_nodes.txt"

        else:
            self.__starting_directory = "D:/Downloads/json/ehealthforum/json-annotated/"
            self.__output_directory = "D:/downloads/json/ehealthforum/trac/relevance/"
            self.__informative_nodes_list_location = "D:/downloads/json/informative-entities.txt"
            self.__other_nodes_list_location = "D:/downloads/json/other-entities.txt"

        self.__elastic_search = connect_elasticsearch()
        self.__load_entity_types()

    # Load list of informative and non-informative (other) entities from the specified file.
    def __load_entity_types(self) -> None:
        i_entities = set()
        with open(self.__informative_nodes_list_location, "r", encoding="utf8") as file:
            for line in file:
                i_entities.add(line.replace("\n", ""))

        o_entities = set()
        with open(self.__other_nodes_list_location, "r", encoding="utf8") as file:
            for line in file:
                o_entities.add(line.replace("\n", ""))

        self.informative_entities = i_entities
        self.other_entities = o_entities

    # Update the list of informative entities with a new relevant entities.
    def update_informative_list(self, informative_entity: str) -> None:
        self.informative_entities.add(informative_entity)

        with open(self.__informative_nodes_list_location, "a", encoding="utf8") as file:
            file.write(informative_entity + "\n")

    # Update the list of non-informative entities with a new relevant entities.
    def update_other_list(self, other_entity: str) -> None:
        self.other_entities.add(other_entity)

        with open(self.__other_nodes_list_location, "a", encoding="utf8") as file:
            file.write(other_entity + "\n")

    def is_informative_entity(self, entity: str) -> bool:
        return is_informative(entity, self.__elastic_search)
