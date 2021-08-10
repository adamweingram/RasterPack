# External Imports
import gc
import logging
import math
from collections import ChainMap

import rasterio as rio
from rasterio.features import geometry_mask
from rasterio.transform import array_bounds
import fiona

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


def clip_number(n, min_num, max_num):
    return max(min(n, max_num), min_num)


def clip(dataset: Dataset, shapefile_path: str, crop: bool = False) -> Dataset:
    logger.debug("Got shapefile path: {}".format(shapefile_path))

    # Create ChainMap for preferences
    user_preferences = {
        "crop": crop
    }

    clip_preferences = dict(ChainMap({
        "all_touched": True,
        "invert": True,
        "crop": True,
        "pad_x": 0,
        "pad_y": 0,
        "pixel_precision": None,
        "quantize_op": math.ceil,
    }, user_preferences))

    # Open the shapefile
    with fiona.open(shapefile_path, "r") as shapefile:
        # Verify spatial compatibility
        assert dataset.profile.data['crs'].data['init'] == shapefile.crs['init']

        # Cache shapes
        shapes = [feature["geometry"] for feature in shapefile]

    # If enabled, crop output raster to extent of the shapefile
    if clip_preferences["crop"]:
        # Calculate the bounds for all the shapes
        shapes_bounds = [{
            "min_x": fiona.bounds(shape)[0],
            "min_y": fiona.bounds(shape)[1],
            "max_x": fiona.bounds(shape)[2],
            "max_y": fiona.bounds(shape)[3]
        } for shape in shapes]

        # Calculate Bounding Box
        dataset_bounding_box = array_bounds(
            height=dataset.profile.data["height"],
            width=dataset.profile.data["width"],
            transform=dataset.profile.data["transform"]
        )

        bounding_box = {
            "min_x": max(min([shape["min_x"] for shape in shapes_bounds]), dataset_bounding_box[0]),
            "min_y": max(min([shape["min_y"] for shape in shapes_bounds]), dataset_bounding_box[1]),
            "max_x": min(max([shape["max_x"] for shape in shapes_bounds]), dataset_bounding_box[2]),
            "max_y": min(max([shape["max_y"] for shape in shapes_bounds]), dataset_bounding_box[3]),
        }
        assert bounding_box["min_x"] < bounding_box["max_x"]
        assert bounding_box["min_y"] < bounding_box["max_y"]

        # Calculate pixel offsets
        calc_bounds = rio.transform.rowcol(
            transform=dataset.profile.data["transform"],
            xs=[bounding_box["min_x"], bounding_box["max_x"]],
            ys=[bounding_box["min_y"], bounding_box["max_y"]],
            op=math.floor,
            precision=None
        )

        array_offsets = {
            "min_row": calc_bounds[0][1],
            "min_col": calc_bounds[1][0],
            "max_row": calc_bounds[0][0],
            "max_col": calc_bounds[1][1]
        }
        del calc_bounds

        # Modify dataset using pixel cropping
        dataset = crop_by_pixel(
            dataset=dataset,
            row_start=array_offsets["min_row"],
            row_end=array_offsets["max_row"],
            col_start=array_offsets["min_col"],
            col_end=array_offsets["max_col"]
        )

    # Build a raster mask using the shapes and transform/dimension information from the raster Dataset object
    mask = geometry_mask(
        geometries=shapes,
        out_shape=(dataset.profile.data["height"], dataset.profile.data["width"]),
        transform=dataset.profile.data["transform"],
        all_touched=clip_preferences["all_touched"],
        invert=clip_preferences["invert"]
    )

    # Run mask operation on each band using binary mask
    for key, band in dataset.bands.items():
        dataset.bands[key] = band * mask
        del band

    # Delete mask array to reduce memory usage
    del mask
    gc.collect()  # [FIXME] Make sure mask array garbage collection call is properly executed for performance

    # Return dataset
    return dataset
