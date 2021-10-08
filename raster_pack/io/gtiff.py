# External Imports
import logging
from copy import deepcopy

import rasterio as rio
from rasterio import MemoryFile
from typing import Optional

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Setup Logger
logger = logging.getLogger("raster_pack.io.gtiff")


def create_dataset(path: str, datatype: Optional[object] = None) -> Dataset:
    """Create a dataset from a given GDAL-formatted SAFE subdataset path string

    :param path: Path of the GeoTIFF file
    :param datatype: Rasterio datatype to use
    :return: Dataset created from the GDAL-compatible dataset at the specified path
    """

    # Open GeoTIFF file for processing
    with rio.open(path) as dataset:

        # Display warning for user if a CRS is not detected in the source raster
        if dataset.crs is None:
            logger.warning("No CRS detected for input raster file! This may be an issue with the file or GDAL!")
            # raise GeospatialDataException("[ERROR] No CRS found! This may be due to an issue with GDAL!")

        # Create Dictionary to Store Data
        output_dict = {}

        # Get data using Rasterio
        for i, band_index in enumerate(dataset.indexes):

            # If there is no user-defined datatype, use the original dataset datatype
            datatype = dataset.dtypes[i] if datatype is None else datatype

            # Read from the dataset into the output dictionary
            output_dict["{}".format(i)] = dataset.read(band_index).astype(datatype)

        # Assemble metadata list
        profile = deepcopy(dataset.profile)
        meta = {}

        # Copy other relevant information to the profile
        profile.data["pixel_dimensions"] = dataset.res

        # Create and return new dataset
        return Dataset(profile=profile, bands=output_dict, meta=meta, nodata=dataset.nodata)


def output_gtiff(dataset: Dataset, output_path: str, datatype: Optional[str] = rio.float32,
                 compression: Optional[str] = None, interleaving: Optional[str] = 'band') -> None:
    """Output Dataset to a GeoTIFF file

    :param dataset: The dataset to be used to generate the GeoTIFF
    :param output_path: The path that the file will be written to
    :param datatype: (Optional) A rasterio datatype object representing the datatype to use when writing the file
    :param compression: (Optional) The compression algorithm to use. By default, no compression is used.
    :param interleaving: (Optional) Which interleaving method to use. Defaults to band-sequential.
    """

    # New instance of GDAL/Rasterio
    with rio.Env():
        # Write an array as a raster band to a new 8-bit file. For
        # the new file's profile, we start with the profile of the source
        # profile = src.profile

        # Update profile
        dataset.profile.update(
            driver="GTiff",
            interleave=interleaving,
            tiled=True,
            # compress='lzw',
            blockxsize=128,
            blockysize=128,
            # nodata=np.float32(0.0),
            dtype=datatype,
            count=len(dataset.bands)
        )
        if compression is not None:
            dataset.profile["compress"] = compression

        # Read each layer and write it to stack
        logger.debug("Started writing to file...")
        with rio.open(output_path, 'w', **dataset.profile) as dst:
            for ident, raw_data in enumerate(dataset.bands.values(), start=1):
                logger.debug("Writing {} as band {}".format(list(dataset.bands.keys())[ident-1], ident))
                dst.write_band(ident, raw_data.astype(datatype))

    logger.debug("Done writing to file.")


def memfile_gtiff(dataset: Dataset, datatype: Optional[str] = rio.float32) -> MemoryFile:
    """Output Dataset to a GeoTIFF MemoryFile

    :param dataset: The dataset to be used to generate the GeoTIFF MemoryFile
    :param datatype: (Optional) A rasterio datatype object representing the datatype to use when writing the file
    :return: A Rasterio MemoryFile
    """

    # New instance of GDAL/Rasterio
    with rio.Env():
        # Write an array as a raster band to a new 8-bit file. For
        # the new file's profile, we start with the profile of the source
        # profile = src.profile

        # Update profile
        dataset.profile.update(
            driver="GTiff",
            dtype=datatype,
            count=len(dataset.bands)
        )

        # Read each layer and write it to stack
        output = MemoryFile()
        with MemoryFile(output) as memfile:
            with memfile.open(**dataset.profile) as dst:
                for ident, raw_data in enumerate(dataset.bands.values(), start=1):
                    dst.write_band(ident, raw_data.astype(datatype))

    logger.debug("Done writing to MemoryFile.")
    return output
