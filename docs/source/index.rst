RasterPack Python Module
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Overview
========

A quick overview of the components and tools available:

.. image:: ./_static/RasterPack-Overview.png

Key Features
------------
- Focus on in-memory operations
- Written in Python using `Numpy <https://numpy.org/>`_, `RasterIO <https://github.com/mapbox/rasterio>`_ and `GDAL <https://gdal.org/>`_ packages
- Import/read-in many different types of satellite/raster imagery
- Run pre-processing steps on imagery in a common way
    - Vegetation indices
    - Resampling
    - Rescaling
    - Mosaicking (accelerated with `Numba <https://numba.pydata.org/>`_)
- Write out results to disk
- Uses data structure that are compatible with other tools
