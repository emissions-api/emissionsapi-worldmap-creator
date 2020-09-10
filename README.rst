Emissions API World Map Creator
===============================

This project is a small command line tool to create beautiful world map images with data from the `Emissions API <https://emissions-api.org/>`_.

Like this one:

.. image:: example.png
  :width: 400
  :alt: https://github.com/emissions-api/emissionsapi-worldmap-creator/blob/master/example.png

Emissions API itself gives easy access to satellite-based emission data.
For more information take a look at our `website <https://emissions-api.org/>`_.

Installation
------------

Install the command line tool using::

    %> pip install emissionsapi-worldmap-creator

Example
-------

Generate an image with the ozone data from the forth of June (the image above):

.. code-block:: bash

    emissionsapi-worldmap-creator ozone 2020-06-04

To show all available options, run:

.. code-block:: bash

    emissionsapi-worldmap-creator --help
