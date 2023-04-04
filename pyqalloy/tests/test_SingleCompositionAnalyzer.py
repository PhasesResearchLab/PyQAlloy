import unittest

from pyqalloy.curation import analysis


class TestSCADA(unittest.TestCase):
    '''Test the SingleCompositionAnalyzer class in the curation module by (1) obtaining the data from ULTERA Database,
    (2) performing a scan of the compositions around 100, but not exceeding 100, and (3) partially verifying results.
    '''

    def setUp(self) -> None:
        self.sC = analysis.SingleCompositionAnalyzer()
        pass

    def test_Scan1(self):
        self.sC.scanCompositionsAround100(queryLimit=10, printOnFly=True)
        self.sC.scanCompositionsAround100(queryLimit=100, printOnFly=False)

    def test_Scan2(self):
        with self.subTest(msg='Scan'):
            self.sC.scanCompositionsAround100(resultLimit=10, printOnFly=True)
            self.sC.scanCompositionsAround100(resultLimit=30, printOnFly=False)

        with self.subTest(msg='Write Results'):
            self.sC.writeResultsToFile('testResults.txt')
