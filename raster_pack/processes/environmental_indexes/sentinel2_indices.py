# External Imports
import logging
import numpy as np

# Set up Logger
logger = logging.getLogger("raster_pack.process.environmental_indexes.sentinel2_indices")


def calc_AWEInsh(band3: np.ndarray, band8: np.ndarray, band11: np.ndarray, band12: np.ndarray):
    """Calculates AWEInsh given Sentinel-2 bands 3, 8, 11, and 12

    :param band3: Sentinel-2 Band 3
    :param band8: Sentinel-2 Band 8
    :param band11: Sentinel-2 Band 11
    :param band12: Sentinel-2 Band 12
    :return: Single numpy array containing the calculated AWEInsh index
    """

    # Convert all input numpy arrays to type float
    band3 = band3.astype(float)
    band8 = band8.astype(float)
    band11 = band11.astype(float)
    band12 = band12.astype(float)

    # Calculate and return
    return (4 * (band3 - band11)) - ((0.25 * band8) + (2.75 * band12))


def calc_AWEIsh(band2: np.ndarray, band3: np.ndarray, band8: np.ndarray, band11: np.ndarray, band12: np.ndarray):
    """Calculates AWEIsh given Sentinel-2 bands 2, 3, 8, 11, and 12

    :param band2: Sentinel-2 Band 2
    :param band3: Sentinel-2 Band 3
    :param band8: Sentinel-2 Band 8
    :param band11: Sentinel-2 Band 11
    :param band12: Sentinel-2 Band 12
    :return: Single numpy array containing the calculated AWEIsh index
    """

    # Convert all input numpy arrays to type float
    band2 = band2.astype(float)
    band3 = band3.astype(float)
    band8 = band8.astype(float)
    band11 = band11.astype(float)
    band12 = band12.astype(float)

    # Calculate and return
    return band2 + (2.5 * band3) - (1.5 * (band8 + band11)) - (0.25 * band12)
