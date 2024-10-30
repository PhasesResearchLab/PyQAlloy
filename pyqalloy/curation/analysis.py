from importlib import resources
import json
from pymongo import MongoClient
from pymongo.collection import Collection
from pymatgen.core import Composition

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

from scipy.spatial import distance_matrix
from statistics import mean

from datetime import datetime

import plotly.express as px

import xlsxwriter
from io import BytesIO
from typing import List, Dict, Tuple, Union


class Analyzer:
    '''Base class for all analyzers. Initializes a connection to the database and collection. Also contains some helper
    functions for data analysis, such as getting a list of all unique DOIs in the collection.

    Args:
        database: Name of the database to connect to.
        collection: Name of the collection to connect to.
        collectionManualOverride: If specified, the collectionManualOverride is used instead of the database and
            collection arguments. It expects a pymongo.collection.Collection object, however, it is not type-checked
            (only hinted) to allow for more flexibility, including instances of
            [MontyDB](https://github.com/davidlatwe/MontyDB) Collection class or
            [Mongomock](https://github.com/mongomock/mongomock) Collection class. Defaults to None and has no effect
            in that case.

    Note:
        The credentials for the database are stored in the credentials.json file in the pyqalloy package. This access
        credentials are not included in the public repository.
    '''

    def __init__(self,
                 database: str,
                 collection: str,
                 collectionManualOverride: Collection = None,
                 credentialsFile: str = None
                 ):
        if collectionManualOverride is not None:
            self.collectionManualOverrideSet = True
            self.collection = collectionManualOverride
            self.ultera_database_uri = None
            self.ultera_client = None
        else:
            self.collectionManualOverrideSet = False
            if credentialsFile is None:
                path = resources.files('pyqalloy').joinpath('credentials.json')
                print(f'Loading the database credentials from default location: {path}')
                with resources.files('pyqalloy').joinpath('credentials.json').open('r') as f:
                    self.credentials = json.load(f)
            else:
                print(f'Loading the database credentials from: {credentialsFile}')
                with open(credentialsFile, 'r') as f:
                    self.credentials = json.load(f)
            if self.credentials['dbKey']=="x2mjf932fhx438hxz932":
                raise ValueError('Database credentials have not been set (the default database key is still in the "credentials.json" file). Please either (1) adjust '\
                                'the credentials.json file in the pyqalloy package to point to your MongoDB-compatible server with ULTERA schema or (2) pass a MongoDB-compatible '\
                                'collection object to the "collectionManualOverride" argument of the Analyzer class.')
            for key in ['name', 'dbKey', 'dataServer']:
                if key not in self.credentials:
                    raise ValueError(f'Credentials file does not contain the required key "{key}". You need to either adjust the credentials file or pass a MongoDB-compatible '\
                                     'collection object to the "collectionManualOverride" argument of the Analyzer class.')
            self.ultera_database_uri = f"mongodb+srv://{self.credentials['name']}:{self.credentials['dbKey']}" \
                                       f"@{self.credentials['dataServer']}"
            self.ultera_client = MongoClient(self.ultera_database_uri)
            self.collection = self.ultera_client[database][collection]
            print(f'Connected to the {collection} in {database} with {self.collection.estimated_document_count()} data '
                  f'points detected.')

    def get_allDOIs(self) -> List[str]:
        '''Returns a list of all unique DOIs in the collection, ordered by the time data has been uploaded (meta.timeStamp) or the unique identifier 
        of the data point if timeStamp order could not be determined. This is useful for iterating over all publications in the collection. If the 
        `collectionManualOverride` is left as None, the function uses the MongoDB aggregation pipeline to perform the operation efficiently on the 
        server side. If the `collectionManualOverride` is specified, the find method is used instead, which is less efficient, but works with other 
        database objects, such as [MontyDB](https://github.com/davidlatwe/MontyDB).

        Returns:
            List of all unique DOIs in the collection ordered by the time data has been uploaded (meta.timeStamp) or the unique identifier 
        of the data point if timeStamp order could not be determined.
        '''

        if not self.collectionManualOverrideSet:
            # Leveraging MongoDB aggregation pipeline to get a list of all unique DOIs efficiently on the server side
            return [e['doi'] for e in self.collection.aggregate([
                    {'$match': {'reference.doi': {'$ne': None}}},
                    {'$group': {
                        '_id': '$reference.doi',
                        'timeStamp': {'$max': '$meta.timeStamp'}
                    }},
                    {'$sort': {
                        'timeStamp': 1,
                        '_id': 1
                    }},
                    {'$set': {'doi': '$_id', '_id': '$$REMOVE'}},
                    {'$project': {'doi': 1, '_id': 0}}
                ])]
        else:
            # In case of a manual override, user is usually trying to "mock" the database and collection objects so
            # the aggregation pipeline may not be available. In that case, we have to utilize the find() method and
            # iterate over all documents in the collection.
            foundDOIs = set()
            allDOIs = list()
            for e in self.collection.find(
                    {'reference.doi': {'$ne': None}}, 
                    {'reference.doi': 1}
                    ).sort([('meta.timeStamp', 1), ('reference.doi', 1)]):
                if e['reference']['doi'] not in foundDOIs:
                    allDOIs.append(e['reference']['doi'])
                    foundDOIs.add(e['reference']['doi'])
            return allDOIs


class SingleDOIAnalyzer(Analyzer):
    '''Extends the Analyzer class. It is used to assess the data coming from a single publication based on the DOI string.

    Args:
        doi: DOI string of the publication to analyze. Defaults to None.
        name: Name of the researcher who uploaded the data. This setting allows limiting the analysis to a person who
            was responsible for the upload. Defaults to None.
        database: Name of the database to connect to. Defaults to 'ULTERA_internal'.
        collection: Name of the collection to connect to. Defaults to 'CURATED_Dec2022'.
        collectionManualOverride: If specified, the collectionManualOverride is used instead of the database and
            collection arguments. It expects a pymongo.collection.Collection object, however, it is not type-checked
            (only hinted) to allow for more flexibility, including instances of
            [MontyDB](https://github.com/davidlatwe/MontyDB) Collection class or
            [Mongomock](https://github.com/mongomock/mongomock) Collection class. Defaults to None and has no effect
            in that case.

    '''

    def __init__(self,
                 doi: str = None,
                 name: str = None,
                 database: str = 'ULTERA_internal',
                 collection: str = 'CURATED_Dec2022',
                 collectionManualOverride: Collection = None,
                 credentialsFile: str = None):
        super().__init__(database=database, collection=collection, collectionManualOverride=collectionManualOverride, credentialsFile=credentialsFile)
        self.name = name
        self.doi = doi
        self.resetVariables()

        print(f'********  Analyzer Initialized  ********')

    def resetVariables(self) -> None:
        '''Resets all variables to their default values. This is useful when switching between different publications.
        without having to reinitialize the class and connect to the database again.'''
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

    def setDOI(self, doi: str) -> None:
        '''Sets the DOI of the publication to analyze. Resets all variables to their default values.'''
        self.doi = doi
        self.resetVariables()

    def setName(self, name: str) -> None:
        '''Sets the name of the researcher analysis is limited to.'''
        self.name = name

    def getCompVecs(self) -> List[List[float]]:
        '''Returns a list of composition vectors for all unique formulas in the publication. The composition vectors are
        normalized to sum to 1.0.

        Returns:
            List of composition vectors in order determined by the database read.
        '''
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
                    f"F: {e['material']['formula']}<br>PF: {e['material']['percentileFormula']}<br>Raw: {e['material']['rawFormula']}<br>RF: {e['material']['relationalFormula']}")
            if 'pointer' in e['reference']:
                self.pointers.add(e['reference']['pointer'])
        # Vectorize based on a list of elements
        self.els = list(self.els)
        for f in self.formulas:
            cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
            compVec = [cd[el] if el in cd else 0 for el in self.els]
            self.compVecs.append(compVec)
        return self.compVecs

    def analyze_nnDistances(self) -> None:
        '''Calculates the nearest neighbor distances for all unique composition vectors in the publication. The distances
        are calculated using the L1 metric and the k-d tree algorithm.'''
        self.getCompVecs()

        nn = NearestNeighbors(n_neighbors=2, metric='l1', algorithm='kd_tree')
        
        if len(self.compVecs) > 1:
            self.nn_distances = [l[1] for l in nn.fit(self.compVecs).kneighbors(self.compVecs)[0]]
        else:
            self.nn_distances = [0]

    def print_nnDistances(
            self, 
            minSamples: int = 2, 
            skipNearEquidistant: bool = False,
            nearEquidistantThreshold: float = 0.9,
            skipWellSeparated: bool = False,
            wellSeparatedThreshold: float = 0.01,
            printOut: bool = True,
            skipFailed: bool = False
        ) -> None:
        '''Prints the nearest neighbor distances for all unique composition vectors in the publication. The distances
        are calculated using the L1 metric and the k-d tree algorithm. The distances are normalized to the maximum
        distance in the publication. The output is persisted in the self.printLog variable.

        Args:
            minSamples: Minimum number of samples required to print the results. Defaults to 2.
            printOut: If True, the results are printed to the console. Defaults to True.
            skipFailed: If True, the method will pass silently over the DOIs that could not generate results, 
                e.g., due to insufficient data available. False by default.
            skipNearEquidistant: If True, the method will skip the DOIs where all distances are nearly the same and 
                likely do not need to be investigated for anomalies, as this presents one of neat expected outcomes.
                It judges the distances based on the nearEquidistantThreshold parameter. Defaults to False.
            nearEquidistantThreshold: Threshold for the near equidistant check. If all distances, normalized to the
                maximum distance, are higher than this threshold, the DOI is skipped. Defaults to 0.9.
            skipWellSeparated: If True, the method will skip the DOIs where all distances ensure good separation of
                compositions, i.e., it is unlikely that anomalies like near duplicates created by typo in the last 
                significant digit are present. It judges the composition separation based on the wellSeparatedThreshold
                parameter. Defaults to False.
            wellSeparatedThreshold: Threshold for the well-separated check. If all distances are higher than this
                threshold, the analysis of that DOI is skipped. Defaults to 0.01 or 1% of the maximum distance in the
                compositional space.

        '''
        assert len(self.compVecs) > 0
        assert len(self.nn_distances) > 0
        assert len(self.formulas) == len(self.nn_distances)
        if len(self.nn_distances) >= minSamples:
            if self.name is None or self.name in self.names:
                # Find the maximum distance to normalize the results
                maxD = max(self.nn_distances)
                # Check if all distances are nearly the same (>nearEquidistantThreshold normalized to max)
                if skipNearEquidistant and all([l / maxD > nearEquidistantThreshold for l in self.nn_distances]):
                    pass
                # Check if all distances separate the compositions well (distance is higher than wellSeparatedThreshold)
                elif skipWellSeparated and all([l > wellSeparatedThreshold for l in self.nn_distances]):
                    pass
                else:
                    self.printLog += f'\n--->  {self.doi}'
                    print(f'--->  {self.doi}')
                    # Align the formulas by the with across the 4 types
                    cols = [line.split("<br>") for line in self.fStrings]
                    widths = [max(len(col.strip()) for col in column) for column in zip(*cols)]
                    prettyFStrings = [' | '.join(col.strip().ljust(width) for col, width in zip(row, widths)) for row in cols]
                    for l, f in zip(self.nn_distances, prettyFStrings):
                        temp_line = f'{round(l, 4):<10}|  {round(l / maxD, 4):<10} <-- {f}'
                        self.printLog += temp_line + '\n'
                        if printOut:
                            print(temp_line)
                    self.printLog += '\n'
                    print('\n')
            elif not skipFailed:
                temp_message = f'Skipping {self.doi:<20}. Specified researcher ({self.name}) not present in the group ({self.names})\n'
                self.printLog += temp_message
                if printOut:
                    print(temp_message)
        elif not skipFailed:
            temp_message = f"Skipping {self.doi:<20} due to not enough composition data samples (minSamples={minSamples})."
            temp_message += f"Found only {len(self.nn_distances)} composition/s with {self.collection.count_documents({'reference.doi': self.doi})} datapoints.\n"
            self.printLog += temp_message
            if printOut:
                print(temp_message)

    def get_compVecs_2DPCA(self):
        '''Performs a 2D PCA on the composition vectors. The results are stored in the self.compVecs_2DPCA variable.
        The minimum range in both dimensions is stored in the self.compVecs_2DPCA_minRangeInDim variable.

        Returns:
            List of 2D PCA coordinates for all composition vectors.

        '''
        if self.compVecs is None or len(self.compVecs) == 0:
            self.getCompVecs()
        pca = PCA(n_components=2)
        self.compVecs_2DPCA = pca.fit_transform(self.compVecs)
        self.compVecs_2DPCA_minRangeInDim = min([
            max(self.compVecs_2DPCA[:, 0]) - min(self.compVecs_2DPCA[:, 0]),
            max(self.compVecs_2DPCA[:, 1]) - min(self.compVecs_2DPCA[:, 1])])

        return self.compVecs_2DPCA

    def analyze_compVecs_2DPCA(self, minDistance: float = 0.001, showFigure: bool = True) -> Union[str, BytesIO]:
        '''Performs a 2D PCA on the composition vectors. The results are stored in the self.compVecs_2DPCA variable.
        The minimum range in both dimensions is stored in the self.compVecs_2DPCA_minRangeInDim variable.
        The results are plotted using plotly. The figure is stored in the self.fig variable.

        Args:
            minDistance: Minimum distance between two points in the 2D PCA space in any dimension to be considered
                as non-linear. Defaults to 0.001.
            showFigure: If True, the figure is displayed. Defaults to True.

        Returns:
            String if specified researcher is not present in the group from the publication. String if a linear trend
            is detected. Figure in BytesIO format if name is matched and non-linear trends are detected.

        '''

        assert len(self.compVecs_2DPCA) > 0
        assert len(self.formulas) > 0
        assert len(self.fStrings) > 0
        if self.name is None or self.name in self.names:
            if self.compVecs_2DPCA_minRangeInDim > minDistance:
                fig = px.scatter(
                    x=self.compVecs_2DPCA[:, 0],
                    y=self.compVecs_2DPCA[:, 1],
                    color=self.formulas,
                    hover_name=self.fStrings,
                    color_discrete_sequence=px.colors.qualitative.Dark24,
                    width=900, height=400,
                    title=f'<b>{self.doi}</b>  --> {", ".join(self.pointers)}<br>parsed by {", ".join(self.names)}',
                    labels={'x': 'PCA1', 'y': 'PCA2', 'color': 'Alloy Reported (Parsed Formula)'},
                    template='plotly_white')
                fig.update_traces(
                    marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
                self.compVecs_2DPCA_plot = BytesIO(fig.to_image(format="png", scale=5))
                if showFigure:
                    fig.show()
                return self.compVecs_2DPCA_plot
            else:
                return f'Skipping {self.doi:<20} Nearly 1D linear trand detected.'
        else:
            return f'Skipping {self.doi:<20}. Specified researcher ({self.name}) not present in the group ({self.names})'

    def writePlot(self, workbookPath: str, skipLines: int) -> None:
        '''Writes the plot to the specified report Excel workbook.

        Args:
            workbookPath: Path to the report Excel workbook. Must be a .xlsx file and must not be open at the time of writing.
            skipLines: Number of lines to skip before writing the plot. It is critical to skip lines to avoid overwriting
                existing data in the workbook.
        '''
        assert isinstance(self.compVecs_2DPCA_plot, BytesIO)
        workbook = xlsxwriter.Workbook(workbookPath)
        worksheet = workbook.add_worksheet()
        cellIndex = f'A{1 + skipLines}'
        worksheet.insert_image(cellIndex, self.doi,
                               {'image_data': self.compVecs_2DPCA_plot, 'x_scale': 0.2, 'y_scale': 0.2})
        workbook.close()

    def writeManyPlots(self, toPlotList: list, workbookPath: str) -> None:
        '''Writes the plots to the specified report Excel workbook.

        Args:
            toPlotList: List of plots to write. Each element of the list can be either a BytesIO object containing the plot
                or a string containing the text to write if no plot is available because of a linear trend in the data or
                because the specified researcher is not present in the group reporting the data.
            workbookPath: Path to the report Excel workbook. Must be a .xlsx file and must not be open at the time of writing.
        '''

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
    '''Class to analyze a single composition in the context of abnormal data detection.

    Args:
        name: Name of the researcher to limit the search to. Defaults to None.
        database: Name of the database to use. Defaults to 'ULTERA_internal'.
        collection: Name of the collection to use. Defaults to 'CURATED_Dec2022'.
        collectionManualOverride: If specified, the collectionManualOverride is used instead of the database and
            collection arguments. It expects a pymongo.collection.Collection object, however, it is not type-checked
            (only hinted) to allow for more flexibility, including instances of
            [MontyDB](https://github.com/davidlatwe/MontyDB) Collection class or
            [Mongomock](https://github.com/mongomock/mongomock) Collection class. Defaults to None and has no effect
            in that case.
    '''

    def __init__(self,
                 name: str = None,
                 database: str = 'ULTERA_internal',
                 collection: str = 'CURATED_Dec2022',
                 collectionManualOverride: Collection = None,
                 credentialsFile: str = None):
        super().__init__(database=database, collection=collection, collectionManualOverride=collectionManualOverride, credentialsFile=credentialsFile)
        self.name = name
        self.formulas = set()
        self.printOuts = list()

    def scanCompositionsAround100(self,
                                  lowerBound: float = 80,
                                  uncertainty: float = 0.21,
                                  upperBound: float = 120,
                                  queryLimit: int = 10000,
                                  resultLimit: int = 1000,
                                  printOnFly: bool = False) -> None:
        '''Scans the database for compositions around 100% but not exactly 100% as defined by the lower and upper bounds.
        Results are stored in self.printOuts and can be printed out or written to a file using self.writeResultsToFile().

        Args:
            lowerBound: Lower bound for the sum of composition to be considered around 100%. Expressed as percentage.
                Defaults to 80 meaning 80%.
            upperBound: Upper bound for the sum of composition to be considered around 100%. Expressed as percentage.
                Defaults to 120 meaning 120%.
            uncertainty: Allowed deviation from 100% for the sum of composition. Expressed as percentage.
                Defaults to 0.21 meaning 0.21%.
            queryLimit: Maximum number of documents to query for from the database collection. If the limit is higher
                than the number of documents in the collection, all documents will be queried. Defaults to 10000.
            resultLimit: Maximum number of results to investigate across all runs of the function, i.e. if the
                SingleCompositionAnalyzer object calls this function multiple times, with resultLimits of 10, 20, and 30,
                the total number of results in self.printOuts will be 30. If you call it with the same resultLimit value,
                there will be no effect on the Analyzer object. Defaults to 1000.
            printOnFly: If True, prints the results out into console on the fly as they are found. Defaults to False.
        '''

        query = {'reference.doi': {'$ne': None}}
        if self.name is not None:
            query.update({'meta.name': self.name})
        for e in self.collection.find(query, limit=queryLimit):
            if len(self.printOuts) >= resultLimit:
                break

            f = e['material']['formula']
            if f not in self.formulas:
                self.formulas.add(f)
                c = Composition(f)
                fracs = list(c.get_el_amt_dict().values())
                fracsSum = round(sum(fracs), 3)

                def printAlloy(self):
                    '''Prints the alloy to the console while retaining the information in self.printOuts list'''
                    printOut = f"DOI: {e['reference']['doi']}"
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

                if fracsSum > lowerBound and fracsSum < (100 - uncertainty):
                    printAlloy(self)
                elif fracsSum > lowerBound / 100 and fracsSum < (100 - uncertainty) / 100:
                    printAlloy(self)
                elif fracsSum < upperBound and fracsSum > (100 + uncertainty):
                    printAlloy(self)
                elif fracsSum < upperBound / 100 and fracsSum > (100 + uncertainty) / 100:
                    printAlloy(self)

    def writeResultsToFile(self, fileName: str) -> None:
        '''Writes the results to a file. The file is created if it does not exist, otherwise it is overwritten.

        Args:
            fileName: Name of the file to write the results to.
        '''
        assert len(self.printOuts) > 0
        with open(fileName, 'w+') as f:
            f.write(datetime.now().strftime("%c"))
            f.write('\n')
            for printOut in self.printOuts:
                f.write(printOut)
                f.write('\n')


class AllDataAnalyzer(Analyzer):
    '''Class to analyze datapoints in the scope of the contents of entire database. It primarily relies on clustering
    analysis to identify outliers and anomalies in a few different ways.

    Args:
        database: Name of the database to use. Defaults to 'ULTERA_internal'.
        collection: Name of the collection to use. Defaults to 'CURATED_Dec2022'.
        name: Name of the researcher to limit the search to. Defaults to None.
        collectionManualOverride: If specified, the collectionManualOverride is used instead of the database and
            collection arguments. It expects a pymongo.collection.Collection object, however, it is not type-checked
            (only hinted) to allow for more flexibility, including instances of
            [MontyDB](https://github.com/davidlatwe/MontyDB) Collection class or
            [Mongomock](https://github.com/mongomock/mongomock) Collection class. Defaults to None and has no effect
            in that case.

    Properties:
        allComps: List of all unique compositions in the database. It is automatically updated when the class is
            initialized.
        els: Set of all unique elements in the database. It is automatically updated when the class is initialized and
            it is used to determine common ordering of elements across methods.
        outliers: List of outliers in the database identified by the last used method (e.g. DBSCAN).
    '''

    def __init__(self,
                 database: str = 'ULTERA_internal',
                 collection: str = 'CURATED_Dec2022',
                 name: str = None,
                 collectionManualOverride: Collection = None,
                 credentialsFile: str = None):
        super().__init__(database=database, collection=collection, collectionManualOverride=collectionManualOverride, credentialsFile=credentialsFile)
        self.name = name
        self.outliers = list()
        self.els = set()

        self.allComps = self.updateAllComps(printOut=False, printOutMinimal=True)

    def updateAllComps(self, printOut: bool = False, printOutMinimal: bool = True) -> list:
        '''Identifies a list of all unique compositions in the database, updates the self.els property, and then converts
        the list of compositions into a list of dictionaries with the formula and a vector representation of the composition
        in the order of self.els. The vector representation is used for full-dimensional clustering analysis. Some other methods
        like TSNE embedding will update these dictionaries with additional keys.

        Args:
            printOut: If True, prints out the list of all unique compositions. Defaults to False.
            printOutMinimal: If True, prints out the number of unique compositions and the list of unique elements. Defaults
                to True.

        Returns:
            List of dictionaries with the formula and a vector representation of the composition in the order of self.els.
        '''

        print('Updating the list of all unique composition points...')
        formulas = set()
        for e in self.collection.find({
            'material.nComponents': {'$gte': 3},
            'reference.doi': {'$ne': None}}):
            rf = e['material']['relationalFormula']
            c = Composition(rf)
            formulas.add(rf)
            self.els.update(list(c.get_el_amt_dict().keys()))

        print(f'Number of unique formulas found: {len(formulas)}')
        comps = list()

        for f in formulas:
            cd = dict(Composition(f).fractional_composition.get_el_amt_dict())
            compVec = [cd[el] if el in cd else 0.0 for el in self.els]
            comps.append({
                'formula': f,
                'compVec': compVec
            })

        if printOutMinimal:
            print(f'Elements Found: {self.els}')
        if printOut:
            print(f'Formulas Found:\n{formulas}')

        self.allComps = comps
        print('Done!')

        return comps

    def getTSNE(self, perplexity: int = 2, init: str = 'pca') -> np.ndarray:
        '''Performs TSNE embedding on the list of compositions in self.allComps. The TSNE embedding is stored in the
        'compVec_TSNE2D' key of each dictionary in self.allComps. The TSNE embedding is also returned as a numpy array.

        Args:
            perplexity: Perplexity parameter for the TSNE embedding. Defaults to 2. This is the parameter that controls
                the number of alloys that are expected to be close to each other in the embedding. The value of 2 is
                chosen for visualizing outlier detection because the database is very sparse, populated by chains of
                neighboring alloys, and we do expect many without more than one neighbor. For more general use, the
                default value of 5-10 is recommended. The value of 30, often used in the literature, is not recommended
                for HEA datasets.
            init: Initialization method for the TSNE embedding. Defaults to 'pca'. The default value is recommended.

        Returns:
            Numpy array of the TSNE embedding.
        '''

        tsne = TSNE(n_components=2, perplexity=perplexity, init=init)
        X = np.array([c['compVec'] for c in self.allComps])
        X_embedded = tsne.fit_transform(X)

        for i, c in enumerate(self.allComps):
            c['compVec_TSNE2D'] = X_embedded[i]

        return X_embedded

    def showTSNE(self):
        '''Plots the TSNE embedding of the compositions in self.allComps. The plot is interactive and allows for
        hovering over the points to see the formula of the alloy.

        Returns:
            None
        '''
        assert len(self.allComps) > 0
        assert 'formula' in self.allComps[0]
        assert 'compVec_TSNE2D' in self.allComps[0]
        assert len(self.allComps[0]['compVec_TSNE2D']) == 2

        fig = px.scatter(x=[c['compVec_TSNE2D'][0] for c in self.allComps],
                         y=[c['compVec_TSNE2D'][1] for c in self.allComps],
                         hover_name=[c['formula'] for c in self.allComps],
                         color_discrete_sequence=px.colors.qualitative.Dark24,
                         labels={'x': f'{len(self.els)}D->2D TSNE1',
                                 'y': f'{len(self.els)}D->2D TSNE2',
                                 'color': f'Embedded Points'},
                         template='plotly_white'
                         )
        fig.show()

    def getDBSCAN(self, eps: float = 0.3, min_samples: int = 2, p: int = 1) -> Tuple[np.ndarray, int]:
        '''Performs DBSCAN clustering on the list of compositions in self.allComps. The DBSCAN clustering is stored in the
        'dbscanCluster' key of each dictionary in self.allComps. The DBSCAN clustering is also returned as a numpy array
        along with the number of outliers identified.

        Args:
            eps: Epsilon parameter for the DBSCAN clustering. Defaults to 0.3. This is the parameter that controls the
                maximum distance between two points to be considered neighbors. With all other parameters at their
                default values, this 0.3 value corresponds to a 30% atomic fraction difference by summing over differences
                in all elements fractions. For example, for Fe0.5Ni0.5, up to Fe0.35Ni0.65 or Fe0.65Ni0.35 would be
                considered neighbors.
            min_samples: Minimum number of samples parameter for the DBSCAN clustering. Defaults to 2. This is the
                parameter that controls the minimum number of neighbors required for a point to be considered a core
                point. If it is not met, the point is considered an outlier and assigned to the -1 cluster.
            p: p parameter for the DBSCAN clustering. Defaults to 1. This is the parameter that controls the metric used
                to calculate the distance between two points. The default value of 1 corresponds to the Manhattan distance
                with consequences described above for eps. The value of 2 would correspond to the Euclidean distance.

        Returns:
            Numpy array of the DBSCAN clustering and the number of outliers identified.
        '''

        assert len(self.allComps) > 0
        assert 'compVec' in self.allComps[0]

        dbscan = DBSCAN(eps=eps, min_samples=min_samples, p=p)
        X = np.array([c['compVec'] for c in self.allComps])
        dbscanClusters = dbscan.fit_predict(X)

        outlierN = 0
        for i, c in enumerate(self.allComps):
            c['dbscanCluster'] = dbscanClusters[i]
            if dbscanClusters[i] == -1:
                outlierN += 1

        print(f'Found {len(set(dbscanClusters))} clusters and {outlierN} outliers.')
        print(f'Outlier ratio: {round(outlierN / len(dbscanClusters) * 100, 1)}%')

        return dbscanClusters, outlierN

    def getDBSCANautoEpsilon(self, outlierTargetN: int = 10) -> Tuple[np.ndarray, int]:
        '''Performs DBSCAN clustering using getDBSCAN() with a range of epsilon values until the desired minimum number
        of outliers is found. It efficiently allows user to find as many outliers as they can investigate independently
        of the number of alloys in the dataset. The DBSCAN clustering is stored in the 'dbscanCluster' key of each dictionary in
        self.allComps. The DBSCAN clustering is also returned as a numpy array along with the number of outliers
        identified.

        Args:
            outlierTargetN: Minimum number of outliers to be identified. Defaults to 10.

        Returns:
            Numpy array of the DBSCAN clustering and the number of outliers identified.
        '''
        assert len(self.allComps) > outlierTargetN
        outlierN = 0
        eps = 1.00001
        assert outlierTargetN > 0
        assert outlierN < outlierTargetN
        while outlierN < outlierTargetN:
            print(f'Running DBSCAN with eps={round(eps, 3)}...')
            dbscanClusters, outlierN = self.getDBSCAN(eps=eps)
            eps -= 0.025

        return dbscanClusters, outlierN

    def showClustersDBSCAN(self):
        '''Plots the TSNE embedding of the compositions in self.allComps colored by the DBSCAN clustering. The plot is
        interactive and allows for hovering over the points to see the formula of the alloy as well as the DBSCAN
        cluster number.

        Returns:
            None
        '''
        assert len(self.allComps) > 0
        assert 'formula' in self.allComps[0]
        assert 'dbscanCluster' in self.allComps[0]
        assert 'compVec_TSNE2D' in self.allComps[0]
        assert len(self.allComps[0]['compVec_TSNE2D']) == 2

        fig = px.scatter(x=[c['compVec_TSNE2D'][0] for c in self.allComps],
                         y=[c['compVec_TSNE2D'][1] for c in self.allComps],
                         color=[str(c['dbscanCluster']) for c in self.allComps],
                         hover_name=[c['formula'] for c in self.allComps],
                         color_discrete_sequence=px.colors.qualitative.Dark24,
                         labels={'x': f'{len(self.els)}D->2D TSNE1',
                                 'y': f'{len(self.els)}D->2D TSNE2',
                                 'color': 'Cluster #'},
                         template='plotly_white'
                         )
        fig.show()

    def updateOutliersList(self) -> None:
        '''Updates the list of outliers in self.outliers. This list is used by the showOutliersDBSCAN() method.

        Returns:
            None
        '''
        assert len(self.allComps) > 0
        assert 'formula' in self.allComps[0]
        assert 'dbscanCluster' in self.allComps[0]

        self.outliers = [c for c in self.allComps if c['dbscanCluster'] == -1]

    def showOutliersDBSCAN(self) -> None:
        '''Plots the TSNE embedding of the compositions in self.allComps colored by the DBSCAN clustering. The plot is
        interactive and allows for hovering over the points to see the formula of the alloy as well as the DBSCAN
        cluster number. Outliers are colored in red.

        Returns:
            None
        '''
        assert len(self.allComps) > 0
        assert 'formula' in self.allComps[0]
        assert 'dbscanCluster' in self.allComps[0]
        assert 'compVec_TSNE2D' in self.allComps[0]
        assert len(self.allComps[0]['compVec_TSNE2D']) == 2

        fig = px.scatter(x=[c['compVec_TSNE2D'][0] for c in self.allComps],
                         y=[c['compVec_TSNE2D'][1] for c in self.allComps],
                         color=['outlier' if c['dbscanCluster'] == -1 else 'clustered' for c in self.allComps],
                         hover_name=[c['formula'] for c in self.allComps],
                         color_discrete_sequence=px.colors.qualitative.Dark24,
                         labels={'x': f'{len(self.els)}D->2D TSNE1',
                                 'y': f'{len(self.els)}D->2D TSNE2',
                                 'color': 'Classification'},
                         template='plotly_white'
                         )
        fig.show()

    def findOutlierDataSources(self, filterByName: bool = False) -> list:
        '''Finds the data sources for the outliers identified by DBSCAN. If filterByName is True, only data sources
        with the same name as the current analyzer name setting will be printed. Otherwise, all data sources will be
        printed.

        Args:
            filterByName: If True, only data sources with the same name as the current analyzer name setting will be printed.
                Defaults to False.

        Returns:
            List of dictionaries containing the data sources for the outliers.
        '''
        assert len(self.outliers) > 0
        assert 'formula' in self.outliers[0]

        outlierSources = list()

        def printEntry(entry):
            out = f'Outlier {outlier["formula"]:<25} | {entry["material"]["percentileFormula"]:<25} | {entry["material"]["rawFormula"]}\n'
            out += f'matched to:  {entry["meta"]["name"]:<20} upload '
            if 'doi' in entry['reference']:
                out += f'from DOI {entry["reference"]["doi"]}'
            if 'pointer' in entry['reference']:
                out += f' at position {entry["reference"]["pointer"]}'
            print(out, '\n')

        for outlier in self.outliers:
            e = self.collection.find_one({'material.relationalFormula': outlier['formula']})
            if e['meta']['name'] == self.name:
                outlierSources.append(e)
                printEntry(e)
            elif not filterByName:
                outlierSources.append(e)
                printEntry(e)
            else:
                print(f'Outlier {outlier["formula"]} not matched to a data source from {self.name}. Check '
                      'the name or set filterByName to False to see all matches.\n')

        if self.name is not None:
            print(f'Found {len(outlierSources)} outlier data sources from {self.name}.')
        else:
            print(f'Found {len(outlierSources)} outlier data sources from all uploaded data.')

        return outlierSources
