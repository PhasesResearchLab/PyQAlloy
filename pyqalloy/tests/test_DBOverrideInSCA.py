import unittest
from pyqalloy.curation import analysis
from montydb import MontyClient
from montydb.types.bson import init as init_bson
import bson

referenceResultPrintOuts = [
    'DOI: 10.1016/j.actamat.2016.06.063\nF:   Mo7 Cr23 Fe23 Co23 Ni23\n'
    'PF:  Mo7.1 Cr23.2 Fe23.2 Co23.2 Ni23.2\nRaw:  Co23Cr23Fe23Ni23Mo7\n'
    'RF:  Mo1 Cr3.29 Fe3.29 Co3.29 Ni3.29\n[7.0, 23.0, 23.0, 23.0, 23.0]\n'
    '-->  99.0\n',
    'DOI: 10.1016/j.actamat.2016.11.016\nF:   Cr16 Fe16 Co16 Ni34.4 Al16\n'
    'PF:  Cr16.3 Fe16.3 Co16.3 Ni35 Al16.3\nRaw:  Al16Co16Cr16Fe16Ni34.4\n'
    'RF:  Cr1 Fe1 Co1 Ni2.15 Al1\n[16.0, 16.0, 16.0, 34.4, 16.0]\n'
    '-->  98.4\n',
    'DOI: 10.1016/j.msea.2017.04.111\nF:   Cr19 Fe19 Co19 Ni37 Cu4 Al4\n'
    'PF:  Cr18.6 Fe18.6 Co18.6 Ni36.3 Cu3.9 Al3.9\nRaw:  Al4Co19Cr19Cu4Fe19Ni37\n'
    'RF:  Cr4.75 Fe4.75 Co4.75 Ni9.25 Cu1 Al1\n[19.0, 19.0, 19.0, 37.0, 4.0, 4.0]\n'
    '-->  102.0\n',
    'DOI: 10.1016/j.matlet.2017.04.072\nF:   Cr23 Fe23 Co23 Ni23 Al7\n'
    'PF:  Cr23.2 Fe23.2 Co23.2 Ni23.2 Al7.1\nRaw:  Al7Co23Cr23Fe23Ni23\n'
    'RF:  Cr3.29 Fe3.29 Co3.29 Ni3.29 Al1\n[23.0, 23.0, 23.0, 23.0, 7.0]\n'
    '-->  99.0\n']

referencePrintoutDOI = [
    "--->  10.1016/j.actamat.2016.06.063",
    "0.1006    |  1.0        <-- F: Mo1 Cr12 Fe12 Co12 Ni12 | PF: Mo2 Cr24.5 Fe24.5 Co24.5 Ni24.5   | Raw: Co24Cr24Fe24Ni24Mo2 | RF: Mo1 Cr12 Fe12 Co12 Ni12",
    "0.1006    |  1.0        <-- F: Mo7 Cr23 Fe23 Co23 Ni23 | PF: Mo7.1 Cr23.2 Fe23.2 Co23.2 Ni23.2 | Raw: Co23Cr23Fe23Ni23Mo7 | RF: Mo1 Cr3.29 Fe3.29 Co3.29 Ni3.29"
]

class TestSCADA(unittest.TestCase):
    '''Test the SingleCompositionAnalyzer class in the curation module with the custom collection of ULTERA samples.
    '''

    def setUp(self) -> None:
        init_bson(use_bson=True)
        self.customCollection = MontyClient(":memory:").db.test
        with open('examples/ULTERA_sample.bson', 'rb+') as f:
            self.customCollection.insert_many(bson.decode_all(f.read()))
        self.sC = analysis.SingleCompositionAnalyzer(collectionManualOverride=self.customCollection)
    def test_CustomDBScanResult(self):
        # Length
        with self.subTest(msg='Test Custom Collection Length'):
            self.assertEqual(
                self.sC.collection.count_documents({}),
                300,
                msg='Collection of correct length not passed to the SingleCompositionAnalyzer'
            )

        with self.subTest(msg='Test Custom Collection ID Present (not modified upon insertion)'):
            result = self.sC.collection.find_one({'_id': bson.ObjectId('635997c429377cf4308b62b0')})
            self.assertIsNotNone(result, msg='Custom collection does not contain the expected ID')

        with self.subTest(msg='Test Correct DOI is attached'):
            # DOI
            self.assertEqual(
                result['reference']['doi'],
                '10.1016/j.actamat.2021.116800',
                msg='Custom collection does not contain the expected DOI associated with the ID')

        with self.subTest(msg='Test Correct Relational Formula is attached'):
            # Relational Formula
            self.assertEqual(
                result['material']['relationalFormula'],
                'Ti1 Ta1.33 Nb1.33 W1.33 Mo1.33',
                msg='Custom collection does not contain the expected relational formula associated with the ID'
            )

        with self.subTest(msg='Test Scan Runtime'):
            self.sC.scanCompositionsAround100(resultLimit=10, printOnFly=True, uncertainty=0.5)

        with self.subTest(msg='Test result length'):
            resLen = len(self.sC.printOuts)
            self.assertGreater(resLen, 0, msg='No results found')
            self.assertEqual(resLen, 4, msg='Found incorrect number of results. Expected exactly 4.')

        with self.subTest(msg='Test printout correctness against reference'):
            self.assertListEqual(self.sC.printOuts, referenceResultPrintOuts,
                                 msg='Printout does not match the reference')

    def tearDown(self) -> None:
        del self.sC
        self.customCollection.drop()
        pass

class TestSDOIADA(unittest.TestCase):
    '''Test the SingleDOIAnalyzer class in the curation module with the custom collection of ULTERA samples.
    '''

    def setUp(self) -> None:
        init_bson(use_bson=True)
        self.customCollection = MontyClient(":memory:").db.test
        with open('examples/ULTERA_sample.bson', 'rb+') as f:
            self.customCollection.insert_many(bson.decode_all(f.read()))
        self.sD = analysis.SingleDOIAnalyzer(collectionManualOverride=self.customCollection)

    def test_gettingDOIs(self):
        doiList = self.sD.get_allDOIs()

        for doi in ['10.1016/j.actamat.2016.06.063', '10.1016/j.actamat.2016.11.016', '10.1016/j.msea.2017.04.111', '10.1016/j.matlet.2017.04.072']:
            with self.subTest(msg=f'Test {doi}'):
                self.assertIn(doi, doiList, msg=f'DOI {doi} not found in the list of DOIs')

        with self.subTest(msg='Test length of DOIs'):
            self.assertEqual(len(doiList), 157, msg='Incorrect number of DOIs found')

    def test_gettingAllDOIsWithNameSet(self):

        with self.subTest(msg='Name set to Adam Krajewski'):
            oldDOIList = self.sD.get_allDOIs()
            self.sD.setName('Adam Krajewski')
            doiList = self.sD.get_allDOIs()
            self.assertEqual(len(doiList), 107, msg='Incorrect number of DOIs found for Adam Krajewski')
            self.assertLessEqual(len(doiList), len(oldDOIList), msg='Number of DOIs found for Adam Krajewski is greater than the number of DOIs found without a name set')

        with self.subTest(msg='Crazy name set so no DOIs should be found'):
            self.sD.setName('Crazy Scientist')
            doiList = self.sD.get_allDOIs()
            self.assertEqual(len(doiList), 0, msg='Incorrect number of DOIs found for Crazy Scientist (should be 0)')

    def test_NNAnalysisDOI(self):
        self.sD.setDOI('10.1016/j.actamat.2016.06.063')
        self.sD.analyze_nnDistances()
        self.sD.print_nnDistances(printOut=False)

        for i, line in enumerate(referencePrintoutDOI):
            with self.subTest(msg=f'Test {i}th line'):
                self.assertIn(line, self.sD.printLog, msg=f'Expected printout line {i} not in the reference')
        

    def tearDown(self):
        del self.sD
        self.customCollection.drop()
        pass

if __name__ == '__main__':
    unittest.main()