.. _installation:

Installation
============

``libra-toolbox`` relies on Python. You can install it from the official website: https://www.python.org/downloads/

To install ``libra-toolbox`` from PyPI, use pip:

.. code-block:: bash

   pip install libra-toolbox

This will install the latest version of the code along with all the dependencies (``numpy``, ``pint``, ``scipy``...).

To install a specific version of the code:

.. code-block:: bash

   pip install libra-toolbox==0.6.1

Here, ``0.6.1`` is the version number. You can replace it with the version you want to install.

To install the code in editable mode (i.e. the code is installed in the current directory and any changes to the code are immediately available to the user):

.. code-block:: bash

   git clone https://github.com/LIBRA-project/libra-toolbox
   cd libra-toolbox
   pip install -e .

To install the code alongside the optional dependencies for the neutronics module, first install `OpenMC <https://docs.openmc.org/en/stable/quickinstall.html>`_ with conda:

.. code-block:: bash

   conda install -c conda-forge openmc>=0.14.0

Then install the code with the optional dependencies:

.. code-block:: bash

   pip install libra-toolbox[neutronics]

To uninstall the package:

.. code-block:: bash

   pip uninstall libra-toolbox
