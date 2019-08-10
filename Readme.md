A script to build ASTER Mineral Indices based on [ASTER Surface Reflectance](https://lpdaac.usgs.gov/products/ast_07xtv003/) and [ASTER Surface Emissivity](https://lpdaac.usgs.gov/products/ast_05v003/) data.

A list of indices based on [ASTER Mineral Index Processing Manual](https://data.gov.au/dataset/ds-ga-a05f7892-da28-7506-e044-00144fdd4fa6) by Aleks Kalinowski and Simon Oliver.

### How to run it

First, install dependencies: `pip install numpy rasterio`.

Place your source files under `data` directory and `python main.py` to generate indices into `output` directory.

