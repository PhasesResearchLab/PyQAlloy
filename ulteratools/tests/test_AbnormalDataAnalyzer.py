import unittest

from ulteratools.data_analyzer import curation

class TestADA(unittest.TestCase):

    def setUp(self) -> None:
        doi = '10.1016/j.jallcom.2008.11.059'
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
            self.sDOI.setName('Adam Krajewski')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection. - empty'):
            self.sDOI.setName('39fd48rym7sfg48g23f')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Test Name Selection - revert to all names'):
            self.sDOI.setName(None)
            self.sDOI.print_nnDistances()

        with self.subTest(msg='Print Selection - min samples'):
            self.sDOI.print_nnDistances(minSamples=32)

    def test_PCA(self):
        with self.subTest(msg='Get PCA'):
            self.sDOI.getCompVecs()
            self.sDOI.get_compVecs_2DPCA()

        with self.subTest(msg='Analyze the Found PCA'):
            self.sDOI.analyze_compVecs_2DPCA(showFigure=False)

        with self.subTest(msg='Write Plots'):
            toPrintList = list()
            for doi in ['10.1016/j.jallcom.2008.11.059', '10.3390/met9010076', '10.1016/j.scriptamat.2018.10.023', '10.1007/978-1-4684-6066-7', '10.3390/e18050189']:
                self.sDOI.setDOI(doi)
                self.sDOI.getCompVecs()
                if len(self.sDOI.compVecs)>1:
                    self.sDOI.get_compVecs_2DPCA()
                    self.sDOI.analyze_compVecs_2DPCA(showFigure=False)
                    if self.sDOI.compVecs_2DPCA_plot is not None:
                        toPrintList.append(self.sDOI.compVecs_2DPCA_plot)
                    else:
                        toPrintList.append(f'Skipping {doi:<30} Nearly 1D linear trand detected.')
                else:
                    toPrintList.append(f'Skipping {doi:<30} Not enough data for PCA (N>=2).')
            self.sDOI.writeManyPlots(toPlotList=toPrintList, workbookPath='testResultPCA.xlsx')

if __name__ == '__main__':
    unittest.main()
