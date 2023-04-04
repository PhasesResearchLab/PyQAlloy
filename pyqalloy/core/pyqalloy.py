import requests
from typing import Union, Tuple, List, Dict, Any, Optional

__version__ = '0.3.4'
__authors__ = [["Adam Krajewski", "ak@psu.edu"]]
__name__ = 'PyQAlloy'


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
