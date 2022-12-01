import unittest

from ulteratools.data_analyzer import curation

class TestADA(unittest.TestCase):

    def setUp(self) -> None:
        doi = '10.3390/met9010076'
        self.sDOI = curation.SingleDOIAnalyzer(doi=doi)
        pass

    def test_DOIAggregation(self):
        doiList = self.sDOI.get_allDOIs()
        print(f'{len(doiList)} DOIs detected in the database')
        self.assertGreater(len(doiList), 0)

    def test_NNdistance(self):
        with self.subTest(msg='Find Distances'):
            self.sDOI.analyze_nnDistances()

        with self.subTest(msg='Test Printout'):
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection. - filled'):
            self.sDOI.setName('Marcia Ahn')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection. - empty'):
            self.sDOI.setName('39fd48rym7sfg48g23f')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection - revert to all names'):
            self.sDOI.setName(None)


if __name__ == '__main__':
    unittest.main()
