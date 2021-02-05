# External Imports
import numpy as np
import rasterio as rio
from typing import Optional, Dict
from copy import deepcopy


class Dataset:
    profile: rio.profiles.Profile
    bands: Dict[str, np.ndarray]
    meta: Optional[dict]

    def __init__(self, profile: rio.profiles.Profile, bands: Dict[str, np.ndarray], meta: Optional[dict]):
        """Instantiate a Dataset object

        :param profile: Profile of the dataset
        :param bands: A dictionary containing the band data associated with keys
        :param meta: (Optional) A dictionary containing metadata about the dataset
        """

        self.profile = profile
        self.bands = bands
        self.meta = meta

    def combine(self, dataset: object) -> object:
        """Combine this dataset with another compatible dataset

        This function simply checks for basic compatibility (resolution, array size,
        etc.) and then combines the list of bands.

        :param dataset: The dataset to combine with
        :return: This dataset with the new dataset added
        """

        # Check for compatibility
        # [TODO] Dataset combination checks need to be much more thorough
        if self.meta["resolution"] != dataset.meta["resolution"] or self.profile["height"] != dataset.profile["height"]:
            raise RuntimeError("Tried to combine two datasets that are not compatible!")

        # Actually copy over (deep copy, EXPENSIVE)
        self.bands.update(deepcopy(dataset.bands))
