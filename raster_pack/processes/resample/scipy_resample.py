# External Imports
import logging
import numpy as np
from scipy.ndimage import zoom
from rasterio import Affine
from typing import Optional
from copy import deepcopy

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Setup Logger
logger = logging.getLogger("raster_pack.processes.resample.scipy_resample")


def scipy_resample(dataset: Dataset, target_resolution: float, resampling_method: Optional[str] = "nearest",
                   output_datatype: Optional[np.dtype] = np.float32) -> Dataset:
    """Resample a dataset to a target resolution

    NOTE: The dataset is PASS BY REFERENCE so the dataset you use with this function
    will be modified IN MEMORY!

    :param dataset: The dataset to resample
    :param target_resolution: The target resolution (in relative units: e.g. 10m -> 60m means you would enter 60)
    :param resampling_method: The scipy resampling method
    :param output_datatype: (Optional) Datatype to use for raster manipulation and output (DEFAULTS TO float32)
    :return: The resampled dataset (SEE NOTE! THIS IS A POINTER TO THE MODIFIED ORIGINAL!)
    """

    # Detect if resolution is not square
    if dataset.meta["resolution"][0] != dataset.meta["resolution"][1]:
        raise RuntimeError("Tried to resample a dataset that doesn't have a square resolution!")

    # Calculate scale factor
    scaling = int(dataset.meta["resolution"][0]) / float(target_resolution)

    # Calculate profile and transfer elements
    trans = deepcopy(dataset.profile["transform"])
    new_transform = Affine(trans.a / scaling, trans.b, trans.c, trans.d, trans.e / scaling, trans.f)
    new_height = dataset.profile["height"] * scaling
    new_width = dataset.profile["width"] * scaling
    new_resolution = (target_resolution, target_resolution)

    # Update profile to match output
    dataset.profile.update(
        res=(float(target_resolution), float(target_resolution)),
        transform=new_transform,
        height=new_height,
        width=new_width
    )
    dataset.meta["resolution"] = new_resolution

    # Change datatype of all bands
    for band_id, band_value in dataset.bands.items():
        dataset.bands[band_id] = band_value.astype(output_datatype)

    # Run resampling
    for key in dataset.bands.keys():
        dataset.bands[key] = zoom(input=dataset.bands[key], zoom=(scaling, scaling), order=0, mode=resampling_method)

    return dataset
