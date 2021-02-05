# External Imports
import numpy as np
import rasterio as rio
from typing import Optional, Dict


class Dataset:
    profile: rio.profiles.Profile
    bands: Dict[str, np.ndarray]
    original_path: Optional[str]
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
