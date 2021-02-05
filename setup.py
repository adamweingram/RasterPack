# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='raster_pack',
    version='0.0.1',
    description='A package for importing, manipulating, processing, and exporting raster data',
    author='Adam Weingram',
    author_email='aweingram@ucmerced.edu',
    url='https://github.com/adamweingram/RasterPack',
    packages=find_packages(exclude=('tests', 'docs'))
)
