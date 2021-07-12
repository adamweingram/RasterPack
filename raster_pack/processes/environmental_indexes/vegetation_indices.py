# External Imports
import logging
import numpy as np

# Set up Logger
logger = logging.getLogger("raster_pack.process.environmental_indexes.vegetation_indices")


# Vegetation Index Calculation Functions
def calc_ndvi(nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
    """Calculates the Normalized Difference Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :return: Single band containing NDVI
    """

    return (nir_band - red_band) / (nir_band + red_band)


def calc_ndavi(nir_band: np.ndarray, blue_band: np.ndarray) -> np.ndarray:
    """Calculates the Normalized Difference Aquatic Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param blue_band: Blue Band as a floating point type
    :return: Single band containing NDAVI
    """

    return (nir_band - blue_band) / (nir_band + blue_band)


def calc_wavi(nir_band: np.ndarray, blue_band: np.ndarray, L: float = 0.5) -> np.ndarray:
    """Calculates the Water Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param blue_band: Blue Band as a floating-point type
    :param L: (Optional) Correction factor
    :return: Single band containing WAVI
    """

    return (1 + L) * ((nir_band - blue_band) / (nir_band + blue_band + L))


def calc_savi(nir_band: np.ndarray, red_band: np.ndarray, L: float) -> np.ndarray:
    """Calculates the Soil Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param L: (Optional) Correction factor
    :return: Single band containing SAVI
    """

    return (1 + L) * ((nir_band - red_band) / (nir_band + red_band + L))


def calc_evi(
        nir_band: np.ndarray,
        red_band: np.ndarray,
        blue_band: np.ndarray,
        L: float = 1,
        gain: float = 2.5,
        c_1: float = 6,
        c_2: float = 7.5) -> np.ndarray:
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
    :return: Single band containing EVI
    """

    # Ignore Division by 0
    # [TODO] Check for issues with division by zero ignoring
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate EVI
    evi = gain * ((nir_band - red_band) / (nir_band + (c_1 * red_band) - (c_2 * blue_band) + L))

    return evi


def calc_evi2(nir_band: np.ndarray, red_band: np.ndarray, gain: float = 2.4, L: float = 1.0) -> np.ndarray:
    """Calculates the Enhanced Vegetation Index 2 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param red_band: Red Band as a floating-point type
    :param gain: (Optional) Gain
    :param L: (Optional) Correction factor
    :return: Single band containing EVI2
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate EVI2
    return gain * (nir_band - red_band) / (nir_band + red_band + L)


def calc_rendvi1(nir_band: np.ndarray, vr2: np.ndarray) -> np.ndarray:
    """Calculates the red edge NDVI1 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param vr2: [TODO] Write description of "VR2" band
    :return: Single band containing reNDVI1
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate reNDVI1
    return (nir_band - vr2) / (nir_band + vr2)


def calc_rendvi2(nir_band: np.ndarray, vr3: np.ndarray) -> np.ndarray:
    """Calculates the red edge NDVI2 for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param vr3: [TODO] Write description of "VR3" band
    :return: Single band containing reNDVI1
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate reNDVI2
    return (nir_band - vr3) / (nir_band + vr3)


def calc_ndwi(green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """Calculates the NDWI for two arrays

    :param green_band: Green Band as a floating-point type
    :param nir_band: Near Infrared Band as a floating-point type
    :return: Single band containing NDWI
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDWI
    return (green_band - nir_band) / (green_band + nir_band)


def calc_ndmi(nir_band: np.ndarray, swir_band: np.ndarray) -> np.ndarray:
    """Calculates the NDMI for two arrays

    :param nir_band: Near Infrared Band as a floating-point type
    :param swir_band: Short-Wave Infrared Band as a floating-point type
    :return: Single band containing NDMI
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDMI
    return (nir_band - swir_band) / (nir_band + swir_band)


def calc_mndwi(green_band: np.ndarray, swir_band: np.ndarray) -> np.ndarray:
    """Calculates the MNDWI for two arrays

    :param green_band: Green Band as a floating-point type
    :param swir_band: Short-Wave Infrared Band as a floating-point type
    :return: Single band containing MNDWI
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate MNDWI
    return (green_band - swir_band) / (green_band + swir_band)


def calc_mtci(vr1: np.ndarray, vr2: np.ndarray, red_band: np.ndarray) -> np.ndarray:
    """Calculates the MTCI for two arrays

    :param vr1: [TODO] Write description for "VR1" band
    :param vr2: [TODO] Write description for "VR2" band
    :param red_band: Red Band as a floating-point type
    :return: Single band containing MTCI
    """

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate MTCI
    return (vr2 - vr1)/(vr1 - red_band)
