from importlib import resources
import json
from pymongo import MongoClient
from pymongo.collection import Collection
from pymatgen.core import Composition
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

from scipy.spatial import distance_matrix
from statistics import mean

from datetime import datetime

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

import xlsxwriter
from io import BytesIO

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
        self.resetVariables()

        print(f'********  Analyzer Initialized  ********')

    def resetVariables(self):
        self.pointers = set()
        self.formulas = list()
        self.nn_distances = list()
        self.names = set()
        self.els = set()
        self.compVecs = list()
        self.fStrings = list()
        self.printLog = str()

        self.compVecs_2DPCA = list()
        self.compVecs_2DPCA_plot = None
        self.compVecs_2DPCA_minRangeInDim = None

    def setDOI(self, doi: str):
        self.doi = doi
        self.resetVariables()

    def setName(self, name):
        self.name = name

    def getCompVecs(self):
        # Reset formulas, els, etc
        self.formulas, self.els, self.names, self.compVecs, self.fStrings = list(), set(), set(), list(), list()
        # Find a set of unique formulas from DOI and a set of all elements present in them
        for e in self.collection.find({'reference.doi': self.doi}):
            c = Composition(e['material']['formula'])
            reducedFormula = c.reduced_formula
            if reducedFormula not in self.formulas:
                self.formulas.append(reducedFormula)
                self.names.add(e['meta']['name'])
                self.els.update(list(c.get_el_amt_dict().keys()))
                self.fStrings.append(
                    e['material']['percentileFormula']#+'<br>'+
                    #e['material']['percentileFormula']+'<br>'+
                    #e['material']['relationalFormula']
                    )
            if 'pointer' in e['reference']:
                self.pointers.add(e['reference']['pointer'])
        # Vectorize based on a list of elements
        self.els = list(self.els)
        for f in self.formulas:
            cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
            compVec = [cd[el] if el in cd else 0 for el in self.els]
            self.compVecs.append(compVec)

    def analyze_nnDistances(self):
        nn = NearestNeighbors(n_neighbors=2, metric='l1', algorithm='kd_tree')
        self.getCompVecs()
        self.nn_distances = [l[1] for l in nn.fit(self.compVecs).kneighbors(self.compVecs)[0]]

    def print_nnDistances(self, minSamples=2, printOut=True):
        assert len(self.compVecs)>0
        assert len(self.nn_distances)>0
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
                temp_message = f'Skipping {self.doi:<20}. Specified researcher ({self.name}) not present in the group ({self.names})'
                self.printLog += temp_message
                if printOut:
                    print(temp_message)
        else:
            temp_message = f'Skipping {self.doi:<20}. Not enough data samples (minSamples={minSamples})'
            self.printLog += temp_message
            if printOut:
                print(temp_message)

    def get_compVecs_2DPCA(self):
        assert len(self.compVecs)>0
        pca = PCA(n_components=2)
        self.compVecs_2DPCA = pca.fit_transform(self.compVecs)
        self.compVecs_2DPCA_minRangeInDim = min([
            max(self.compVecs_2DPCA[:, 0]) - min(self.compVecs_2DPCA[:, 0]),
            max(self.compVecs_2DPCA[:, 1]) - min(self.compVecs_2DPCA[:, 1])])

    def analyze_compVecs_2DPCA(self, minDistance=0.001, showFigure=True):
        assert len(self.compVecs_2DPCA) > 0
        assert len(self.formulas) > 0
        assert len(self.fStrings) > 0
        if self.compVecs_2DPCA_minRangeInDim > minDistance:
            fig = px.scatter(
                x=self.compVecs_2DPCA[:, 0],
                y=self.compVecs_2DPCA[:, 1],
                color=self.fStrings,
                hover_name=self.fStrings,
                color_discrete_sequence=px.colors.qualitative.Dark24,
                width=900, height=400,
                title=f'<b>{self.doi}</b>  --> {", ".join(self.pointers)}<br>parsed by {", ".join(self.names)}',
                labels={'x': 'PCA1', 'y': 'PCA2', 'color': 'Alloy Reported'},
                template='plotly_white')
            fig.update_traces(
                marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
            self.compVecs_2DPCA_plot = BytesIO(fig.to_image(format="png", scale=5))
            if showFigure:
                fig.show()
        else:
            print(f'Skipping {self.doi:<20} Nearly 1D linear trand detected.')

    def writePlot(self, workbookPath: str, skipLines: int):
        assert isinstance(self.compVecs_2DPCA_plot, BytesIO)
        workbook = xlsxwriter.Workbook(workbookPath)
        worksheet = workbook.add_worksheet()
        cellIndex = f'A{1+skipLines}'
        worksheet.insert_image(cellIndex, self.doi, {'image_data': self.compVecs_2DPCA_plot, 'x_scale': 0.2, 'y_scale': 0.2})
        workbook.close()

    def writeManyPlots(self, toPlotList: list, workbookPath: str):
        workbook = xlsxwriter.Workbook(workbookPath)
        worksheet = workbook.add_worksheet()
        skipLines = 0

        for tp in toPlotList:
            cellIndex = f'A{1 + skipLines}'
            if isinstance(tp, BytesIO):
                worksheet.insert_image(cellIndex, self.doi,
                                       {'image_data': tp, 'x_scale': 0.2, 'y_scale': 0.2})
                skipLines += 21
            elif isinstance(tp, str):
                worksheet.write(cellIndex, tp)
                skipLines += 1
        workbook.close()


class SingleCompositionAnalyzer(Analyzer):

    def __init__(self, name=None, database='ULTERA', collection='CURATED'):
        super().__init__(database=database, collection=collection)
        self.name = name
        self.formulas = set()
        self.printOuts = list()

    def scanCompositionsAround100(self,
                                  lowerBound=80,
                                  uncertainty=0.21,
                                  upperBound=120,
                                  queryLimit=10000,
                                  resultLimit=1000,
                                  printOnFly=False):

        query = {'reference.doi': {'$ne': None}}
        if self.name is not None:
            query.update({'meta.name': self.name})
        for e in self.collection.find(query, limit=queryLimit):
            f = e['material']['formula']
            if f not in self.formulas:
                self.formulas.add(f)
                c = Composition(f)
                fracs = list(c.get_el_amt_dict().values())
                fracsSum = round(sum(fracs), 3)

                def printAlloy(self):
                    printOut =  f"DOI: {e['reference']['doi']}"
                    if 'pointer' in e['reference']:
                        printOut += f"  --> {e['reference']['pointer']}"
                    printOut += f"\nF:   {f}\n"
                    printOut += f"PF:  {e['material']['percentileFormula']}\n"
                    printOut += f"Raw:  {e['material']['rawFormula']}\n"
                    printOut += f"RF:  {e['material']['relationalFormula']}\n"
                    printOut += str(fracs)
                    printOut += f'\n-->  {fracsSum}\n'
                    self.printOuts.append(printOut)
                    if printOnFly:
                        print(printOut)

                if fracsSum>lowerBound and fracsSum<(100-uncertainty):
                    printAlloy(self)
                elif fracsSum>lowerBound/100 and fracsSum<(100-uncertainty)/100:
                    printAlloy(self)
                elif fracsSum<upperBound and fracsSum>(100+uncertainty):
                    printAlloy(self)
                elif fracsSum<upperBound/100 and fracsSum>(100+uncertainty)/100:
                    printAlloy(self)

            if len(self.printOuts)>resultLimit:
                break

    def writeResultsToFile(self, fileName: str):
        assert len(self.printOuts)>0
        with open(fileName, 'w+') as f:
            f.write(datetime.now().strftime("%c"))
            f.write('\n')
            for printOut in self.printOuts:
                f.write(printOut)
                f.write('\n')