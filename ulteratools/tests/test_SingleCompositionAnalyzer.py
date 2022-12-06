import unittest

from ulteratools.data_analyzer import curation

class TestSCADA(unittest.TestCase):

    def setUp(self) -> None:
        self.sC = curation.SingleCompositionAnalyzer()
        pass

    def test_Scan1(self):
        self.sC.scanCompositionsAround100(queryLimit=10, printOnFly=True)

    def test_Scan2(self):
        self.sC.scanCompositionsAround100(resultLimit=10, printOnFly=True)
