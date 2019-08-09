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

np.seterr(divide="ignore", invalid="ignore")
COLORMAP = {0: (0, 0, 0), 1: (3, 0, 2), 2: (8, 0, 6), 3: (12, 0, 9), 4: (17, 0, 13), 5: (21, 0, 18), 6: (26, 0, 22), 7: (30, 0, 27), 8: (35, 0, 31), 9: (39, 0, 37), 10: (44, 0, 42), 11: (49, 0, 47), 12: (53, 0, 52), 13: (57, 0, 58), 14: (60, 0, 62), 15: (63, 0, 67), 16: (67, 0, 71), 17: (68, 0, 76), 18: (71, 0, 80), 19: (73, 0, 85), 20: (76, 0, 90), 21: (78, 0, 94), 22: (79, 0, 99), 23: (81, 0, 103), 24: (82, 0, 108), 25: (84, 0, 112), 26: (83, 0, 117), 27: (85, 0, 121), 28: (86, 0, 126), 29: (87, 0, 131), 30: (85, 0, 135), 31: (86, 0, 140), 32: (86, 0, 144), 33: (86, 0, 149), 34: (84, 0, 153), 35: (83, 0, 158), 36: (83, 0, 162), 37: (83, 0, 167), 38: (82, 0, 172), 39: (78, 0, 176), 40: (77, 0, 181), 41: (76, 0, 185), 42: (75, 0, 190), 43: (70, 0, 194), 44: (69, 0, 199), 45: (67, 0, 203), 46: (65, 0, 208), 47: (59, 0, 213), 48: (57, 0, 217), 49: (54, 0, 222), 50: (52, 0, 226), 51: (45, 0, 231), 52: (42, 0, 235), 53: (39, 0, 240), 54: (35, 0, 244), 55: (32, 0, 249), 56: (24, 0, 254), 57: (20, 0, 254), 58: (15, 0, 254), 59: (11, 0, 254), 60: (3, 0, 254), 61: (0, 0, 254), 62: (0, 3, 254), 63: (0, 7, 254), 64: (0, 15, 254), 65: (0, 20, 254), 66: (0, 24, 254), 67: (0, 28, 254), 68: (0, 37, 254), 69: (0, 41, 254), 70: (0, 45, 254), 71: (0, 50, 254), 72: (0, 54, 254), 73: (0, 62, 254), 74: (0, 66, 254), 75: (0, 71, 254), 76: (0, 75, 254), 77: (0, 83, 254), 78: (0, 88, 254), 79: (0, 92, 254), 80: (0, 96, 254), 81: (0, 105, 254), 82: (0, 109, 254), 83: (0, 113, 254), 84: (0, 118, 254), 85: (0, 126, 254), 86: (0, 130, 254), 87: (0, 134, 254), 88: (0, 139, 254), 89: (0, 143, 254), 90: (0, 151, 254), 91: (0, 156, 254), 92: (0, 160, 254), 93: (0, 164, 254), 94: (0, 173, 254), 95: (0, 177, 254), 96: (0, 181, 254), 97: (0, 186, 254), 98: (0, 194, 254), 99: (0, 198, 254), 100: (0, 202, 254), 101: (0, 207, 254), 102: (0, 215, 254), 103: (0, 219, 254), 104: (0, 224, 254), 105: (0, 228, 254), 106: (0, 232, 254), 107: (0, 241, 254), 108: (0, 245, 254), 109: (0, 249, 254), 110: (0, 254, 254), 111: (0, 254, 245), 112: (0, 254, 241), 113: (0, 254, 237), 114: (0, 254, 232), 115: (0, 254, 224), 116: (0, 254, 219), 117: (0, 254, 215), 118: (0, 254, 211), 119: (0, 254, 202), 120: (0, 254, 198), 121: (0, 254, 194), 122: (0, 254, 190), 123: (0, 254, 186), 124: (0, 254, 177), 125: (0, 254, 173), 126: (0, 254, 169), 127: (0, 254, 164), 128: (0, 254, 156), 129: (0, 254, 151), 130: (0, 254, 147), 131: (0, 254, 143), 132: (0, 254, 134), 133: (0, 254, 130), 134: (0, 254, 126), 135: (0, 254, 122), 136: (0, 254, 113), 137: (0, 254, 109), 138: (0, 254, 105), 139: (0, 254, 101), 140: (0, 254, 96), 141: (0, 254, 88), 142: (0, 254, 83), 143: (0, 254, 79), 144: (0, 254, 75), 145: (0, 254, 66), 146: (0, 254, 62), 147: (0, 254, 58), 148: (0, 254, 54), 149: (0, 254, 45), 150: (0, 254, 41), 151: (0, 254, 37), 152: (0, 254, 33), 153: (0, 254, 24), 154: (0, 254, 20), 155: (0, 254, 15), 156: (0, 254, 11), 157: (0, 254, 7), 158: (0, 254, 0), 159: (3, 254, 0), 160: (7, 254, 0), 161: (11, 254, 0), 162: (20, 254, 0), 163: (24, 254, 0), 164: (28, 254, 0), 165: (32, 254, 0), 166: (41, 254, 0), 167: (45, 254, 0), 168: (50, 254, 0), 169: (54, 254, 0), 170: (62, 254, 0), 171: (66, 254, 0), 172: (71, 254, 0), 173: (75, 254, 0), 174: (79, 254, 0), 175: (88, 254, 0), 176: (92, 254, 0), 177: (96, 254, 0), 178: (100, 254, 0), 179: (109, 254, 0), 180: (113, 254, 0), 181: (118, 254, 0), 182: (122, 254, 0), 183: (130, 254, 0), 184: (134, 254, 0), 185: (139, 254, 0), 186: (143, 254, 0), 187: (152, 254, 0), 188: (156, 254, 0), 189: (160, 254, 0), 190: (164, 254, 0), 191: (168, 254, 0), 192: (177, 254, 0), 193: (181, 254, 0), 194: (186, 254, 0), 195: (190, 254, 0), 196: (198, 254, 0), 197: (202, 254, 0), 198: (207, 254, 0), 199: (211, 254, 0), 200: (220, 254, 0), 201: (224, 254, 0), 202: (228, 254, 0), 203: (232, 254, 0), 204: (241, 254, 0), 205: (245, 254, 0), 206: (249, 254, 0), 207: (254, 254, 0), 208: (254, 249, 0), 209: (254, 241, 0), 210: (254, 237, 0), 211: (254, 232, 0), 212: (254, 228, 0), 213: (254, 220, 0), 214: (254, 215, 0), 215: (254, 211, 0), 216: (254, 207, 0), 217: (254, 198, 0), 218: (254, 194, 0), 219: (254, 190, 0), 220: (254, 186, 0), 221: (254, 177, 0), 222: (254, 173, 0), 223: (254, 169, 0), 224: (254, 164, 0), 225: (254, 160, 0), 226: (254, 152, 0), 227: (254, 147, 0), 228: (254, 143, 0), 229: (254, 139, 0), 230: (254, 130, 0), 231: (254, 126, 0), 232: (254, 122, 0), 233: (254, 118, 0), 234: (254, 109, 0), 235: (254, 105, 0), 236: (254, 101, 0), 237: (254, 96, 0), 238: (254, 88, 0), 239: (254, 84, 0), 240: (254, 79, 0), 241: (254, 75, 0), 242: (254, 71, 0), 243: (254, 62, 0), 244: (254, 58, 0), 245: (254, 54, 0), 246: (254, 50, 0), 247: (254, 41, 0), 248: (254, 37, 0), 249: (254, 33, 0), 250: (254, 28, 0), 251: (254, 20, 0), 252: (254, 16, 0), 253: (254, 11, 0), 254: (254, 7, 0), 255: (254, 0, 0)}


def prepare_bands(files):
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

def image_histogram_equalization(image, number_bins=256):
    image_histogram, bins = np.histogram(image.flatten(), number_bins, density=True)
    cdf = image_histogram.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize

    # use linear interpolation of cdf to find new pixel values
    # TODO should it be better nearest neighbour?
    image_equalized = np.interp(image.flatten(), bins[:-1], cdf)

    return ma.masked_array(image_equalized.reshape(image.shape), mask = image.mask)


def calculate_indicies(bands, mask, meta, output_path):
    indicies = {
        # Iron
        "Fe3p": lambda bands: np.true_divide(bands[2], bands[1]),
        "Fe2p": lambda bands: np.true_divide(bands[5], bands[3]) + np.true_divide(bands[1], bands[2]),
        "Laterite": lambda bands: np.true_divide(bands[4], bands[5]),
        "Gossan": lambda bands: np.true_divide(bands[4], bands[2]),
        "Ferrous silicates": lambda bands: np.true_divide(bands[5], bands[4]),
        "Ferric oxides": lambda bands: np.true_divide(bands[4], bands[3]),
        # Other
        "NDVI": lambda bands: np.true_divide((bands[3] - bands[2]), (bands[3] + bands[2])),
    }

    meta["driver"] = "GTiff"
    meta["dtype"] = rasterio.uint8
    meta["count"] = 1
    meta["nodata"] = 0


    for name, formula in indicies.items():
        with rasterio.open("%s/%s.tif"%(output_path, name), "w", **meta) as dst:
            image = formula(bands)

            image = image_histogram_equalization(image)

            ma.set_fill_value(image, 0)
            dst.write(image.filled().astype(rasterio.uint8), 1)
            dst.write_colormap(1, COLORMAP)


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


for group in extract_in_groups("data/2019 Suzak/Reflectance Tiff/"):
    input_dir = "tmp/reflectance/%s"%(group)
    output_dir = "output/%s"%(group)


    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = [os.path.join(input_dir, f) for f in sorted(os.listdir(input_dir))]
    bands, mask, meta = prepare_bands(files)
    calculate_indicies(bands, mask, meta, output_dir)
