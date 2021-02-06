# External Imports
import numpy as np
from typing import Optional


def normalize(array: np.ndarray, pre_low: np.int64, pre_high: np.int64, post_low: np.int64, post_high: np.int64,
              output_type: Optional[np.dtype] = np.float32) -> np.ndarray:
    """Normalize an ndarray so every value is normalized to a given range

    :param array: Input ndarray to normalize
    :param pre_low: The lower bound of values in the input array
    :param pre_high: The upper bound of values in the input array
    :param post_low: The lower bound of values to scale to
    :param post_high: The upper bound of values to scale to
    :param output_type: (Optional) Data type of the output array
    :return: The ndarray with each value normalized to the given post-range
    """

    # Run linear interpolation
    return np.interp(array.astype(output_type), (pre_low, pre_high), (post_low, post_high)).astype(output_type)
