from __future__ import annotations

# External Imports
import numpy as np
import rasterio as rio
from typing import Optional, Dict, List
from copy import deepcopy


class Dataset:
    profile: rio.profiles.Profile
    bands: Dict[str, np.ndarray]
    nodata: Optional[object]
    meta: Optional[dict]
    subdatasets: Optional[List[Dataset]]

    def __init__(self, profile: rio.profiles.Profile, bands: Dict[str, np.ndarray], nodata: Optional[object] = None,
                 meta: Optional[dict] = None, subdatasets: Optional[List[Dataset]] = None):
        """Instantiate a Dataset object

        :param profile: Profile of the dataset
        :param bands: A dictionary containing the band data associated with keys
        :param nodata: The type/value used to denote no or invalid data
        :param meta: (Optional) A dictionary containing metadata about the dataset
        :param subdatasets: (Optional) A list containing additional subdataset Dataset objects
        """

        self.profile = profile
        self.bands = bands
        self.nodata = nodata
        self.meta = meta
        self.subdatasets = subdatasets

    def switch_nodata(self, new_nodata_value: object, recursive: bool = False) -> None:
        """Change nodata to a different value (modifies the array data!)

        :param new_nodata_value: The new value to use as nodata
        :param recursive: (Optional) Whether or not to run on subdatasets too
        """

        # Change for every band
        for band_key, band_data in self.bands.items():
            # Create a binary mask of nodata value locations (if nodata is specified in arguments)
            nodata_mask = np.where(band_data.copy() == self.nodata, 1, 0)

            # Create masked array
            masked_array = np.ma.array(band_data, mask=nodata_mask, fill_value=new_nodata_value)

            # Replace nodata values using MaskedArray filled method (uses mask to to insert nodata_value values)
            self.bands[band_key] = masked_array.filled()

        # If recursive, modify for subdatasets as well
        if recursive and self.subdatasets is not None:
            for subdataset in self.subdatasets:
                subdataset.switch_nodata(new_nodata_value=new_nodata_value, recursive=True)

        # Change nodata value property associated with self
        self.nodata = new_nodata_value

    def split_bands(self, band_ids: List[str]) -> Dataset:
        """Split off specific bands

        Split specified bands off into a separate Dataset object.

        :param band_ids: Keys corresponding to bands that should be split off
        :return: New Dataset object with the same profile and metadata containing only the specified bands
        """
        # Create a dict that will form the bands property of the new Dataset object
        bands_to_split = {band_key: self.bands[band_key] for band_key in band_ids}

        # Remove bands from this Dataset object that will be split off
        for band_key in band_ids:
            del self.bands[band_key]

        # Create a new Dataset object with similar settings (and new bands) and return
        return Dataset(
            profile=deepcopy(self.profile),
            bands=bands_to_split,
            nodata=deepcopy(self.nodata),
            meta=deepcopy(self.meta),
            subdatasets=None
        )


def combine(first: Dataset, second: Dataset, skip_duplicates: Optional[bool] = False, copy: bool = True) -> Dataset:
    """Combine one dataset with another compatible dataset

    This function simply checks for basic compatibility (resolution, array size,
    etc.) and then combines the list of bands. Also note that the function
    makes a deep copy of both datasets so a clean output can be created. This
    leads to a possible ballooning in memory!

    :param first: The dataset that the second will be combined into
    :param second: The dataset that will be combined with the first
    :param skip_duplicates: (Optional) Whether or not to skip duplicate bands (Default False)
    :param copy: (Optional) Whether or not to copy data or just use references (Default True = will copy)
    :return: This dataset with the new dataset added
    """

    # Combination with "None" should return the original
    if first is None:
        return second

    if second is None:
        return first

    # Check for compatibility
    # [TODO] Dataset combination checks need to be much more thorough
    # [FIXME] Current combine implementation doesn't actually catch different-dimension ndarrays!
    if first.meta["resolution"] != second.meta["resolution"] or \
            first.profile["crs"] != second.profile["crs"] or \
            first.profile["height"] != second.profile["height"] or \
            first.profile["width"] != second.profile["width"]:
        raise RuntimeError("Tried to combine two datasets that are not compatible!")

    # Create a deep copy of datasets (Caution, EXPENSIVE if copy is set!)
    first_bands = deepcopy(first.bands) if copy else first.bands
    second_bands = deepcopy(second.bands) if copy else second.bands

    # Test for bands with the same name to avoid overwriting data
    # If the user wants to skip duplicates, remove the duplicate entry from the second
    # band dictionary.
    for key in first_bands.keys():
        if key in second_bands.keys():
            if not skip_duplicates:
                raise RuntimeError("Tried to combine two datasets with matching band keys!")
            else:
                del second_bands[key]

    # Actually copy over
    first.bands = {**first_bands, **second_bands}

    # Create a deep copy of all the subdatasets if specified (Caution, potentially EXTREMELY EXPENSIVE!)
    if first.subdatasets is not None:
        first_subdatasets = deepcopy(first.subdatasets) if copy is not None else first.subdatasets
    else:
        first_subdatasets = {}

    if second.subdatasets is not None:
        second_subdatasets = deepcopy(second.subdatasets) if copy is not None else second.subdatasets
    else:
        second_subdatasets = {}

    # Combine list of subdatasets
    first.subdatasets = {**first_subdatasets, **second_subdatasets}

    # Return the first dataset with the second copied into it
    return first
