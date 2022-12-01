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
            temp_sDOI = curation.SingleDOIAnalyzer(name='Marcia Ahn', doi='10.3390/met9010076')
            temp_sDOI.analyze_nnDistances()
            temp_sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection. - empty'):
            temp_sDOI = curation.SingleDOIAnalyzer(name='wnjvbwejhcv', doi='10.3390/met9010076')
            temp_sDOI.analyze_nnDistances()
            temp_sDOI.print_nnDistances()


if __name__ == '__main__':
    unittest.main()
