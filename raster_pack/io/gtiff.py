# External Imports
import logging
import rasterio as rio
from rasterio import MemoryFile
from typing import Optional

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Setup Logger
logger = logging.getLogger("raster_pack.io.gtiff")


def output_gtiff(dataset: Dataset, output_path: str, datatype: Optional[str] = rio.float32) -> None:
    """Output Dataset to a GeoTIFF file

    :param dataset: The dataset to be used to generate the GeoTIFF
    :param output_path: The path that the file will be written to
    :param datatype: (Optional) A rasterio datatype object representing the datatype to use when writing the file
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
        logger.debug("Started writing to file...")
        with rio.open(output_path, 'w', **dataset.profile) as dst:
            for ident, raw_data in enumerate(dataset.bands.values(), start=1):
                dst.write_band(ident, raw_data.astype(datatype))
    logger.debug("Done writing to file.")


def memfile_gtiff(dataset: Dataset, datatype: Optional[str] = rio.float32) -> MemoryFile:
    """Output Dataset to a GeoTIFF MemoryFile

    :param dataset: The dataset to be used to generate the GeoTIFF MemoryFile
    :param datatype: (Optional) A rasterio datatype object representing the datatype to use when writing the file
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
