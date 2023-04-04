# PyQAlloy: Python tools for ensuring the Quality of Alloys data

![GitHub top language](https://img.shields.io/github/languages/top/PhasesResearchLab/PyQAlloy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyqalloy)
![GitHub license](https://img.shields.io/github/license/PhasesResearchLab/PyQAlloy)
![build status](https://github.com/PhasesResearchLab/PyQAlloy/actions/workflows/test.yml/badge.svg)
![build status](https://github.com/PhasesResearchLab/PyQAlloy/actions/workflows/lastCommit.yml/badge.svg)
[![codecov](https://codecov.io/gh/PhasesResearchLab/PyQAlloy/branch/main/graph/badge.svg?token=M1DWRD4ML3)](https://codecov.io/gh/PhasesResearchLab/PyQAlloy)

[![stable](https://img.shields.io/badge/Read%20The%20Docs-Stable-green)](https://pyqalloy.readthedocs.io/en/stable/) 
[![latest](https://img.shields.io/badge/Read%20The%20Docs-Latest-green)](https://pyqalloy.readthedocs.io/en/latest/)
[![ULTERA](https://img.shields.io/badge/ULTERA-statistics-red)](https://ULTERA.org)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/PhasesResearchLab/PyQAlloy?label=Last%20Commit)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/PhasesResearchLab/PyQAlloy?label=Last%20Release)
![GitHub commits since tagged version](https://img.shields.io/github/commits-since/PhasesResearchLab/PyQAlloy/v0.3.0?color=g)
![GitHub issues](https://img.shields.io/github/issues/PhasesResearchLab/PyQAlloy)

## Introduction

PyQAlloy development is a part of [**ULTERA Project**](https://ultera.org) carried under the 
[**DOE ARPA-E ULTIMATE program**](https://arpa-e.energy.gov/?q=arpa-e-programs/ultimate) that
aims to develop a new generation of materials for turbine blades in gas turbines and related
applications. The [ULTERA Project](https://ultera.org), along is led by 
[Phases Research Lab](https://phaseslab.com) at Penn State. As a part of it, we developed 
a new large-scale database of high entropy alloys (HEAs) reported in the literature
along with their experimental properties. As of March 2023, the database contains
around 6,000 property data points of 2,500 HEAs coming from almost 500 publications. It is
currently the largest database of HEAs in the world, and while it is not publicly available
we welcome collaborators who would like to use it in their research or contribute to it.

ULTERA Database is not simply a dataset but features a robust set of data processing, 
curation, and aggregation tools we built for the last 3 years. These tools allowed us to 
remove around the 5-10% erroneous data we identified in datasets available in the literature.
Most of our tools are not published yet, as the project is ongoing (they give us a competitive
advantage), and because most of the tools require an elaborate computing infrastructure setup.

However, as some of them are less-infrastructure-demanding and are, at the same time
highly applicable outside HEAs, we decided to release them as separate packages. This repository
contains the first of such packages, **PyQAlloy**, which is a Python package for detecting data
abnormalities in datasets of arbitrary alloys, ranging from complex, concentrated solutions, i.e.
High Entropy Alloys (HEAs) / Multi Principle Element Alloys (MPEAs) / Concentrated Complex Alloys 
(CCAs) to more traditional alloys such as steels, nickel-based superalloys, etc.

## Installation

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

If you are using the [**ULTERA Project**](https://ultera.org) infrastructure, now you should fill in your details into the 
`pyqalloy/credentials.json` with `name`, `dbKey`, and `dataServer` fields, and you should be ready to go! :)

If you are not using the ULTERA infrastructure, you will need to set up your own MongoDB database and fill it with data 
that conforms to the ULTERA schema. This will be quite elaborate, but we have the tools to do it, and we can assist you. 

