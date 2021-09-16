<div align="center">
    <h1>RasterPack</h1>
    <hr>
    A set of tools to designed to make processing raster data easier and faster
</div>

![screenshot of software](media/SoftwareScreenshot.png)

<p align="center">
    <a href="#key-features">Key Features</a> •
    <a href="#how-to-use">How to Use</a>
</p>

## Key Features

- Focus on in-memory operations
- Written in Python using [Numpy](https://numpy.org/), [RasterIO](https://github.com/mapbox/rasterio) and [GDAL](https://gdal.org/) packages
- Import/read-in many different types of satellite/raster imagery
- Run pre-processing steps on imagery in a common way
    - Vegetation indices
    - Resampling
    - Rescaling
    - Mosaicking (accelerated with [Numba](https://numba.pydata.org/))
- Write out results to disk
- Uses data structure that are compatible with other tools

## How to Use

The software is designed to be used in scripts or other processing chains, and is 
therefore distributed as a python package. The following sections contain instructions
for installing the package in an existing python environment.

### MacOS/Linux/Unix

```bash
git clone https://github.com/adamweingram/RasterPack.git RasterPack

pip3 install -e ./RasterPack
```
