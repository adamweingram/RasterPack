# External Imports
import logging
import rasterio as rio

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Set up Logger
logger = logging.getLogger("raster_pack.tools.clip")


def crop_by_pixel(dataset: Dataset, row_start: int, row_end: int, col_start: int, col_end: int) -> Dataset:
    # Verify input conditions
    assert dataset.profile is not None
    assert dataset.profile.data is not None
    assert "transform" in dataset.profile.data.keys()
    assert "width" in dataset.profile.data.keys()
    assert "height" in dataset.profile.data.keys()
    assert "pixel_dimensions" in dataset.profile.data.keys()

    # Actually modify each band's data array
    for band_key, data_array in dataset.bands.items():
        # Use a range index to crop the array
        dataset.bands[band_key] = data_array[row_start:row_end, col_start:col_end]

    # Recalculate the transform
    new_origin_point = dict(zip(
        ["x_coord", "y_coord"],
        rio.transform.xy(
            transform=dataset.profile.data["transform"],
            rows=row_start,
            cols=col_start,
            offset="ul"
        )
    ))

    new_transform = rio.transform.from_origin(
        west=new_origin_point["x_coord"],
        north=new_origin_point["y_coord"],
        xsize=dataset.profile.data["pixel_dimensions"][0],
        ysize=dataset.profile.data["pixel_dimensions"][1]
    )

    # Change the profile
    new_profile = dataset.profile.data
    new_profile["width"] = col_end - col_start
    new_profile["height"] = row_end - row_start
    new_profile["transform"] = new_transform
    dataset.profile.data = new_profile

    # Return changed dataset
    return dataset
