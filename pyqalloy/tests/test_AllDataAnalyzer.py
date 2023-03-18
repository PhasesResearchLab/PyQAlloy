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





if __name__ == '__main__':
    unittest.main()
