'''
 * Created by filip on 19/12/2019
'''

import json
import os

from collection import COLLECTIONS

from benchmark import Benchmark
from utils.loginit import get_logger

logger = get_logger(__name__)  # pylint: disable=invalid-name


@Benchmark.register
class Filip0Benchmark(Benchmark):
    name = "filip0bench"
    query_type = "title"

    @staticmethod
    def config():
        fold = "s1"
        searcher = "bm25rm3yang19"
        collection = "filip0"
        rundocsonly = False  # use only docs from the searcher as pos/neg training instances (i.e., not all qrels)
        maxqlen = 4
        maxdoclen = 800
        niters = 50
        batch = 32
        lr = 0.001
        softmaxloss = False

        stemmer = None
        indexstops = False
        return locals().copy()  # ignored by sacred

    def build(self):
        self.folds = json.load(open(os.path.join(self.collection.basepath, "filip0folds.json"), "rt"))
        self.create_and_store_train_and_pred_pairs(self.folds)
