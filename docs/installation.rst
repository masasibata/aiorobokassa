Installation
============

Requirements
------------

- Python 3.8 or higher
- aiohttp >= 3.8.0
- pydantic >= 2.0.0

Install from PyPI
------------------

The recommended way to install aiorobokassa is using pip:

.. code-block:: bash

   pip install aiorobokassa

Install from source
--------------------

To install from source, clone the repository and install using pip:

.. code-block:: bash

   git clone https://github.com/masasibata/aiorobokassa.git
   cd aiorobokassa
   pip install -e .

Install with development dependencies
-------------------------------------

To install with development dependencies (for testing and development):

.. code-block:: bash

   pip install aiorobokassa[dev]

Or using Poetry:

.. code-block:: bash

   poetry install --extras dev

Verify installation
--------------------

You can verify the installation by importing the library:

.. code-block:: python

   import aiorobokassa
   print(aiorobokassa.__version__)

