# External Imports
import logging
import re

import rasterio as rio
from typing import Optional, List
from copy import deepcopy
from datetime import datetime

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
            output_dict["{}".format(dataset.descriptions[i])] = dataset.read(band_index).astype(datatype)

        # Gather data from product name code
        # [FIXME] THE DATA GATHERING REGEX _IS NOT CORRECT_ FOR DATASETS FROM BEFORE 2016-12-06!!!
        name_butchered = re.search(
            pattern=r'S(?P<mission_id>[A-Z,0-9]{2})_MSI(?P<product_level>[A-Z,0-9]{3})_(?P<sensor_start_datetime>[0-9]{8}T[0-9]{6})_N(?P<processing_baseline_number>[0-9]{4})_R(?P<relative_orbit_number>[0-9]{3})_T(?P<tile_id>[A-Z,0-9]{5})_(?P<product_discriminator>[0-9]{8}T[0-9]{6}).SAFE',
            string=str(dataset.name)
        )

        # Assemble metadata list
        meta = {
            "date": datetime.strptime(name_butchered.group('sensor_start_datetime'), '%Y%m%dT%H%M%S'),  # Get only the date using a regex
            "resolution": deepcopy(dataset.res),
            "mission_id": str(name_butchered.group('mission_id')),
            "product_level": str(name_butchered.group('product_level')),
            "processing_baseline_number": str(name_butchered.group('processing_baseline_number')),
            "relative_orbit_number": str(name_butchered.group('relative_orbit_number')),
            "product_discriminator": str(name_butchered.group('product_discriminator'))
        }
        profile = deepcopy(dataset.profile)

        # Create and return new dataset
        return Dataset(profile=profile, bands=output_dict, meta=meta)
