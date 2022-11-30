from importlib import resources
import json
from pymongo import MongoClient
from pymongo.collection import Collection
from pymatgen.core import Composition
from sklearn.neighbors import NearestNeighbors


def getCompVecs(collection: Collection, doi: str):
    formulas, els, compVecs = set(), set(), list()
    # Find a set of unique formulas from DOI and a set of all elements present in them
    for e in collection.find({'reference.doi': doi}):
        c = Composition(e['material']['formula'])
        formulas.add(c.reduced_formula)
        els.update(list(c.get_el_amt_dict().keys()))
    # Vectorize based on a list of elements
    els = list(els)
    for f in formulas:
        cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
        compVec = [cd[el] if el in cd else 0 for el in els]
        compVecs.append(compVec)

    return compVecs, formulas, els

class AbnormalDataAnalyzer:
    def __init__(self, database='ULTERA', collection='CURATED', name=None):
        with resources.files('ulteratools').joinpath('credentials.json').open('r') as f:
            self.credentials = json.load(f)
        self.ultera_database_uri = f"mongodb+srv://{self.credentials['name']}:{self.credentials['dbKey']}" \
                                   f"@testcluster.g3kud.mongodb.net/ULTREA_materials?retryWrites=true&w=majority"
        self.ultera_client = MongoClient(self.ultera_database_uri)
        self.collection = self.ultera_client[database][collection]
        print(f'Connected to the {collection} in {database} with {self.collection.estimated_document_count()} data '
              f'points detected.')
        print(f'********  AbnormalDataAnalyzer Initialized  ********')


    def analyze_nnDistances(self, doi: str):
        nn = NearestNeighbors(n_neighbors=2, metric='l1', algorithm='kd_tree')
        compVecs, formulas, els = getCompVecs(collection=self.collection, doi=doi)
        nn_distances = [l[1] for l in nn.fit(compVecs).kneighbors(compVecs)[0]]
        return nn_distances

    def print_nnDistances(self, formulas: list, nn_distances: list):
        assert len(formulas)==len(nn_distances)
        maxD = max(nn_distances)
        for l, f in zip(nn_distances, formulas):
            print(f'{round(l, 4):<10}|  {round(l/maxD, 4):<10} <-- {f}')

    