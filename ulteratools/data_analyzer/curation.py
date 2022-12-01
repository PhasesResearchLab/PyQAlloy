from importlib import resources
import json
from pymongo import MongoClient
from pymongo.collection import Collection
from pymatgen.core import Composition
from sklearn.neighbors import NearestNeighbors


def getCompVecs(collection: Collection, doi: str):
    formulas, els, names, compVecs = set(), set(), set(), list()
    # Find a set of unique formulas from DOI and a set of all elements present in them
    for e in collection.find({'reference.doi': doi}):
        c = Composition(e['material']['formula'])
        formulas.add(c.reduced_formula)
        names.add(e['meta']['name'])
        els.update(list(c.get_el_amt_dict().keys()))
    # Vectorize based on a list of elements
    els = list(els)
    for f in formulas:
        cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
        compVec = [cd[el] if el in cd else 0 for el in els]
        compVecs.append(compVec)

    return compVecs, formulas, names, els

class SingleDOIAnalyzer:
    def __init__(self, doi:str, database='ULTERA', collection='CURATED', name=None):

        with resources.files('ulteratools').joinpath('credentials.json').open('r') as f:
            self.credentials = json.load(f)
        self.ultera_database_uri = f"mongodb+srv://{self.credentials['name']}:{self.credentials['dbKey']}" \
                                   f"@testcluster.g3kud.mongodb.net/ULTREA_materials?retryWrites=true&w=majority"
        self.ultera_client = MongoClient(self.ultera_database_uri)
        self.collection = self.ultera_client[database][collection]
        print(f'Connected to the {collection} in {database} with {self.collection.estimated_document_count()} data '
              f'points detected.')

        self.name = name
        self.doi = doi
        self.formulas = None
        self.nn_distances = None
        self.names = None
        self.els = None
        self.compVecs = None

        print(f'********  AbnormalDataAnalyzer Initialized  ********')

    def get_allDOIs(self):
        return [e['doi'] for e in self.collection.aggregate([
            {'$match': {'reference.doi': {'$ne': None}}},
            {'$group': {'_id': '$reference.doi'}},
            {'$set': {'doi': '$_id', '_id': '$$REMOVE'}}])]

    def analyze_nnDistances(self):
        nn = NearestNeighbors(n_neighbors=2, metric='l1', algorithm='kd_tree')
        self.compVecs, self.formulas, self.names, self.els = getCompVecs(collection=self.collection, doi=self.doi)
        self.nn_distances = [l[1] for l in nn.fit(self.compVecs).kneighbors(self.compVecs)[0]]

    def print_nnDistances(self):
        assert self.compVecs is not None
        assert self.nn_distances is not None
        assert len(self.formulas)==len(self.nn_distances)
        if self.name is None or self.name in self.names:
            maxD = max(self.nn_distances)
            for l, f in zip(self.nn_distances, self.formulas):
                print(f'{round(l, 4):<10}|  {round(l/maxD, 4):<10} <-- {f}')
        else:
            print(f'Skipping {self.doi}. Specified researcher ({self.name}) not present in the group ({self.names})')

