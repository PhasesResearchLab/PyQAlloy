import unittest

from pyqalloy.data_analyzer import curation

class TestAllDataContext(unittest.TestCase):

    def setUp(self) -> None:
        self.allD = curation.AllDataAnalyzer()
        pass



if __name__ == '__main__':
    unittest.main()
