import os
import zipfile
import re
import glob

import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from collections import defaultdict

import numpy as np
import numpy.ma as ma

import utils
import colormaps
import band_math_definitions

np.seterr(divide="ignore", invalid="ignore")


def stack_bands(band_refs):
    keys = sorted(band_refs.keys())

    with rasterio.open(band_refs[keys[1]]) as src:
        vrt_options = {
            "resampling": Resampling.nearest,
            "crs": src.crs,
            "transform": src.transform,
            "height": src.height,
            "width": src.width,
        }


    bands = [None]*15
    mask = None
    meta = None

    for idx in keys:
        path = band_refs[idx]

        print(f"Reprojecting band {idx}: {path}")

        with rasterio.open(path) as src:
            with WarpedVRT(src, **vrt_options) as vrt:
                meta = vrt.profile.copy()
                data = vrt.read()

                if mask is None:
                    mask = (data == 0)
                else:
                    mask = mask & (data == 0)

                bands[idx] = data[0].astype(np.float32)

    bands = [ma.masked_array(b, mask = mask) if b is not None else None for b in bands]

    return bands, meta


def store_as_geotiff(image, path, dtype=rasterio.uint8, colormap = colormaps.RAINBOW):
    meta["driver"] = "GTiff"
    meta["dtype"] = dtype
    meta["count"] = 1
    meta["nodata"] = 0

    with rasterio.open(path, "w", **meta) as dst:
        dst.write(image.filled().astype(dtype), 1)
        dst.write_colormap(1, colormap)

def output_indicies(bands, meta, output_path):
    meta["driver"] = "GTiff"
    meta["dtype"] = rasterio.uint8
    meta["count"] = 1
    meta["nodata"] = 0

    for name, formula in band_math_definitions.INDICIES.items():
        image = formula(bands)

        image = utils.image_histogram_equalization(image)
        ma.set_fill_value(image, 0)

        store_as_geotiff(image, f"{output_path}/{name}.tif")


def all_VNIR_SWIR():
    return glob.glob("./data/**/AST_07XT_*.zip", recursive=True)

def all_TIR():
    return glob.glob("./data/**/AST_05_*.zip", recursive=True)


def band_sources_in_groups():
    group_name_grep = re.compile("AST_[^_]+_(\d+)_.+")
    band_number_grep = re.compile(".*Band(\d+)(N|)\.tif$")

    groups = defaultdict(dict)

    for z in all_VNIR_SWIR() + all_TIR():
        with zipfile.ZipFile(z, "r") as zip_ref:
            all_files = sorted(zip_ref.namelist())
            relevant_files = filter(lambda x: band_number_grep.search(x), all_files)

            for file in relevant_files:
                group = group_name_grep.search(file).group(1)
                band = band_number_grep.search(file).group(1)
                value = f"zip:{z}!{file}"

                groups[group][int(band)] = value

    return groups


for group, files in band_sources_in_groups().items():
    output_dir = "output/%s"%(group)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print(f"Stacking '{group}'...")
    bands, meta = stack_bands(files)
    print(f"Processing '{group}'...")
    output_indicies(bands, meta, output_dir)
    print(f"Finished '{group}'")
