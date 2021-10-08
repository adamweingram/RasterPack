# External Imports
import logging
from collections import deque
from typing import Union

import numpy as np

# Set up Logger
logger = logging.getLogger("raster_pack.process.environmental_indexes.sentinel2_indices")


def calc_AWEInsh(band3: np.ndarray, band8: np.ndarray, band11: np.ndarray, band12: np.ndarray,
                 nan_value: Union[int, float, None] = np.nan):
    """Calculates AWEInsh given Sentinel-2 bands 3, 8, 11, and 12

    :param band3: Sentinel-2 Band 3
    :param band8: Sentinel-2 Band 8
    :param band11: Sentinel-2 Band 11
    :param band12: Sentinel-2 Band 12
    :param nan_value: (Optional) Value to replace numpy "NaN"s before returning
    :return: Single numpy array containing the calculated AWEInsh index
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(band3.copy() == nan_value, 1, 0),
        np.where(band8.copy() == nan_value, 1, 0),
        np.where(band11.copy() == nan_value, 1, 0),
        np.where(band12.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Convert all input numpy arrays to type float
    band3 = band3.astype(float)
    band8 = band8.astype(float)
    band11 = band11.astype(float)
    band12 = band12.astype(float)

    # Calculate
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (4 * (band3 - band11)) - ((0.25 * band8) + (2.75 * band12))
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_AWEIsh(band2: np.ndarray, band3: np.ndarray, band8: np.ndarray, band11: np.ndarray, band12: np.ndarray,
                nan_value: Union[int, float, None] = np.nan):
    """Calculates AWEIsh given Sentinel-2 bands 2, 3, 8, 11, and 12

    :param band2: Sentinel-2 Band 2
    :param band3: Sentinel-2 Band 3
    :param band8: Sentinel-2 Band 8
    :param band11: Sentinel-2 Band 11
    :param band12: Sentinel-2 Band 12
    :param nan_value: (Optional) Value to replace numpy "NaN"s before returning
    :return: Single numpy array containing the calculated AWEIsh index
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(band3.copy() == nan_value, 1, 0),
        np.where(band8.copy() == nan_value, 1, 0),
        np.where(band11.copy() == nan_value, 1, 0),
        np.where(band12.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Convert all input numpy arrays to type float
    band2 = band2.astype(float)
    band3 = band3.astype(float)
    band8 = band8.astype(float)
    band11 = band11.astype(float)
    band12 = band12.astype(float)

    # Calculate
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = band2 + (2.5 * band3) - (1.5 * (band8 + band11)) - (0.25 * band12)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array
