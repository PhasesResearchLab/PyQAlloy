import unittest
import json
from io import StringIO
from contextlib import redirect_stdout

import pyqalloy
from pyqalloy.curation import analysis
from montydb import MontyClient
from montydb.types.bson import init as init_bson
import bson


    
class TestTemplateParsingIntoJSON(unittest.TestCase):
    """Tests corectness of the parsing of the template provided in the examples folder into JSON format by (1) investigating corectness of the generated 
    entries against the expected reference entries and (2) testing for correct error throwing in the case of purposefully incomplete data at one of the 
    example template lines.
    """

    def setUp(self):
        # Error is expected on certain line/s
        self.errorLines = [81]
        # Number of expected entries in the JSON file after parsing
        self.expectedEntries = 83 - len(self.errorLines)
        # The reference "_id" fields are discarded in the test, as they are generated by the database based on the UNIX timestamp and will not match.
        self.referenceEntries = \
        """
        [
            {"_id": {"$oid": "671a288cc978aa5bc7e27bce"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.424Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Ti30 Zr30 Hf16 Nb24", "formula": "Hf8 Zr15 Ti15 Nb12", "compositionDictionary": {"Ti": 0.3, "Zr": 0.3, "Hf": 0.16, "Nb": 0.24}, "percentileFormula": "Hf16 Zr30 Ti30 Nb24", "relationalFormula": "Hf1 Zr1.88 Ti1.88 Nb1.5", "compositionVector": [0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.3, 0.24, 0.0, 0.0, 0.0, 0.16, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "A8B12C15D15", "reducedFormula": "Hf8Zr15(Ti5Nb4)3", "system": "Hf-Nb-Ti-Zr", "elements": ["Hf", "Nb", "Ti", "Zr"], "nComponents": 4, "structure": ["BCC"], "nPhases": 1, "processes": ["AC", "CR", "A", "A"], "nProcessSteps": 4, "comment": "20min at 900*C + 200h at 600*C", "observationTemperature": 298.0}, "property": {"name": "tensile yield strength", "value": 730000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.actamat.2023.118728", "pointer": "F6"}},
            {"_id": {"$oid": "671a288cc978aa5bc7e27be0"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.424Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Zr Nb Ta Hf0.2 Cr1", "formula": "Hf0.2 Zr1 Ta1 Nb1 Cr1", "compositionDictionary": {"Zr": 0.23809523809523808, "Nb": 0.23809523809523808, "Ta": 0.23809523809523808, "Hf": 0.047619047619047616, "Cr": 0.23809523809523808}, "percentileFormula": "Hf4.8 Zr23.8 Ta23.8 Nb23.8 Cr23.8", "relationalFormula": "Hf1 Zr5 Ta5 Nb5 Cr5", "compositionVector": [0.0, 0.0, 0.2381, 0.0, 0.0, 0.0, 0.0, 0.2381, 0.2381, 0.0, 0.0, 0.2381, 0.0476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "A0.2BCDE", "reducedFormula": "Hf0.2Zr1Ta1Nb1Cr1", "system": "Cr-Hf-Nb-Ta-Zr", "elements": ["Cr", "Hf", "Nb", "Ta", "Zr"], "nComponents": 5, "structure": ["BCC", "C15", "HCP"], "nPhases": 3, "processes": ["AC"], "nProcessSteps": 1, "observationTemperature": 298.0}, "property": {"name": "ultimate compressive strength", "value": 1420000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.jallcom.2022.166593", "pointer": "S"}},
            {"_id": {"$oid": "671a288cc978aa5bc7e27c57"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.479Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Zr35 Ti30 Nb20 Al10 Ta5 ", "formula": "Zr7 Ti6 Ta1 Nb4 Al2", "compositionDictionary": {"Zr": 0.35, "Ti": 0.3, "Nb": 0.2, "Al": 0.1, "Ta": 0.05}, "percentileFormula": "Zr35 Ti30 Ta5 Nb20 Al10", "relationalFormula": "Zr7 Ti6 Ta1 Nb4 Al2", "compositionVector": [0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.0, 0.35, 0.2, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "AB2C4D6E7", "reducedFormula": "Zr7TaTi6(Nb2Al)2", "system": "Al-Nb-Ta-Ti-Zr", "elements": ["Al", "Nb", "Ta", "Ti", "Zr"], "nComponents": 5, "structure": ["BCC"], "nPhases": 1, "processes": ["VAM", "CR", "A", "WQ"], "nProcessSteps": 4, "comment": "5min at 1050*C in argon in quartz tube, B2 nanoprecipitates", "observationTemperature": 298.0}, "property": {"name": "tensile yield strength", "value": 841000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.ijrmhm.2023.106263", "pointer": "P"}}
        ]
        """
        
        with self.subTest('Runtime execution of the parsing (plus output capture.)'):
            output = StringIO()
            with redirect_stdout(output):
                pyqalloy.parseTemplateToJSON('examples/ExampleTemplateULTERA_ErrorsAdded.xlsx', 'data.json')
            self.parsingPrintout = output.getvalue()

    def test_JSON_present(self):
        with self.subTest('Check if the JSON file was created (even if it is empty).'):
            with open('data.json', 'r') as f:
                self.jsonData = f.read()
            self.assertGreater(len(self.jsonData), 0)
            

        with self.subTest('Check if the JSON file has the data payload (json loadable).'):
            with open('data.json', 'r') as f:
                self.jsonData = f.read()
            self.assertIsInstance(json.loads(self.jsonData), list)
                
    def test_printout(self):
        with self.subTest('Check if the printout captured is not empty.'):
            self.assertGreater(len(self.parsingPrintout), 0)
        
        with self.subTest('Check if a set of expected symbols is present in the printout.'):
            self.assertIn('Importing data.', self.parsingPrintout, msg='Data import not found.')
            self.assertIn('Reading the metadata.', self.parsingPrintout, msg='Metadata reading not found.')
            self.assertIn('L10  [x]', self.parsingPrintout, msg='Line 10 successful upload (first data line in the template) was expected but not found.')
            self.assertIn('MoNbTaW', self.parsingPrintout, msg='MoNbTaW on template example line 10 was expected but not found.')
            self.assertIn('Persisted the data to the target file:  data.json', self.parsingPrintout)

        with self.subTest('Check if the error message is present in the printout.'):
            self.assertIn('Upload failed! --->', self.parsingPrintout)

        with self.subTest('Check if the error lines are correctly detected.'):
            for line in self.errorLines:
                self.assertIn(f'L{line:<3} [ ]', self.parsingPrintout, msg=f'Error on line {line} not found.')

    def test_references(self):
        with open('data.json', 'r') as f:
            self.jsonData = f.read()
        dataDicts = json.loads(self.jsonData)
        for i, entry in enumerate(dataDicts):
            entry.pop('_id')
            entry['meta'].pop('timeStamp')
            entry['meta'].pop('dataSheetName')

        dataDictsRef = json.loads(self.referenceEntries)
        for i, entry in enumerate(dataDictsRef):
            with self.subTest(f'Check if the reference entry {i} is present in the parsed data (with exception of some fields).'):
                entry.pop('_id')    
                entry['meta'].pop('timeStamp')
                entry['meta'].pop('dataSheetName')

                self.assertTrue(
                    any(
                        all(
                            key in d and d[key] == value for key, value in entry.items()
                        )
                        for d in dataDicts
                    )
                )

    def test_NoIndentationJSON(self):
        with self.subTest('Runtime execution of the parsing with no-indentation JSON output.'):
            pyqalloy.parseTemplateToJSON('examples/ExampleTemplateULTERA_ErrorsAdded.xlsx', 'data-ni.json', indent=None, verbose=False)
        
        with self.subTest('Check if the JSON file was created (even if it is empty).'):
            with open('data-ni.json', 'r') as f:
                self.jsonData = f.read()
            self.assertGreater(len(self.jsonData), 0)

        with self.subTest('Check that the JSON can be loaded without errors.'):
            with open('data-ni.json', 'r') as f:
                self.jsonData = f.read()
            loadedData = json.loads(self.jsonData)
            self.assertIsInstance(loadedData, list)
            self.assertGreater(len(loadedData), 0)

        with self.subTest('Check that the number of lines in the JSON matches the number of expected entries plus the first and last line.'):
            self.assertEqual(self.jsonData.count('\n') - 2, self.expectedEntries)

    def tearDown(self):
        pass


class TestTemplateParsingIntoBSON(unittest.TestCase):
    """Tests corectness of the parsing of the template provided in the examples folder into BSON format by (1) investigating corectness of the generated 
    entries against the expected reference entries and (2) testing for correct error throwing in the case of purposefully incomplete data at one of the 
    example template lines.
    """

    def setUp(self):
        # Error is expected on certain line/s
        self.errorLines = [81]
        # Number of expected entries in the JSON file after parsing
        self.expectedEntries = 83 - len(self.errorLines)
        # The reference "_id" fields are discarded in the test, as they are generated by the database based on the UNIX timestamp and will not match.
        self.referenceEntries = \
        """
        [
            {"_id": {"$oid": "671a288cc978aa5bc7e27bce"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.424Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Ti30 Zr30 Hf16 Nb24", "formula": "Hf8 Zr15 Ti15 Nb12", "compositionDictionary": {"Ti": 0.3, "Zr": 0.3, "Hf": 0.16, "Nb": 0.24}, "percentileFormula": "Hf16 Zr30 Ti30 Nb24", "relationalFormula": "Hf1 Zr1.88 Ti1.88 Nb1.5", "compositionVector": [0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.3, 0.24, 0.0, 0.0, 0.0, 0.16, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "A8B12C15D15", "reducedFormula": "Hf8Zr15(Ti5Nb4)3", "system": "Hf-Nb-Ti-Zr", "elements": ["Hf", "Nb", "Ti", "Zr"], "nComponents": 4, "structure": ["BCC"], "nPhases": 1, "processes": ["AC", "CR", "A", "A"], "nProcessSteps": 4, "comment": "20min at 900*C + 200h at 600*C", "observationTemperature": 298.0}, "property": {"name": "tensile yield strength", "value": 730000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.actamat.2023.118728", "pointer": "F6"}},
            {"_id": {"$oid": "671a288cc978aa5bc7e27be0"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.424Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Zr Nb Ta Hf0.2 Cr1", "formula": "Hf0.2 Zr1 Ta1 Nb1 Cr1", "compositionDictionary": {"Zr": 0.23809523809523808, "Nb": 0.23809523809523808, "Ta": 0.23809523809523808, "Hf": 0.047619047619047616, "Cr": 0.23809523809523808}, "percentileFormula": "Hf4.8 Zr23.8 Ta23.8 Nb23.8 Cr23.8", "relationalFormula": "Hf1 Zr5 Ta5 Nb5 Cr5", "compositionVector": [0.0, 0.0, 0.2381, 0.0, 0.0, 0.0, 0.0, 0.2381, 0.2381, 0.0, 0.0, 0.2381, 0.0476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "A0.2BCDE", "reducedFormula": "Hf0.2Zr1Ta1Nb1Cr1", "system": "Cr-Hf-Nb-Ta-Zr", "elements": ["Cr", "Hf", "Nb", "Ta", "Zr"], "nComponents": 5, "structure": ["BCC", "C15", "HCP"], "nPhases": 3, "processes": ["AC"], "nProcessSteps": 1, "observationTemperature": 298.0}, "property": {"name": "ultimate compressive strength", "value": 1420000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.jallcom.2022.166593", "pointer": "S"}},
            {"_id": {"$oid": "671a288cc978aa5bc7e27c57"}, "meta": {"source": "LIT", "name": "Adam Krajewski", "email": "ak@psu.edu", "directFetch": "T", "handFetch": "F", "comment": null, "timeStamp": {"$date": "2024-10-24T10:59:24.479Z"}, "dataSheetName": "ExampleTemplateULTERA_ErrorsAdded.xlsx"}, "material": {"rawFormula": "Zr35 Ti30 Nb20 Al10 Ta5 ", "formula": "Zr7 Ti6 Ta1 Nb4 Al2", "compositionDictionary": {"Zr": 0.35, "Ti": 0.3, "Nb": 0.2, "Al": 0.1, "Ta": 0.05}, "percentileFormula": "Zr35 Ti30 Ta5 Nb20 Al10", "relationalFormula": "Zr7 Ti6 Ta1 Nb4 Al2", "compositionVector": [0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.0, 0.35, 0.2, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "anonymizedFormula": "AB2C4D6E7", "reducedFormula": "Zr7TaTi6(Nb2Al)2", "system": "Al-Nb-Ta-Ti-Zr", "elements": ["Al", "Nb", "Ta", "Ti", "Zr"], "nComponents": 5, "structure": ["BCC"], "nPhases": 1, "processes": ["VAM", "CR", "A", "WQ"], "nProcessSteps": 4, "comment": "5min at 1050*C in argon in quartz tube, B2 nanoprecipitates", "observationTemperature": 298.0}, "property": {"name": "tensile yield strength", "value": 841000000.0, "source": "EXP", "temperature": 298.0, "unitName": "Pa"}, "reference": {"doi": "10.1016/j.ijrmhm.2023.106263", "pointer": "P"}}
        ]
        """
        
        with self.subTest('Runtime execution of the parsing (plus output capture.)'):
            output = StringIO()
            with redirect_stdout(output):
                pyqalloy.parseTemplateToBSON('examples/ExampleTemplateULTERA_ErrorsAdded.xlsx', 'data.bson')
            self.parsingPrintout = output.getvalue()

    def test_BSON_present(self):
        with self.subTest('Check if the BSON file was created (even if it is empty).'):
            with open('data.bson', 'rb') as f:
                self.bsonData = f.read()
            self.assertGreater(len(self.bsonData), 0)

    def test_printout(self):
        with self.subTest('Check if the printout captured is not empty.'):
            self.assertGreater(len(self.parsingPrintout), 0)
        
        with self.subTest('Check if a set of expected symbols is present in the printout.'):
            self.assertIn('Importing data.', self.parsingPrintout, msg='Data import not found.')
            self.assertIn('Reading the metadata.', self.parsingPrintout, msg='Metadata reading not found.')
            self.assertIn('L10  [x]', self.parsingPrintout, msg='Line 10 successful upload (first data line in the template) was expected but not found.')
            self.assertIn('MoNbTaW', self.parsingPrintout, msg='MoNbTaW on template example line 10 was expected but not found.')
            self.assertIn('Persisted the data to the target file:  data.bson', self.parsingPrintout)

        with self.subTest('Check if the error message is present in the printout.'):
            self.assertIn('Upload failed! --->', self.parsingPrintout)

        with self.subTest('Check if the error lines are correctly detected.'):
            for line in self.errorLines:
                self.assertIn(f'L{line:<3} [ ]', self.parsingPrintout, msg=f'Error on line {line} not found.')

    def test_references(self):
        init_bson(use_bson=True)
        tempCollection = MontyClient(":memory:").db.test

        with open('data.bson', 'rb+') as f:
            tempCollection.insert_many(bson.decode_all(f.read()))

        with self.subTest('Check if the collection has been populated with the expected number of entries.'):
            self.assertEqual(tempCollection.count_documents({}), self.expectedEntries)

        dataDicts = list(tempCollection.find({}, {'_id': 0, 'meta.timeStamp': 0, 'meta.dataSheetName': 0}))

        dataDictsRef = json.loads(self.referenceEntries)

        for i, entry in enumerate(dataDictsRef):
            with self.subTest(f'Check if the reference entry {i} is present in the parsed data (with exception of some fields).'):
                entry.pop('_id')
                entry['meta'].pop('timeStamp')
                entry['meta'].pop('dataSheetName')

                self.assertTrue(
                    any(
                        all(
                            key in d and d[key] == value for key, value in entry.items()
                        )
                        for d in dataDicts
                    )
                )

    def tearDown(self):
        pass
    
if __name__ == '__main__':
    unittest.main()
