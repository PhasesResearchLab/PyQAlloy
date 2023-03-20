=========
PyQAlloy
=========

PyQAlloy development is a part of `ULTERA
Project <https://ultera.org>`__ carried under the `DOE ARPA-E ULTIMATE
program <https://arpa-e.energy.gov/?q=arpa-e-programs/ultimate>`__ that
aims to develop a new generation of materials for turbine blades in gas
turbines and related applications. The `ULTERA
Project <https://ultera.org>`__, along is led by `Phases Research
Lab <https://phaseslab.com>`__ at Penn State. As a part of it, we
developed a new large-scale database of high entropy alloys (HEAs)
reported in the literature along with their experimental properties. As
of March 2023, the database contains around 6,000 property data points
of 2,500 HEAs coming from almost 500 publications. It is currently the
largest database of HEAs in the world, and while it is not publicly
available we welcome collaborators who would like to use it in their
research or contribute to it.

ULTERA Database is not simply a dataset but features a robust set of
data processing, curation, and aggregation tools we built for the last 3
years. These tools allowed us to remove around the 5-10% erroneous data
we identified in datasets available in the literature. Most of our tools
are not published yet, as the project is ongoing (they give us a
competitive advantage), and because most of the tools require an
elaborate computing infrastructure setup.

However, as some of them are less-infrastructure-demanding and are, at
the same time highly applicable outside HEAs, we decided to release them
as separate packages. This repository contains the first of such
packages, **PyQAlloy**, which is a Python package for detecting data
abnormalities in datasets of arbitrary alloys, ranging from complex,
concentrated solutions, i.e. High Entropy Alloys (HEAs) / Multi
Principle Element Alloys (MPEAs) / Concentrated Complex Alloys (CCAs) to
more traditional alloys such as steels, nickel-based superalloys, etc.

.. image:: assets/AbnormalCompositionDetection_v1.png
    :width: 300pt
    :alt: schematic
    :align: center

.. note::
   This project is under active development. We recommend using released (stable) versions.

Index
-----

.. toctree::
   install
   source/pyqalloy
   examples/UserCuration
   genindex
   :maxdepth: 2
   :caption: Contents