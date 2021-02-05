# External Imports
import logging
import rasterio as rio
from typing import Optional, List
from copy import deepcopy

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Setup Logger
logger = logging.getLogger("raster_pack.io.safe")


def get_datasets(path: str) -> List[Dataset]:
    """Create a list of datasets from a given SAFE file

    :param path: The path the SAFE file is located at
    :return: A list of Dataset objects containing the data from the SAFE file
    """

    # Get Subdatasets as properly formatted path strings
    subdataset_paths = []
    with rio.open(path) as dataset:
        if dataset.subdatasets is not None and len(dataset.subdatasets) > 0:
            subdataset_paths = dataset.subdatasets
        else:
            raise RuntimeError("No subdatasets found in the given SAFE file!")

    # Create Dataset objects from subdatasets
    datasets = []
    for subdataset_path in subdataset_paths:
        new_dataset = create_dataset(subdataset_path)
        datasets.append(new_dataset)

    # Return loaded datasets
    return datasets


def create_dataset(path: str, datatype: Optional[object] = None) -> Dataset:
    """Create a dataset from a given GDAL-formatted SAFE subdataset path string

    :param path: GDAL-formatted subdataset path
    :param datatype: Rasterio datatype to use
    :return: Dataset created from the GDAL-compatible dataset at the specified path
    """

    # --[ Open Raster for Processing, Get Important Values ]--
    with rio.open(path) as dataset:

        # Display warning for user if a CRS is not detected in the source raster
        if dataset.crs is None:
            logger.warning("No CRS detected for input raster file! This may be an issue with the file or GDAL!")
            raise RuntimeError("[ERROR] No CRS found! This may be due to an issue with GDAL!")

        # Create Dictionary to Store Data
        output_dict = {}

        # Get data using Rasterio
        for i, band_index in enumerate(dataset.indexes):

            # If there is no user-defined datatype, use the original dataset datatype
            if datatype is None:
                datatype = dataset.dtypes[i]

            # Read from the dataset into the output dictionary
            output_dict["{}".format(band_index)] = dataset.read(band_index).astype(datatype)

        # Assemble metadata list
        meta = {
            "resolution": deepcopy(dataset.res)
        }
        profile = deepcopy(dataset.profile)

        # Create and return new dataset
        return Dataset(profile=profile, bands=output_dict, meta=meta)
