# External Imports
import logging
from collections import deque
from typing import Union
from functools import reduce

import numpy as np

# Set up Logger
logger = logging.getLogger("raster_pack.process.environmental_indexes.vegetation_indices")


# Vegetation Index Calculation Functions
def calc_ndvi(nir_band: np.ndarray, red_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Normalized Difference Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing NDVI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(red_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run NDVI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (nir_band - red_band) / (nir_band + red_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_ndavi(nir_band: np.ndarray, blue_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Normalized Difference Aquatic Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param blue_band: Blue Band as a floating point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing NDAVI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(blue_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run NDAVI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (nir_band - blue_band) / (nir_band + blue_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_wavi(nir_band: np.ndarray, blue_band: np.ndarray, L: float = 0.5, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Water Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param blue_band: Blue Band as a floating-point type
    :param L: (Optional) Correction factor
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing WAVI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(blue_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run WAVI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (1 + L) * ((nir_band - blue_band) / (nir_band + blue_band + L))
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_savi(nir_band: np.ndarray, red_band: np.ndarray, L: float, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Soil Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param L: (Optional) Correction factor
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing SAVI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(red_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run SAVI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (1 + L) * ((nir_band - red_band) / (nir_band + red_band + L))
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_evi(
        nir_band: np.ndarray,
        red_band: np.ndarray,
        blue_band: np.ndarray,
        L: float = 1,
        gain: float = 2.5,
        c_1: float = 6,
        c_2: float = 7.5,
        nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Enhanced Vegetation Index for two arrays

    The default values for Sentinel-2 are: gain = 2.5, c_1 = 6.0, c_2 = 7.5, L = 1.0.

    Reference: https://github.com/sentinel-hub/custom-scripts/blob/master/sentinel-2/evi/script.js

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param blue_band: Blue Band as a floating-point type
    :param L: (Optional) Correction factor
    :param gain: (Optional) Gain
    :param c_1: (Optional) Coefficient 1
    :param c_2: (Optional) Coefficient 2
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing EVI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(red_band.copy() == nan_value, 1, 0),
        np.where(blue_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run EVI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = gain * ((nir_band - red_band) / (nir_band + (c_1 * red_band) - (c_2 * blue_band) + L))
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_evi2(nir_band: np.ndarray, red_band: np.ndarray, gain: float = 2.4, L: float = 1.0, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the Enhanced Vegetation Index 2 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param gain: (Optional) Gain
    :param L: (Optional) Correction factor
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing EVI2
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(red_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run EVI2 calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = gain * (nir_band - red_band) / (nir_band + red_band + L)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_rendvi1(nir_band: np.ndarray, vr2: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the red edge NDVI1 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param vr2: [TODO] Write description of "VR2" band
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing reNDVI1
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(vr2.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run reNDVI1 calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (nir_band - vr2) / (nir_band + vr2)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_rendvi2(nir_band: np.ndarray, vr3: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the red edge NDVI2 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param vr3: [TODO] Write description of "VR3" band
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing reNDVI1
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(vr3.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run reNDVI2 calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (nir_band - vr3) / (nir_band + vr3)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_ndwi(green_band: np.ndarray, nir_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the NDWI for two arrays

    :param green_band: Green Band as a floating-point type
    :param nir_band: Near Infrared Band as a floating-point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing NDWI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(green_band.copy() == nan_value, 1, 0),
        np.where(nir_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run NDWI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (green_band - nir_band) / (green_band + nir_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_ndmi(nir_band: np.ndarray, swir_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the NDMI for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param swir_band: Short-Wave Infrared Band as a floating-point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing NDMI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(nir_band.copy() == nan_value, 1, 0),
        np.where(swir_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run NDMI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (nir_band - swir_band) / (nir_band + swir_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_mndwi(green_band: np.ndarray, swir_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the MNDWI for two arrays

    :param green_band: Green Band as a floating-point type
    :param swir_band: Short-Wave Infrared Band as a floating-point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing MNDWI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(green_band.copy() == nan_value, 1, 0),
        np.where(swir_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run MNDWI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (green_band - swir_band) / (green_band + swir_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array


def calc_mtci(vr1: np.ndarray, vr2: np.ndarray, red_band: np.ndarray, nan_value: Union[int, float, None] = np.nan) -> np.ndarray:
    """Calculates the MTCI for two arrays

    :param vr1: [TODO] Write description for "VR1" band
    :param vr2: [TODO] Write description for "VR2" band
    :param red_band: Red Band as a floating-point type
    :param nan_value: (Optional) Nodata value to use (ALSO replaces numpy "NaN"s in the array before returning)
    :return: Single band containing MTCI
    """

    # Create a binary masks of nodata value locations (if nodata is specified in arguments)
    masks = deque([
        np.where(vr1.copy() == nan_value, 1, 0),
        np.where(vr2.copy() == nan_value, 1, 0),
        np.where(red_band.copy() == nan_value, 1, 0),
    ])

    # Merge down into a single nodata mask with all the nodata values mapped
    full_mask = masks.pop()
    while masks:
        full_mask = np.logical_and(full_mask, masks.pop())

    # Remove reference to now empty deque
    del masks

    # Run MTCI calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        calc = (vr2 - vr1) / (vr1 - red_band)
        calc = np.nan_to_num(calc, copy=False, nan=nan_value, posinf=nan_value, neginf=nan_value)

    # Create masked array
    masked_calc = np.ma.array(calc, mask=full_mask, fill_value=nan_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_calc.filled()

    return output_array
