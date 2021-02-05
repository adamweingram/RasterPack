# External Imports
import logging
import numpy as np

# Set up Logger
logger = logging.getLogger("raster_pack.process.environmental_indexes.vegetation_indices")


# Vegetation Index Calculation Functions
def calc_ndvi(nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
    """Calculates the Normalized Difference Vegetation Index for two arrays

    :param nir_band: Near Infrared Band
    :param red_band: Red Band
    :return: Single band containing NDVI
    """

    nir_band = nir_band.astype(float)
    red_band = red_band.astype(float)

    return (nir_band - red_band) / (nir_band + red_band)


def calc_ndavi(nir_band: np.ndarray, blue_band: np.ndarray) -> np.ndarray:
    """Calculates the Normalized Difference Aquatic Vegetation Index for two arrays

    :param nir_band: Near Infrared Band
    :param blue_band: Blue Band
    :return: Single band containing NDAVI
    """

    nir_band = nir_band.astype(float)
    blue_band = blue_band.astype(float)

    return (nir_band - blue_band) / (nir_band + blue_band)


def calc_wavi(nir_band: np.ndarray, blue_band: np.ndarray, L: float = 0.5) -> np.ndarray:
    """Calculates the Water Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band
    :param blue_band: Blue Band
    :param L: (Optional) Correction factor
    :return: Single band containing WAVI
    """

    nir_band = nir_band.astype(float) / 1000
    blue_band = blue_band.astype(float) / 1000

    return (1 + L) * ((nir_band - blue_band) / (nir_band + blue_band + L))


def calc_savi(nir_band: np.ndarray, red_band: np.ndarray, L: float) -> np.ndarray:
    """Calculates the Soil Adjusted Vegetation Index for two arrays

    :param nir_band: Near Infrared Band
    :param red_band: Red Band
    :param L: (Optional) Correction factor
    :return: Single band containing SAVI
    """

    nir_band = nir_band.astype(float)
    red_band = red_band.astype(float)

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

    :param nir_band: Near Infrared Band
    :param red_band: Red Band
    :param blue_band: Blue Band
    :param L: (Optional) Correction factor
    :param gain: (Optional) Gain
    :param c_1: (Optional) Coefficient 1
    :param c_2: (Optional) Coefficient 2
    :return: Single band containing EVI
    """

    # Change type to float
    nir_band = nir_band.astype(float) / 1000
    red_band = red_band.astype(float) / 1000
    blue_band = blue_band.astype(float) / 1000

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate EVI
    evi = gain * ((nir_band - red_band) / (nir_band + (c_1 * red_band) - (c_2 * blue_band) + L))

    return evi


def calc_evi2(nir_band: np.ndarray, red_band: np.ndarray, gain: float = 2.4, L: float = 1.0) -> np.ndarray:
    """Calculates the Enhanced Vegetation Index 2 for two arrays

    :param nir_band: Near Infrared Band
    :param red_band: Red Band
    :param gain: (Optional) Gain
    :param L: (Optional) Correction factor
    :return: Single band containing EVI2
    """

    # Change type to float
    nir_band = nir_band.astype(float)
    red_band = red_band.astype(float)

    # Ignore Division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate EVI2
    return gain * (nir_band - red_band) / (nir_band + red_band + L)
