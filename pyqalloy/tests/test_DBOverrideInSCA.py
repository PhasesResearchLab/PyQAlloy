import unittest
from pyqalloy.curation import analysis
from montydb import MontyClient
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


class TestSCADA(unittest.TestCase):
    '''Test the SingleCompositionAnalyzer class in the curation module by (1) obtaining the data from ULTERA Database,
    (2) performing a scan of the compositions around 100, but not exceeding 100, and (3) partially verifying results.
    '''

    def setUp(self) -> None:
        self.customCollection = MontyClient(":memory:").db.test
        with open('dev/ULTERA_sample.bson', 'rb+') as f:
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
        self.customCollection.drop()
        pass