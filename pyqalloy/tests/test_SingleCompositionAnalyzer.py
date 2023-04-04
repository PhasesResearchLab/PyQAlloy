import unittest

from pyqalloy.curation import analysis


class TestSCADA(unittest.TestCase):
    '''Test the SingleCompositionAnalyzer class in the curation module by (1) obtaining the data from ULTERA Database,
    (2) performing a scan of the compositions around 100, but not exceeding 100, and (3) partially verifying results.
    '''

    def setUp(self) -> None:
        self.sC = analysis.SingleCompositionAnalyzer()
        pass

    def test_ScanQL(self):
        self.sC.scanCompositionsAround100(queryLimit=20, printOnFly=True)
        resLen1 = len(self.sC.printOuts)
        print(f'First scan (QL=10): {resLen1} results')
        self.sC.scanCompositionsAround100(queryLimit=500, printOnFly=False)
        resLen2 = len(self.sC.printOuts)
        print(f'Second scan (QL=+500): {resLen2} results')
        self.assertGreater(resLen2,
                           resLen1,
                           msg='Results are added to the printOuts list whenever scan is run, so the '
                               'length of the list should increase every time until all abnormalities '
                               'are found')
        self.assertGreater(resLen2 - resLen1,
                           resLen1,
                           msg='The number of results should increase when the query limit is increased')

    def test_ScanBounds(self):
        self.sC.scanCompositionsAround100(queryLimit=1000, lowerBound=95, upperBound=105, printOnFly=False)
        resLen1 = len(self.sC.printOuts)
        print(f'First scan (LB=95, UB=105): {resLen1} results')
        self.sC = analysis.SingleCompositionAnalyzer()
        self.sC.scanCompositionsAround100(queryLimit=1000, lowerBound=50, upperBound=150, printOnFly=False)
        resLen2 = len(self.sC.printOuts)
        print(f'Second scan (LB=50, UB=150): {resLen2} results')
        self.assertGreater(resLen2, resLen1, msg='The number of results should increase when the bounds of what is '
                                                 'considered "around 100%" are increased from 95-105% to 50-150%')

    def test_ScanRL(self):
        with self.subTest(msg='Scan'):
            self.sC.scanCompositionsAround100(resultLimit=5, printOnFly=True)
            resLen1 = len(self.sC.printOuts)
            print(f'First scan (RL=5): {resLen1} results')
            self.assertEqual(resLen1, 5)
            self.sC.scanCompositionsAround100(resultLimit=10, printOnFly=False)
            resLen2 = len(self.sC.printOuts)
            print(f'Second scan (RL=+10): {resLen2} results')
            self.assertEqual(resLen2, 10)

        with self.subTest(msg='Write Results'):
            self.sC.writeResultsToFile('testResults.txt')
