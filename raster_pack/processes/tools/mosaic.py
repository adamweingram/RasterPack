# External Imports
import time
import logging
import numpy as np
import rasterio as rio
from numba import njit

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Set up Logger
logger = logging.getLogger("raster_pack.tools.mosaic")


def merge(first: Dataset, second: Dataset) -> Dataset:
    # Verify correct conditions
    # [TODO] Create elegant failure conditions for incorrect inputs instead of AssertionErrors
    assert "crs" in first.profile.data.keys() and "crs" in second.profile.data.keys()
    assert first.profile.data["crs"] == second.profile.data["crs"]
    assert "transform" in first.profile.data.keys() and "transform" in second.profile.data.keys()
    assert len(first.bands) == len(second.bands)
    assert first.bands.keys() == second.bands.keys()

    # Merge each band
    # [TODO] Each band could easily be merged in parallel
    new_bands = {}
    output_transform = None
    last_band_key = None
    for band_key in first.bands.keys():
        logger.debug("Started merging for band: {}".format(band_key))
        start_time = time.time()
        merged = direct_merge(
            first_data=first.bands[band_key],
            first_transform=first.profile.data["transform"],
            second_data=second.bands[band_key],
            second_transform=second.profile.data["transform"]
        )

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
                 second_data: np.ndarray, second_transform: rio.transform) -> (np.ndarray, rio.transform):
    # Calculate pixel alignment offset for the inputs
    first_bounds = rio.transform.array_bounds(height=len(first_data[0]),
                                              width=len(first_data),
                                              transform=first_transform)

    second_bounds = rio.transform.array_bounds(height=len(second_data[0]),
                                               width=len(second_data),
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

    # [TODO] Derive width and height (in number of pixels) for the new raster
    # Note: Maybe use "res" value from original dataset info?
    new_pixel_width = 10  # [HACK] TEMPORARY!!!
    new_pixel_height = 10  # [HACK] TEMPORARY!!!

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
    # Calculate offset using top-left corner of the input array
    input_as_coordinate = dict(zip(
        ["xs", "ys"],
        rio.transform.xy(transform=input_transform, rows=0, cols=0, offset='center')
    ))

    offset = dict(zip(
        ["row", "col"],
        rio.transform.rowcol(transform=substrate_transform, xs=input_as_coordinate["xs"], ys=input_as_coordinate["ys"])
    ))

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
    # Overwrite substrate raster values with values from the input raster
    for row_num in range(0, len(input_array)):
        for col_num in range(0, len(input_array)):
            new_row = row_num + row_offset
            new_col = col_num + col_offset
            substrate_array[new_row][new_col] = input_array[row_num][col_num]

    return substrate_array
