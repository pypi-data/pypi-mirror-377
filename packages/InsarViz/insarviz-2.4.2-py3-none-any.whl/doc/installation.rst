############
Installation
############


Installation
************

If you would like to be able to **modify the code** or use a beta version, follow instead the **Developer installation** below.

Set up the environment
--------------------------

We recommend you to install the InsarViz tool in a *virtual environment* (an independent package installation, so that the package versions required by InsarViz do not mess up with your own installation).

* **With Anaconda**

If you have installed the `Anaconda distribution <https://docs.anaconda.com/anaconda/install/>`_ (for example Miniconda). If you are using Windows, open an *Anaconda Powershell Prompt*. Create a conda environment (InsarViz requires Python >= 3.9):

.. code-block :: bash

 conda create -n insarviz-env python=3.9

And then *activate* it:

.. code-block :: bash

 conda activate insarviz-env

* **Without Anaconda**

Without Anaconda, create a Python virtual environment (InsarViz requires Python >= 3.9):

.. code-block :: bash

 python3 -m venv path_to_venv

And then *activate* it:

.. code-block :: bash

 source path_to_venv/bin/activate

Install
-------

Installing InsarViz in a virtual environment (activate it first), or system-wide, is just a one-line command:

.. code-block :: bash

 pip install insarviz

If you already installed InsarViz before and only want to update it, run this command instead: 

.. code-block :: bash

 pip install insarviz -U

Check your installation
-----------------------

You can check your installation by doing (first activate the virtual environment if you used one):

.. code-block :: bash

 ts_viz --help

This should print the help message. If not, your install failed.

Run InsarViz
----------------

Simply run InsarViz from the following command line (first activate the virtual environment if you used one):

.. code-block :: bash

 ts_viz 

You can provide directly the path of a file to open (an Insar datacube or an InsarViz project) using the *-i* option:

.. code-block :: bash

 ts_viz -i path_to_file

Debug
*****

Check that you used the pip of the virtual environment to install insarviz:

.. code-block :: bash

 which pip

Should return ``/path/to/venv/bin/pip``.
You can enforce the use of the correct pip using:

.. code-block :: bash

 /path/to/venv/bin/pip install insarviz

If the install prompts an error, try updating pip:

.. code-block :: bash

 python3 -m pip install --upgrade pip

If you get errors mentioning rasterio, try:

.. code-block :: bash

 python3
 >> import rasterio

If this fails with an error mentioning that rasterio cannot find libgdal.so.XX, you 
should try changing the version of GDAL you are using. InsarViz has rasterio 
(https://rasterio.readthedocs.io) as dependency. Rasterio depends upon the GDAL library 
(https://gdal.org) and assumes gdal is already installed. We recommend using version 
1.3.10 of rasterio which is compatible with GDAL >= 3.1 (on Linux, use the command 
gdalinfo --version to figure out which version of gdal you have).

Developer installation 
***********************

Follow this section instead of the **Installation** section if you would like to be able to **modify the code** or use a beta version.

Download source code
--------------------

Download the source code using git (first navigate to the destination folder):

* *Without a gitlab account*:

.. code-block :: bash

 git clone https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz

* *With a gitlab account (ssh)*:

.. code-block :: bash

 git clone git@gricad-gitlab.univ-grenoble-alpes.fr:deformvis/insarviz.git

Note that you can specify a branch using the option *-b*, for example the *beta* branch:

.. code-block :: bash

 git clone https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz -b beta

Use UV to install
-----------------

We recommend using UV
(https://docs.astral.sh/uv/getting-started/installation/) to manage
the dependencies and install InsarViz for developers. A lock file
(``uv.lock``) is included in the project directory, to allow for
easily recreating a proper environment. First navigate inside the root
of the cloned folder, then create a environment using the following
command :

.. code-block :: bash

   uv venv --python 3.9  # Create a virtual environment with a specific Python version

Once the environment is created, there are two ways to run InsarViz :

* Activating the environment manually

.. code-block :: bash

   uv sync --locked           # Install InsarViz and its dependencies from the lock file
   source .venv/bin/activate  # Activate the environment
   ts_viz                     # Launch InsarViz

* Running InsarViz through UV

.. code-block :: bash
  
   uv run --locked ts_viz

Update InsarViz after modifying the code
------------------------------------------

By default, UV installs InsarViz as an "editable" package
(https://docs.astral.sh/uv/concepts/projects/sync/#editable-installation). In
short, it means that you don't have to reinstall it each time you
modify the code.
