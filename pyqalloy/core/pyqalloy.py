import bson.json_util
import requests
import json
from importlib import resources
from urllib.parse import urlparse
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Union, Tuple, List, Dict, Any

import pandas as pd
import bson
from montydb import MontyClient
from montydb.types.bson import init as bson_init
from pymongo import MongoClient
from pymongo.collection import Collection

from pyqalloy.core.utils import datapoint2entry

__version__ = '0.3.5'
__authors__ = [["Adam Krajewski", "ak@psu.edu"]]
__name__ = 'PyQAlloy'


def setCredentials(
        name: str,
        dbKey: str,
        dataServer: str
    ) -> None:
    """Set the credentials for an ULTERA-compatible database (e.g. ULTERA), which itself is MongoDB-compatible. You need to 
    know (1) username, (2) database key, and (3) data server addres, which you can obtain from your database administrator.
    Internally, PyQAlloy will persist them to the "credentials.json" file in installation directory and use them to form a 
    connection URI to the database at runtime, which will then be used to access the data. 

    Args:
        name: Your username for the database. Make sure that you have basic permissions to read the data (write is not needed).
        dbKey: The key to access the database. This is a secret key, typically looking like x2mjf932fhx438hxz932, which you should
            never share with anyone.
        dataServer: The URI of the data server. This is the address of the server where the data is stored, typically looking like
            "testcluster.g3kud.mongodb.net/ULTREA_materials". It may also include the port, e.g. 
            "testcluster.g3kud.mongodb.net:27017/ULTREA_materials", or be appended with additional parameters like
            "?retryWrites=true&w=majority". It should *not* include the protocol ("mongodb+srv://").

    Returns:
        None. It persists the credentials to the "credentials.json" file in the installation directory.
    """
    with resources.files('pyqalloy').joinpath('credentials.json').open('r') as f:
        credentials = json.load(f)
        if credentials['name'] == name and credentials['dbKey'] == dbKey and credentials['dataServer'] == dataServer:
            print('The credentials are the same as the existing ones. No changes were made.')
        else:
            print('Replacing the existing credentials:\n', credentials, '\nwith the new ones:\n', {'name': name, 'dbKey': dbKey, 'dataServer': dataServer})
    with resources.files('pyqalloy').joinpath('credentials.json').open('w') as f:
        json.dump(
            {'name': name, 'dbKey': dbKey, 'dataServer': dataServer}, 
            f,
            indent=4)

def setCredentialsFromURI(
        uri: str
    ) -> None:
    """Construct the credentials dictionary from the MongoDB URI and persists it to the "credentials.json" file using the
    setCredentials function. 

    Args:
        uri: The MongoDB URI that contains the username, password, and data server address. The URI should be in the format
            "mongodb+srv://username:password@dataServer". You can skip the "mongodb+srv://" part without affecting the effects.

    Returns:
        None. It persists the credentials to the "credentials.json" file in the installation directory.
    """
    uri = urlparse(uri)
    setCredentials(uri.username, uri.password, uri.netloc.split('@')[-1])

def parseTemplate(
        template: str,
        targetCollection: Collection
    ) -> None:
    """Parse an ULTERA template XLSX file and persist the data ainto the ``targetCollection``. The template file should be
    in the ULTERA format (at least version 4) and contain all the required fields (e.g. "composition"). Please note that running this
    will only create a dataset of raw ULTERA upload entries which will (a) miss several fields, (b) not be validated, (c) only 
    partially homogenized, and (d) not aggregated around unique materials. Thus, not all PyQAlloy functions will work on the data
    produced by this function and you may need to either (1) contribute it to the ULTERA database and downselect your contribution
    based on your name (see tutorial) or (2) run the entire ULTERA-like pipeline on your own (separate codebase).

    Args:
        template: The path to the template file in the XLSX format.
        target: The MongoDB-compatible ``Collection`` object where the parsed data will be stored. It's quite flexible and can
            be pointed to both in-memory ``mongomock`` or ``MontyDB`` databases, or to a real MongoDB database in the cloud or on-premises.

    Returns:
        None. It persists the parsed data to the target collection.
    """

    #Import metadata
    print('Reading the metadata.')
    metaDF = pd.read_excel(template, usecols="A:F", nrows=4)
    meta = metaDF.to_json(orient="split")
    metaParsed = json.loads(meta, strict=False)['data']

    # Format metadata into a dictionary
    metaData = {
        'source': 'LIT',
        'name': metaParsed[0][1],
        'email': metaParsed[1][1],
        'directFetch': metaParsed[2][1],
        'handFetch': metaParsed[3][1],
        'comment': metaParsed[0][5],
        'timeStamp': datetime.now(ZoneInfo('America/New_York')),
        'dataSheetName': template
    }
    print('Data credited to: '+metaParsed[0][1])
    print('Contact email: '+metaParsed[1][1])

    # Import data
    print('\nImporting data.')
    df2 = pd.read_excel(template, usecols="A:N", nrows=10000, skiprows=8)
    result = df2.to_json(orient="records")
    parsed = json.loads(result, strict=False)
    print('Imported '+str(parsed.__len__())+' datapoints.\n')

    # Convert metadata and data into database datapoints and upload
    for datapoint in parsed:
        comp = datapoint['Composition'].replace(' ','')
        try:
            uploadEntry = datapoint2entry(metaData, datapoint)
            targetCollection.insert_one(uploadEntry)
            print(f'[x] {comp}')
        except ValueError as e:
            exceptionMessage = str(e)
            print(f'[ ] Upload failed! ---> {exceptionMessage}\n')
            pass



def showDocs(headless=False) -> Tuple[Union[int, requests.models.Response, str], str]:
    """Open the offline documentation in a web browser, if the documentation is available locally, i.e. when you are
    in the cloned pySIPFENN GitHub repository you've installed in editable mode. It should work as expected if you do
    remote development in VS Code. Note the function doesn't use importlib since docs are not part of the package.
    In any other case, the function opens the online documentation and ULTERA web page.

    Args:
        headless: If True, the function will not open the documentation in a web browser, but will return the response
        object from the online documentation. If False, the function will open the documentation in a web browser either
        locally or online. Default is False.
    Returns:
        If headless is False, the function returns a tuple with the status code of the web browser opening the
        documentation and the type of documentation that was opened. If headless is True, the function returns a tuple
        with the response object from the online documentation and the type of documentation that was opened.
    """
    import os
    if os.path.isfile('docs/_build/index.html') and not headless:
        print('Found the local documentation. Opening it now...')
        return os.system('open docs/_build/index.html'), 'local'
    else:
        print('Documentation local files were not found. Please be advised that the documentation is only available if '
              'you are in cloned pySIPFENN GitHub repository. pySIPFENN will now attempt to visit '
              'https://pysipfenn.org for the online documentation.')
        if headless:
            return requests.get('https://pyqalloy.ultera.org'), 'online'
        else:
            os.system('open https://ultera.org')
            return os.system('open https://pyqalloy.ultera.org'), 'online'
