import unittest

from ulteratools.data_analyzer import curation

class TestADA(unittest.TestCase):

    def setUp(self) -> None:
        self.ADA = curation.AbnormalDataAnalyzer()
        pass

    def test_DOIAggregation(self):
        doiList = self.ADA.get_allDOIs()
        print(f'{len(doiList)} DOIs detected in the database')
        self.assertGreater(len(doiList), 0)

    def test_NNdistance(self):
        doi = '10.3390/met9010076'
        self.ADA.analyze_nnDistances(doi)

if __name__ == '__main__':
    unittest.main()
