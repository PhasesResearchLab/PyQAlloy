from importlib import resources
import json
from pymongo import MongoClient
from pymongo.collection import Collection
from pymatgen.core import Composition
from sklearn.neighbors import NearestNeighbors


class Analyzer:
    def __init__(self, database, collection):
        with resources.files('ulteratools').joinpath('credentials.json').open('r') as f:
            self.credentials = json.load(f)
        self.ultera_database_uri = f"mongodb+srv://{self.credentials['name']}:{self.credentials['dbKey']}" \
                                   f"@testcluster.g3kud.mongodb.net/ULTREA_materials?retryWrites=true&w=majority"
        self.ultera_client = MongoClient(self.ultera_database_uri)
        self.collection = self.ultera_client[database][collection]
        print(f'Connected to the {collection} in {database} with {self.collection.estimated_document_count()} data '
              f'points detected.')

    def get_allDOIs(self):
        return [e['doi'] for e in self.collection.aggregate([
            {'$match': {'reference.doi': {'$ne': None}}},
            {'$group': {'_id': '$reference.doi'}},
            {'$set': {'doi': '$_id', '_id': '$$REMOVE'}}])]

class SingleDOIAnalyzer(Analyzer):

    def __init__(self, doi=None, name=None, database='ULTERA', collection='CURATED'):
        super().__init__(database=database, collection=collection)
        self.name = name
        self.doi = doi
        self.formulas = set()
        self.nn_distances = list()
        self.names = set()
        self.els = set()
        self.compVecs = list()
        self.fStrings = list()
        self.printLog = str()
        print(f'********  Analyzer Initialized  ********')


    def setDOI(self, doi: str):
        self.doi = doi

    def setName(self, name):
        self.name = name

    def getCompVecs(self, collection: Collection, doi: str):
        # Reset formulas, els, etc
        self.formulas, self.els, self.names, self.compVecs, self.fStrings = set(), set(), set(), list(), list()
        # Find a set of unique formulas from DOI and a set of all elements present in them
        for e in collection.find({'reference.doi': doi}):
            c = Composition(e['material']['formula'])
            self.formulas.add(c.reduced_formula)
            self.names.add(e['meta']['name'])
            self.els.update(list(c.get_el_amt_dict().keys()))
            self.fStrings.append(
                e['material']['formula']#+'<br>'+
                #e['material']['percentileFormula']+'<br>'+
                #e['material']['relationalFormula']
                )
        # Vectorize based on a list of elements
        self.els = list(self.els)
        for f in self.formulas:
            cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
            compVec = [cd[el] if el in cd else 0 for el in self.els]
            self.compVecs.append(compVec)

    def analyze_nnDistances(self):
        nn = NearestNeighbors(n_neighbors=2, metric='l1', algorithm='kd_tree')
        self.getCompVecs(collection=self.collection, doi=self.doi)
        self.nn_distances = [l[1] for l in nn.fit(self.compVecs).kneighbors(self.compVecs)[0]]

    def print_nnDistances(self, minSamples=2, printOut=True):
        assert self.compVecs is not None
        assert self.nn_distances is not None
        assert len(self.formulas)==len(self.nn_distances)
        if len(self.nn_distances)>=minSamples:
            if self.name is None or self.name in self.names:
                maxD = max(self.nn_distances)
                self.printLog += f'\n--->  {self.doi}'
                for l, f in zip(self.nn_distances, self.formulas):
                    temp_line = f'{round(l, 4):<10}|  {round(l/maxD, 4):<10} <-- {f}'
                    self.printLog += temp_line+'\n'
                    if printOut:
                        print(temp_line)
                self.printLog += '\n'
            else:
                temp_message = f'Skipping {self.doi}. Specified researcher ({self.name}) not present in the group ({self.names})'
                self.printLog += temp_message
                if printOut:
                    print(temp_message)
        else:
            temp_message = f'Skipping {self.doi}. Not enough data samples (minSamples={minSamples})'
            self.printLog += temp_message
            if printOut:
                print(temp_message)


