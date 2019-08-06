from scipy import stats
import numpy as np

import affine

import gdal

import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

import matplotlib as mpl


input_files = (
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061316_8698/AST_07XT_00305152002062311_20190805061316_8698.SurfaceReflectanceVNIR.Band1.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061316_8698/AST_07XT_00305152002062311_20190805061316_8698.SurfaceReflectanceVNIR.Band2.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061316_8698/AST_07XT_00305152002062311_20190805061316_8698.SurfaceReflectanceVNIR.Band3N.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band4.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band5.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band6.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band7.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band8.tif",
    "data/2019 Suzak/Reflectance Tiff/AST_07XT_00305152002062311_20190805061317_8698/AST_07XT_00305152002062311_20190805061317_8698.SurfaceReflectanceSWIR.Band9.tif",
)

np.seterr(divide='ignore', invalid='ignore')

with rasterio.open(input_files[0]) as src:
    dst_bounds = src.bounds
    dst_height = src.height
    dst_width = src.width
    dst_crs = src.crs
    dst_transform = src.transform


vrt_options = {
    'resampling': Resampling.nearest,
    'crs': dst_crs,
    'transform': dst_transform,
    'height': dst_height,
    'width': dst_width,
    'nodata': 0
}

bands = [None]
mask = None
meta = None

for path in input_files:
    with rasterio.open(path) as src:
        with WarpedVRT(src, **vrt_options) as vrt:
            meta = vrt.meta.copy()
            data = vrt.read()

            bands.append(data.astype(np.float32))

            if mask is None:
                mask = vrt.read_masks(1)
            else:
                mask = mask & vrt.read_masks(1)

indicies = {
    # Iron
    "Fe3p": lambda bands: bands[2] / bands[1],
    "Fe2p": lambda bands: (bands[5] / bands[3] + bands[1] / bands[2]),
    "Laterite": lambda bands: bands[4] / bands[5],
    "Gossan": lambda bands: bands[4] / bands[2],
    "Ferrous silicates": lambda bands: bands[5] / bands[4] ,
    "Ferric oxides": lambda bands: bands[4] / bands[3],
    # Other
    "NDVI": lambda bands: (bands[3] - bands[2]) / (bands[3] + bands[2]),
}

meta["driver"] = "GTiff"

meta["dtype"] = rasterio.float32
meta["count"] = 1

for name, formula in indicies.items():
    with rasterio.open("output/%s.tif"%(name), "w", **meta) as dst:
        dst.write(formula(bands).astype(rasterio.float32))
        dst.write_mask(mask)
