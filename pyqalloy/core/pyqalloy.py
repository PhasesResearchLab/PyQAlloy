import requests
import json
from importlib import resources
from urllib.parse import urlparse
from typing import Union, Tuple, List, Dict, Any, Optional

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
