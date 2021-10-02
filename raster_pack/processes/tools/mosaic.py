# External Imports
from typing import Tuple, Optional
import time
import logging
import numpy as np
import rasterio as rio
from numba import njit

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Set up Logger
logger = logging.getLogger("raster_pack.tools.mosaic")


def merge(first: Dataset, second: Dataset, reference: Optional[Dataset] = None) -> Dataset:
    """Merge two Dataset objects together (merge the rasters)

    The function will attempt to merge two Dataset objects and their corresponding rasters. The
    function will also attempt to merge metadata, though this is better done manually as some
    data will inevitably only apply to one Dataset or the other. **Spatial information like
    transform is preserved.**

    CAUTION: Will automatically use numpy's nan as a "nodata" value if the first Dataset object's "nodata" field is
    set to None! This may cause data loss if numpy.nan corresponds to a real value in your data!

    :param first: The first Dataset object
    :param second: The second Dataset object
    :param reference: (Optional) A dataset to use as a "reference" or "model" (for the extent/dimensions/etc.)
    :return: A new Dataset object that is the result of merging the two input Dataset objects
    """

    # Verify correct conditions
    # [TODO] Create elegant failure conditions for incorrect inputs instead of AssertionErrors
    assert "crs" in first.profile.data.keys() and "crs" in second.profile.data.keys()
    assert first.profile.data["crs"] == second.profile.data["crs"]
    assert "transform" in first.profile.data.keys() and "transform" in second.profile.data.keys()
    assert len(first.bands) == len(second.bands)
    assert first.bands.keys() == second.bands.keys()

    # Fix lacking "nodata" values
    first.nodata = np.nan if first.nodata is None else first.nodata
    second.nodata = np.nan if second.nodata is None else second.nodata

    # Merge each band
    # [TODO] Each band could easily be merged in parallel
    new_bands = {}
    output_transform = None
    last_band_key = None
    for band_key in first.bands.keys():
        logger.debug("Started merging for band: {}".format(band_key))
        start_time = time.time()

        # Modify non-matching nodata values
        # Note: By default, the first dataset's "nodata" will be used here
        if first.nodata != second.nodata:
            second_band_data = second.bands[band_key]
            np.where(second_band_data == second.nodata, first.nodata, second_band_data)

        # Actually perform merge
        merged = direct_merge(first_data=first.bands[band_key], first_transform=first.profile.data["transform"],
                              second_data=second.bands[band_key], second_transform=second.profile.data["transform"],
                              pixel_resolution=first.profile.data["pixel_dimensions"],
                              nodata_value=first.nodata)

        # "Merge" with model if provided
        if reference is not None:
            # Get the reference transform
            ref_profile = reference.profile.data

            # Get the reference band numpy array
            ref_key, ref_band_data = next(iter(reference.bands.items()))

            # Create a new substrate array
            nodata_array = np.ndarray(shape=ref_band_data.shape, dtype=ref_band_data.dtype)

            # Fill the new substrate array with nodata values
            nodata_array.fill(first.nodata)

            # Merge with nodata substrate array
            # [TODO] Find a way to reuse the already created "substrate" array rather than doubling memory usage
            merged = direct_merge(first_data=nodata_array, first_transform=ref_profile["transform"],
                                  second_data=merged[0], second_transform=merged[1],
                                  pixel_resolution=(first.profile.data["pixel_dimensions"]),
                                  nodata_value=first.nodata)
            del nodata_array

        new_bands[band_key] = merged[0]
        output_transform = merged[1]
        last_band_key = band_key
        logger.debug("Completed merging for band: {} in {} seconds".format(band_key, time.time() - start_time))

    # Create the profile for the output file by modifying the profile from the last band processed
    new_profile = first.profile
    new_profile.data["transform"] = output_transform
    new_profile.data["width"] = len(new_bands[last_band_key][0])
    new_profile.data["height"] = len(new_bands[last_band_key])
    new_profile.data["count"] = len(new_bands.keys())

    # [TODO] Implement proper metadata "diffing" for merge outputs
    return Dataset(profile=new_profile, bands=new_bands, nodata=first.nodata, meta=None, subdatasets=None)


def direct_merge(first_data: np.ndarray, first_transform: rio.transform,
                 second_data: np.ndarray, second_transform: rio.transform,
                 pixel_resolution: Tuple[int, int] = (10, 10),
                 nodata_value: Optional[object] = np.nan) -> (np.ndarray, rio.transform):
    """Directly merge two numpy ndarrays with associated spatial transforms

    :param first_data: Raw ndarray from the first dataset
    :param first_transform: Spatial transform from the first dataset
    :param second_data: Raw ndarray from the second dataset
    :param second_transform: Spatial transform from the second dataset
    :param pixel_resolution: The pixel resolution for both datasets given as a tuple
    :param nodata_value: The value to use to fill the "substrate" array
    :return: A tuple containing a raw combined ndarray and a combined spatial transform respectively
    """

    # Verify conditions
    assert nodata_value is not None

    # Calculate pixel alignment offset for the inputs
    first_bounds = rio.transform.array_bounds(height=len(first_data),
                                              width=len(first_data[0]),
                                              transform=first_transform)

    second_bounds = rio.transform.array_bounds(height=len(second_data),
                                               width=len(second_data[0]),
                                               transform=second_transform)

    # In format (West, South, East, North)
    # [TODO] Verify that comparison method of determining new bounds works for all coordinate systems/transforms
    new_bounds = dict(zip(
        ["west", "south", "east", "north"],
        [
            first_bounds[0] if first_bounds[0] <= second_bounds[0] else second_bounds[0],
            first_bounds[1] if first_bounds[1] <= second_bounds[1] else second_bounds[1],
            first_bounds[2] if first_bounds[2] >= second_bounds[2] else second_bounds[2],
            first_bounds[3] if first_bounds[3] >= second_bounds[3] else second_bounds[3]
        ]
    ))

    # Derive pixel dimensions for the new raster
    # Note: Maybe use "res" value from original dataset info?
    new_pixel_width = pixel_resolution[0]
    new_pixel_height = pixel_resolution[1]

    # Create transform from origin point and pixel size
    new_transform = rio.transform.from_origin(west=new_bounds["west"], north=new_bounds["north"], xsize=new_pixel_width,
                                              ysize=new_pixel_height)

    # Using the new reference transform, calculate the dimensions of output in number of pixels
    new_raster_dim = dict(zip(
        ["rows", "cols"],
        rio.transform.rowcol(transform=new_transform, xs=new_bounds["east"], ys=new_bounds["south"])
    ))

    # Create the new "substrate" array
    new_array = np.ndarray(shape=(new_raster_dim["rows"], new_raster_dim["cols"]), dtype=first_data.dtype)

    # Fill the substrate array with "nodata" (depending on what's defined)
    new_array.fill(nodata_value)

    # Write both datasets to the "substrate" array
    # [TODO] Overwrite method should be user-selectable (different methods for mosaic/merge, etc.)
    new_array = calc_offset_overwrite(input_array=first_data, input_transform=first_transform,
                                      substrate_array=new_array, substrate_transform=new_transform)

    new_array = calc_offset_overwrite(input_array=second_data, input_transform=second_transform,
                                      substrate_array=new_array, substrate_transform=new_transform)

    # Return the new data array as well as the calculated transform
    return new_array, new_transform


def calc_offset_overwrite(input_array: np.ndarray, input_transform: rio.transform,
                          substrate_array: np.ndarray, substrate_transform: rio.transform) -> np.ndarray:
    """A helper function to spatially overwrite a "substrate" array with an input array

    The function will automatically calculate the overlap using the array dimensions and each dataset's spatial
    transform. The **substrate array will be overwritten where overlap exists**.

    :param input_array: Raw ndarray to overwrite from
    :param input_transform: Spatial transform of the input dataset
    :param substrate_array: Raw ndarray to use as the "substrate" that will be written to
    :param substrate_transform: Spatial transform of the substrate dataset
    :return: A reference the the substrate array that has been partially overwritten
    """

    # Calculate offset using top-left corner of the input array
    input_as_coordinate = dict(zip(
        ["xs", "ys"],
        rio.transform.xy(transform=input_transform, rows=0, cols=0, offset='center')
    ))

    offset = dict(zip(
        ["row", "col"],
        rio.transform.rowcol(transform=substrate_transform, xs=input_as_coordinate["xs"], ys=input_as_coordinate["ys"])
    ))

    # Verify offsets won't result in segmentation faults
    assert offset["row"] + len(input_array) - 1 < len(substrate_array)
    assert offset["col"] + len(input_array[0]) - 1 < len(substrate_array[0])

    # Array operations performed in separate function for performance
    logger.debug("Starting overwrite of substrate array...")
    start_write_time = time.time()
    return_array = overwrite_with_offset(
        input_array=input_array,
        row_offset=offset["row"],
        col_offset=offset["col"],
        substrate_array=substrate_array
    )
    logger.debug("Overwrote offset array to substrate array in {} seconds".format(time.time() - start_write_time))
    return return_array


@njit
def overwrite_with_offset(input_array: np.ndarray, row_offset: int, col_offset: int,
                          substrate_array: np.ndarray) -> np.ndarray:
    """An efficiency-focused helper function to actually do overlap overwrite heavy-lifting

    :param input_array: Raw ndarray to get data from
    :param row_offset: The offset relative to the substrate array's start row
    :param col_offset: The offset relative to the substrate array's start column
    :param substrate_array: Raw ndarray to overwrite
    :return: A reference to the partially overwritten substrate array
    """

    # Overwrite substrate raster values with values from the input raster
    for row_num in range(0, len(input_array)):
        for col_num in range(0, len(input_array[0])):
            new_row = row_num + row_offset
            new_col = col_num + col_offset
            substrate_array[new_row][new_col] = input_array[row_num][col_num]

    return substrate_array
