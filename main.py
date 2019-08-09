import sys

import os
import zipfile
import re
import glob
import shutil

import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.plot import adjust_band

import numpy as np
import numpy.ma as ma
import affine

import utils
import colormaps
import band_math_definitions

np.seterr(divide="ignore", invalid="ignore")


def stack_bands(files):
    with rasterio.open(files[0]) as src:
        vrt_options = {
            "resampling": Resampling.nearest,
            "crs": src.crs,
            "transform": src.transform,
            "height": src.height,
            "width": src.width,
        }


    bands = []
    mask = None
    meta = None

    for path in files:
        with rasterio.open(path) as src:
            with WarpedVRT(src, **vrt_options) as vrt:
                meta = vrt.profile.copy()
                data = vrt.read()

                if mask is None:
                    mask = (data == 0)
                else:
                    mask = mask & (data == 0)

                bands.append(data[0].astype(np.float32))

    bands = [ma.masked_array(b, mask = mask) for b in bands]

    bands.insert(0, None)

    return bands, mask, meta



def calculate_indicies(bands, mask, meta, output_path):
    meta["driver"] = "GTiff"
    meta["dtype"] = rasterio.uint8
    meta["count"] = 1
    meta["nodata"] = 0


    for name, formula in band_math_definitions.INDICIES.items():
        with rasterio.open("%s/%s.tif"%(output_path, name), "w", **meta) as dst:
            image = formula(bands)

            image = utils.image_histogram_equalization(image)

            ma.set_fill_value(image, 0)
            dst.write(image.filled().astype(rasterio.uint8), 1)
            dst.write_colormap(1, colormaps.RAINBOW)


def extract_in_groups(data_path):
    output_path = "tmp/reflectance/"
    bands_grep = re.compile(".*Band\d(N|)\.tif$")

    archives = glob.glob(data_path + '*.zip')

    output = set()

    for z in archives:
        with zipfile.ZipFile(z, "r") as zip_ref:
            file_list = zip_ref.namelist()

            bands = filter(lambda x: bands_grep.search(x), file_list)

            for item in bands:
                directory = re.search('AST_07XT_(\d+)_.+', item).group(1)
                path = output_path + directory
                output.add(directory)
                zip_ref.extract(item, path=path)

    return output


for group in extract_in_groups("data/2019 Suzak/Reflectance/"):
    input_dir = "tmp/reflectance/%s"%(group)
    output_dir = "output/%s"%(group)


    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = [os.path.join(input_dir, f) for f in sorted(os.listdir(input_dir))]
    bands, mask, meta = stack_bands(files)
    print(f"Processing '{group}'...")
    calculate_indicies(bands, mask, meta, output_dir)
