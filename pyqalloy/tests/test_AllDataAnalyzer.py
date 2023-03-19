import unittest

from pyqalloy.data_analyzer import curation

class TestAllDataContextULTERA(unittest.TestCase):

    def setUp(self) -> None:
        self.allD = curation.AllDataAnalyzer()

    def testInit(self) -> None:
        self.assertGreater(len(self.allD.allComps), 0)
        self.assertIn('formula', self.allD.allComps[0])
        self.assertIn('compVec', self.allD.allComps[0])

    def testTSNE(self) -> None:
        with self.subTest(msg='Find TSNE Embedding under large perplexity'):
            self.allD.getTSNE(perplexity=30)

            self.assertIn('compVec_TSNE2D', self.allD.allComps[0])
            self.assertEqual(len(self.allD.allComps[0]['compVec_TSNE2D']), 2)

        with self.subTest(msg='Find TSNE Embedding under low (stnadard) perplexity'):
            self.allD.getTSNE()

            self.assertIn('compVec_TSNE2D', self.allD.allComps[0])
            self.assertEqual(len(self.allD.allComps[0]['compVec_TSNE2D']), 2)

        with self.subTest(msg='Test if the TSNE embedding successfully prints out'):
            self.allD.showTSNE()

    def testDBSCAN(self) -> None:

        with self.subTest(msg='DBSCAN default'):
            _, outlierN1 = self.allD.getDBSCAN(eps=0.05)

            self.assertIn('dbscanCluster', self.allD.allComps[0])

        with self.subTest(msg='DBSCAN epsilon effect'):
            _, outlierN2 = self.allD.getDBSCAN(eps=0.05)
            _, outlierN3 = self.allD.getDBSCAN(eps=0.5)

            self.assertGreater(outlierN2, outlierN3)

        with self.subTest(msg='Automatic epsilon adjustment to find at least 5 outliers'):
            _, outlierN4 = self.allD.getDBSCANautoEpsilon(outlierTargetN=5)

            self.assertGreater(outlierN4, 5)

        with self.subTest(msg='Update a list of outliers'):
            self.allD.updateOutliersList()

            self.assertGreater(len(self.allD.outliers), 0)
            self.assertIn('formula', self.allD.outliers[0])
            self.assertIn('compVec', self.allD.outliers[0])


        with self.subTest(msg='Retrieve information on where the outlier data came from - no name filter'):
            self.allD.findOutlierDataSources(filterByName=False)





    def testTSNEplusDBSCAN(self) -> None:
        self.allD.getTSNE()
        # Low epsilon for nicer visual effect only
        self.allD.getDBSCAN(eps=0.05, min_samples=3)

        with self.subTest(msg='Printing out a plot with clusters'):
            self.allD.showClustersDBSCAN()

        with self.subTest(msg='Printing out a plot with outliers'):
            self.allD.updateOutliersList()










if __name__ == '__main__':
    unittest.main()
