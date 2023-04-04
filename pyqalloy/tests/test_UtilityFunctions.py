import unittest
import os

import pyqalloy as pqa

class TestUtilities(unittest.TestCase):
    '''Test the utility functions of pyqalloy package that are not part of the core or curation modules.'''

    def testShowDocs(self):
        print('Testing the showDocs() function of pyqalloy package.')
        with self.subTest(msg='Test if the online documentation is called when outside of main repository directory'):
            docStatus, docType = pqa.showDocs()
            self.assertEqual(docStatus, 0)
            self.assertEqual(docType, 'online')

        with self.subTest(msg='Test if the local documentation is called when inside of main repository directory'):
            os.chdir('../../')
            docStatus, docType = pqa.showDocs()
            self.assertEqual(docStatus, 0)
            self.assertEqual(docType, 'local')
