# Install pySIPFENN

## From GitHub
At the moment, PyQAlloy is not available on PyPI, so you need to clone the repository and install
it in editable mode. While not required, it is recommended to first set up a virtual environment using venv or Conda. 
This ensures that one of the required versions of Python (3.9+) is used and there are no dependency conflicts. 
If you have Conda installed on your system (see instructions at https://docs.conda.io/en/latest/miniconda.html), 
you can create a new environment with:

    conda create -n pyqalloy python=3.9 jupyter
    conda activate pyqalloy

Then, clone PyQAlloy from GitHub like

    git clone https://github.com/PhasesResearchLab/PyQAlloy.git

Or by downloading a ZIP file (not recommended if you want to make changes). Please note this will, by default, download 
the latest development version of the software, which may not be stable. For a stable version, you can specify a version 
tag after the URL with `--branch <tag_name> --single-branch`.

Then, move to the PyQAlloy folder and install in editable (`-e`) mode.

    cd PyQAlloy
    pip install -e .

## From TAR.GZ

If you have downloaded a TAR.GZ file, you should follow instructions above,
setting up the Conda environment, but instead of cloning from GitHub, 
you can quickly install it with

    pip install <path_to_tar.gz>

The resulting installation will be the same as if you installed a package from 
PyPI, but you will not be able to make changes to the code.

## Dataset connection
If you are using the [**ULTERA Project**](https://ultera.org) infrastructure, now you should fill in your details into the 
`pyqalloy/credentials.json` 'name' and 'dbKey' fields, and you should be ready to go! :)

If you are not using the ULTERA infrastructure, you will need to set up your own MongoDB database and fill it with data 
that conforms to the ULTERA schema. This will be quite elaborate, but we have the tools to do it, and we can assist you. 
