import unittest
import os

import pyqalloy as pqa

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

class TestUtilities(unittest.TestCase):
    '''Test the utility functions of pyqalloy package that are not part of the core or curation modules, such as
    opening the docs in a web browser or headless.'''

    @unittest.skipIf(IN_GITHUB_ACTIONS, 'Test depends on the ability to open a web browser')
    def testShowDocs_Open(self):
        '''Test the showDocs() function of pyqalloy package by opening the documentation in a web browser.'''
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
            os.chdir('pyqalloy/tests/')

    def testShowDocs_Headless(self):
        '''Test the showDocs() function of pyqalloy package by requesting the documentation in a headless fashion and
        checking the response.'''
        with self.subTest(msg='Test if the online documentation is called when outside of main repository directory'):
            docStatus, docType = pqa.showDocs(headless=True)
            self.assertEqual(docStatus.status_code, 200)
            self.assertEqual(docType, 'online')

        with self.subTest(msg='Test if the local documentation is called when inside of main repository directory'):
            os.chdir('../../')
            docStatus, docType = pqa.showDocs(headless=True)
            self.assertIsInstance(docStatus, str)
            self.assertEqual(docType, 'local')
            os.chdir('pyqalloy/tests/')

if __name__ == '__main__':
    unittest.main()