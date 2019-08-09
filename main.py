import os

import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

import numpy as np
import numpy.ma as ma

import utils
import colormaps
import band_math_definitions
import source_indexer

np.seterr(divide="ignore", invalid="ignore")

def log(message):
    print(message)


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

        log(f"Reprojecting band {idx}: {path}")

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

def has_vnir(bands):
    return bands[1] is not None

def has_swir(bands):
    return bands[4] is not None

def has_tir(bands):
    return bands[10] is not None

def output_indicies(bands, indicies, meta, output_path):
    meta["driver"] = "GTiff"
    meta["dtype"] = rasterio.uint8
    meta["count"] = 1
    meta["nodata"] = 0

    for name, formula in indicies.items():
        image = formula(bands)

        image = utils.image_histogram_equalization(image)
        ma.set_fill_value(image, 0)

        store_as_geotiff(image, f"{output_path}/{name}.tif")

def process(bands, meta, output_path):
    if has_vnir(bands):
        log("Writing VNIR indicies...")
        output_indicies(bands, band_math_definitions.VNIR, meta, output_path)

    if has_swir(bands):
        log("Writing SWIR indicies...")
        output_indicies(bands, band_math_definitions.SWIR, meta, output_path)

    if has_tir(bands):
        log("Writing TIR indicies...")
        output_indicies(bands, band_math_definitions.TIR, meta, output_path)

    if has_vnir(bands) and has_tir(bands):
        log("Writing VNIR and SWIR indicies...")
        output_indicies(bands, band_math_definitions.VNIR_SWIR, meta, output_path)



for group, files in source_indexer.band_sources_in_groups().items():
    output_dir = "output/%s"%(group)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    log(f"Stacking '{group}'...")
    bands, meta = stack_bands(files)
    log(f"Processing '{group}'...")
    process(bands, meta, output_dir)
    log(f"Finished '{group}'")
