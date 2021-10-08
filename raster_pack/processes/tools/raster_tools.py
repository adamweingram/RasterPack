# External Imports
import numpy as np
from typing import Optional


def normalize(array: np.ndarray, pre_low: np.int64, pre_high: np.int64, post_low: np.int64, post_high: np.int64,
              output_type: Optional[np.dtype] = np.float32, nodata_value: Optional[object] = None) -> np.ndarray:
    """Normalize an ndarray so every value is normalized to a given range

    :param array: Input ndarray to normalize
    :param pre_low: The lower bound of values in the input array
    :param pre_high: The upper bound of values in the input array
    :param post_low: The lower bound of values to scale to
    :param post_high: The upper bound of values to scale to
    :param output_type: (Optional) Data type of the output array
    :param nodata_value: (Optional) "Nodata" value that needs to remain consistent through calculation
    :return: The ndarray with each value normalized to the given post-range
    """

    # Check if types match
    matching_types = False
    if output_type != array.dtype:
        array = array.astype(output_type)
        matching_types = True

    # Create a binary mask of nodata value locations (if nodata is specified in arguments)
    nodata_mask = np.where(array.copy() == nodata_value, 1, 0)

    # Run linear interpolation
    interpolated = np.interp(array, (pre_low, pre_high), (post_low, post_high))

    # Create masked array
    masked_array = np.ma.array(interpolated, mask=nodata_mask, fill_value=nodata_value)

    # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
    output_array = masked_array.filled()

    # Return interpolated result
    return output_array if matching_types else output_array.astype(output_type)
