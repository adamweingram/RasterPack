# External Imports
import logging
import numpy as np
from rasterio.transform import Affine
import rasterio.warp as rio_warp
from typing import Optional
from copy import deepcopy

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Setup Logger
logger = logging.getLogger("raster_pack.processes.resample.scipy_resample")


def rasterio_resample(dataset: Dataset, target_resolution: float, new_nodata: Optional[np.dtype] = None,
                      resampling_method: Optional[rio_warp.Resampling] = rio_warp.Resampling.nearest,
                      output_datatype: Optional[np.dtype] = np.float32) -> Dataset:
    """Resample a dataset to a target resolution

    NOTE: The dataset is PASS BY REFERENCE so the dataset you use with this function
    will be modified IN MEMORY!

    :param dataset: The dataset to resample
    :param target_resolution: The target resolution (in relative units: e.g. 10m -> 60m means you would enter 60)
    :param new_nodata: (Optional) The nodata type of the output dataset
    :param resampling_method: (Optional) The rasterio warp resampling method (Nearest Neighbor by default)
    :param output_datatype: (Optional) Datatype to use for raster manipulation and output (DEFAULTS TO float32)
    :return: The resampled dataset (SEE NOTE! THIS IS A POINTER TO THE MODIFIED ORIGINAL!)
    """

    # Detect if resolution is not square
    if dataset.meta["resolution"][0] != dataset.meta["resolution"][1]:
        raise RuntimeError("Tried to resample a dataset that doesn't have a square resolution!")

    # Calculate scale factor
    scaling = int(dataset.meta["resolution"][0]) / float(target_resolution)

    # Copy data from source Dataset
    source_crs = deepcopy(dataset.profile["crs"])
    source_transform = deepcopy(dataset.profile["transform"])
    source_nodata = dataset.profile["nodata"] if dataset.profile["nodata"] is not None else 0.0  # Must set nodata!

    # Calculate profile and transfer elements
    new_transform = Affine(source_transform.a / scaling, source_transform.b, source_transform.c, source_transform.d,
                           source_transform.e / scaling, source_transform.f)
    new_height = int(dataset.profile["height"] * scaling)
    new_width = int(dataset.profile["width"] * scaling)
    new_resolution = (target_resolution, target_resolution)
    new_nodata = source_nodata if new_nodata is None else new_nodata
    new_crs = source_crs    # [TODO] Add ability to change CRS in rasterio resample function

    # Update profile to match output
    dataset.profile.update(
        res=(float(target_resolution), float(target_resolution)),
        transform=new_transform,
        height=new_height,
        width=new_width,
        nodata=new_nodata
    )
    dataset.meta["resolution"] = new_resolution

    # Change datatype of all bands
    for band_id, band_value in dataset.bands.items():
        dataset.bands[band_id] = band_value.astype(output_datatype)

    # Run resampling
    for band_key, band_data in dataset.bands.items():
        # Create an array in the correct resampled dimensions
        resampled_array = np.ma.asanyarray(np.empty(shape=(new_width, new_height), dtype=output_datatype))

        # Resample/warp
        rio_warp.reproject(band_data, resampled_array, src_transform=source_transform, dst_transform=new_transform,
                           width=new_width, height=new_height, src_nodata=source_nodata, dst_nodata=new_nodata,
                           src_crs=source_crs, dst_crs=new_crs, resample=resampling_method)

        # Set value in dictionary
        dataset.bands[band_key] = resampled_array

    return dataset
