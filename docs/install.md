# Installation

## Basic (as a library)

PyQAlloy is readily available on PyPI (since V0.3.5), and you can get it with a simple:

    pip install pyqalloy

Once the installation process is complete, you will be able to utilize it in your Python scripts 
or Jupyter notebooks.


## Development (recommended)

**To get a ready-to-go installation of PyQAlloy with all notebooks in this repository, it is recommended
to install it in development mode** - that is to clone the repository and install it in editable mode. 

While not required, it is recommended to first set up a virtual environment using venv or Conda. 
This ensures that one of the required versions of Python (3.9+) is used and there are no dependency conflicts. 
If you have Conda installed on your system (see instructions at https://docs.conda.io/en/latest/miniconda.html), 
you can create a new environment with:

    conda create -n pyqalloy python=3.9 jupyter
    conda activate pyqalloy

Then, clone PyQAlloy from GitHub like

    git clone https://github.com/PhasesResearchLab/PyQAlloy.git

Please note this will, by default, download 
the latest development version of the software, which may not be stable. For a stable version, you can specify a version 
tag after the URL with `--branch <tag_name> --single-branch`.

Then, move to the PyQAlloy folder and install in editable (`-e`) mode.

    cd PyQAlloy
    pip install -e .


## Database Access 

If you are using the [**ULTERA Project**](https://ultera.org) infrastructure, now you should fill in your details into the 
`pyqalloy/credentials.json` with `name`, `dbKey`, and `dataServer` fields, and you should be ready to go as the most current 
stable version will be kept up-to-date with the latest stable snapshot of ULTERA! :)

## Getting Started 

### If you have ULTERA access

You can start by going through the `UserCuration.ipynb` notebook. It will guide you through
all core functionalities of PyQAlloy.

### If you are not using the ULTERA infrastructure 
You will need to set up your own MongoDB database or another tool
"pretending" to be one and fill it with data that conforms to the ULTERA schema. You can do it either manually
(instructions will be provided in the future, and we are happy to help you get started today) or by using
a snapshot of the ULTERA database subset `devTools/ULTERA_sample.bson` if you only want to learn how to use PyQAlloy
for now.

Start with `CustomDatasetFromBSON.ipynb` notebook which will show you how to create a custom MontyDB in-memory database
from a BSON file (or JSON if you prefer). Then, you can modify the `UserCuration.ipynb` notebook to use your custom 
database and work through all exercises there.