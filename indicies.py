import affine
import numpy as np

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

bands = []
mask = None
meta = None

for path in input_files:
    with rasterio.open(path) as src:
        with WarpedVRT(src, **vrt_options) as vrt:
            meta = vrt.meta.copy()

            bands.append(vrt.read())

            if mask is None:
                mask = vrt.read_masks(1)
            else:
                mask = mask & vrt.read_masks(1)


meta["driver"] = "GTiff"

naip_ndvi = ((bands[3] - bands[0]) / (bands[3] + bands[0]) * 100).astype(np.int16)

with rasterio.open("stacked.tif", 'w', **meta) as dst:
    dst.write(naip_ndvi)
    dst.write_mask(mask)
