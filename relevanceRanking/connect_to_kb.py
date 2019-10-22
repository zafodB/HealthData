'''
 * Created by filip on 22/10/2019
'''

from elasticsearch import Elasticsearch

informative_entity_types = {"dsyn", "patf", "sosy", "dora", "fndg", "menp", "chem", "orch", "horm", "phsu", "medd",
                            "bhvr", "diap", 'bacs', 'chem', 'enzy', "inpo", "elii"}
uninformative_entity_types = {"phpr", "npop", 'bsoj', 'idcn', "sbst", "food", "evnt", "geoa", "idcn"}


def connect_elasticsearch():
    _es = Elasticsearch([{"host": "d5hadoop22.mpi-inf.mpg.de", "client.transport.sniff": True, "port": 9200}])
    return _es


def entity_info(es_object, index_name, entity):
    res = es_object.search(index=index_name, size=1, search_type="dfs_query_then_fetch",
                           _source_includes=["human_readable", "types"], body={
            "filter": {"bool": {"must": [{"term": {"kb_id": entity}},
                                         {"term": {"_type": "entity"}}]}}})
    return res["hits"]["hits"][0]["_source"]


def is_informative_entity(es, entity=""):
    ei = entity_info(es, "health-kb", entity)

    types = []

    if "types" in ei.keys():
        types = [str(x) for x in ei["types"]]

    return len(set(types).intersection(informative_entity_types)) > 0 or len(
        [x for x in types if x.startswith("disease_affecting") or x.startswith("symptoms")]) > 0


es = connect_elasticsearch()

# is_informative_entity(es, "C0037199")

print(is_informative_entity(es, "C0037199"))
