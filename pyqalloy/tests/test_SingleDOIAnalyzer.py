import unittest

from pyqalloy.curation import analysis

referenceDOIs = ['10.1557/adv.2017.76', '10.1557/jmr.2019.18', '10.1557/jmr.2019.36', '10.1557/jmr.2019.40', 
                 '10.3390/coatings9010016', '10.3390/e16020870', '10.3390/e18050189', '10.3390/e21010015', 
                 '10.3390/e21020114', '10.3390/e21020122', '10.3390/e21020169', '10.3390/e21030288']

nnDistancesRef = [0.08658008658008651, 0.0909090909090909, 0.08225108225108217, 0.09090909090909093, 0.08225108225108217]

class TestADA(unittest.TestCase):

    def setUp(self) -> None:
        doi = '10.1016/j.jallcom.2008.11.059'
        self.sDOI = analysis.SingleDOIAnalyzer(
            doi=doi
            )
        pass

    def test_DOIAggregation(self):
        doiList = self.sDOI.get_allDOIs()
        print(f'{len(doiList)} DOIs detected in the database')
        self.assertGreater(len(doiList), 0, msg='No DOIs detected in the database')

        for doi in referenceDOIs:
            with self.subTest(msg=f'Test {doi}'):
                self.assertIn(doi, doiList, msg=f'Known DOI {doi} not found in the list of DOIs')

        self.assertEqual(
            len(doiList), 479, 
            msg='Incorrect number of DOIs found. Make sure you are using CURATED_Dec2022 snapshot or adjust the reference number of DOIs.')


    def test_NNdistance(self):
        with self.subTest(msg='Find Distances'):
            self.sDOI.analyze_nnDistances()

            for i, dist in enumerate(nnDistancesRef):
                with self.subTest(msg=f'Test {i}'):
                    self.assertAlmostEqual(dist, self.sDOI.nn_distances[i], places=5, msg=f'Incorrect distance found for {i}th nearest neighbor (in the reference: {self.sDOI.doi})')

        with self.subTest(msg='Test Printout'):
            self.sDOI.print_nnDistances(printOut=False)

            self.assertIn('10.1016/j.jallcom.2008.11.059', self.sDOI.printLog, msg='Printout does not contain the DOI')
            self.assertIn('Adam Krajewski', self.sDOI.printLog, msg='Printout does not contain the name')
            self.assertIn(
                '0.0866    |  0.9524     <-- F: Ti0.5 Cr1 Fe1 Co1 Ni1 Cu0.5 Al0.5   | PF: Ti9.1 Cr18.2 Fe18.2 Co18.2 Ni18.2 Cu9.1 Al9.1  | Raw: Al0.5CoCrCu0.5FeNiTi0.5   | RF: Ti1 Cr2 Fe2 Co2 Ni2 Cu1 Al1', 
                self.sDOI.printLog,
                msg='Printout does not contain a reference result string. Was any printout style changed?'
                )

        with self.subTest(msg='Test Name Selection. - filled'):
            self.sDOI.setName('Adam Krajewski')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()

            doiList = self.sDOI.get_allDOIs()
            self.assertEqual(len(doiList), 276, msg='Incorrect number of DOIs found for Adam Krajewski. Make sure you are using CURATED_Dec2022 snapshot or adjust the reference number of DOIs.')


        with self.subTest(msg='Test Name Selection. - empty'):
            self.sDOI.setName('39fd48rym7sfg48g23f')
            self.sDOI.analyze_nnDistances()
            self.sDOI.print_nnDistances()
            doiList = self.sDOI.get_allDOIs()
            self.assertEqual(len(doiList), 0, msg='Incorrect number of DOIs found for unexisting name (should be 0)')

        with self.subTest(msg='Test Name Selection - revert to all names'):
            self.sDOI.setName(None)
            log0 = self.sDOI.printLog
            self.sDOI.print_nnDistances(printOut=False)
            self.assertGreater(len(self.sDOI.printLog), len(log0), msg='Printout length did not increase after reverting to all names which should cover the case again and generate more printout')

        with self.subTest(msg='Print Selection - min samples'):
            self.sDOI.print_nnDistances(minSamples=32)

    def test_PCA(self):
        with self.subTest(msg='Get PCA'):
            self.sDOI.getCompVecs()
            self.sDOI.get_compVecs_2DPCA()

            self.assertGreater(len(self.sDOI.compVecs), 0, msg='PCA data not generated')
            self.assertEqual(len(self.sDOI.compVecs_2DPCA[0]), 2, msg='Incorrect dimensionality of the PCA result')
            self.assertEqual(len(self.sDOI.compVecs_2DPCA), 5, msg='Incorrect number of entries in the PCA result')

        with self.subTest(msg='Analyze the Found PCA'):
            self.sDOI.analyze_compVecs_2DPCA(showFigure=False)
            self.assertIsNotNone(self.sDOI.compVecs_2DPCA_plot)

        with self.subTest(msg='Write Plots - wrong name test'):
            self.sDOI.setName('Researcher 934ocfhxm834xfb')
            self.sDOI.analyze_compVecs_2DPCA(
                showFigure=False,
                skipFailed=False,
            )
            self.assertIn('not present in the group', self.sDOI.printLog)
            self.sDOI.setName(None)

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
                        self.sDOI.writePlot(workbookPath='testResultPCA_single.xlsx', skipLines=0)
                    else:
                        toPrintList.append(f'Skipping {doi:<30} Nearly 1D linear trand detected.')
                else:
                    toPrintList.append(f'Skipping {doi:<30} Not enough data for PCA (N>=2).')

            self.sDOI.writeManyPlots(toPlotList=toPrintList, workbookPath='testResultPCA_many.xlsx')

    def tearDown(self) -> None:
        self.sDOI.ultera_client.close()
        del self.sDOI
        pass

if __name__ == '__main__':
    unittest.main()
