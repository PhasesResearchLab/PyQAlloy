import unittest
import csv
import os
from pymatgen.core import Structure
from tqdm import tqdm
import numpy as np
from natsort import natsorted
from importlib import resources

from ulteratools.data_analyzer import curation

class TestADA(unittest.TestCase):

    def setUp(self) -> None:
        self.ADA = curation.AbnormalDataAnalyzer()
        pass

    def test_NNdistance(self):
        doi = '10.3390/met9010076'
        self.ADA.analyze_nnDistances(doi)

if __name__ == '__main__':
    unittest.main()
