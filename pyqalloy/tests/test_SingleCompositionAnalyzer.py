import unittest

from pyqalloy.data_analyzer import curation

class TestSCADA(unittest.TestCase):

    def setUp(self) -> None:
        self.sC = curation.SingleCompositionAnalyzer()
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
