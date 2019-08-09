from collections import defaultdict
import zipfile
import re
import glob

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
