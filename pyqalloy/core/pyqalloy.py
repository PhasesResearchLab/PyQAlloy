import requests

__version__ = '0.3.4'
__authors__ = [["Adam Krajewski", "ak@psu.edu"]]
__name__ = 'PyQAlloy'


def showDocs(headless=False):
    """Open the offline documentation in a web browser, if the documentation is available locally, i.e. when you are
    in the cloned pySIPFENN GitHub repository you've installed in editable mode. Note the function doesn't use importlib
    since docs are not part of the package for space savings. Otherwise, the function opens the online documentation.

    Args:
        headless: If True, the function will not open the documentation in a web browser. If it finds the local
            documentation, it will return the path to the local documentation. If it finds the online documentation, it
            will return the response object from the online documentation. If False, the function will open the
            documentation in a web browser.
    Returns:
        If headless=True, the function will return the path to the local documentation or the response object from the
        online documentation and the type of documentation. If headless=False, the function will return the status code
        from the web browser and the type of documentation.
    """
    import os
    if os.path.isfile('docs/_build/index.html'):
        print('Found the loacal documentation. Opening it now...')
        if headless:
            return 'file://' + os.path.abspath('docs/_build/index.html'), 'local'
        else:
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
