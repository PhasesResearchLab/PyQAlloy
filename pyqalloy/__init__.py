from pyqalloy.core import *
from pyqalloy.curation import *

def showDocs():
    """Open the offline documentation in a web browser, if the documentation is available locally, i.e. when you are
    in the cloned pySIPFENN GitHub repository you've installed in editable mode. Note the function doesn't use importlib
    since docs are not part of the package for space savings. Otherwise, the function opens the online documentation."""

    import os
    if os.path.isfile('docs/_build/index.html'):
        print('Found the loacal documentation. Opening it now...')
        os.system('open docs/_build/index.html')
    else:
        os.system('open https://ultera.org')
        print('Documentation local files were not found. Please be advised that the documentation is only available if'
              'you are in cloned pySIPFENN GitHub repository. pySIPFENN will now attempt to visit '
              'https://pysipfenn.org for the online documentation.')