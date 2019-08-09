import numpy as np
import band_math_definitions as BM

VNIR = {
    "Visible": {
        "R": lambda b: b[3],
        "G": lambda b: b[2],
        "B": lambda b: b[1],
    },
    "Vegetation and visible bands": {
        "R": BM.VNIR["NDVI"],
        "G": lambda b: b[2],
        "B": lambda b: b[1],
    }
}

SWIR = {
    "AlOH minerals + advanced argillic alteration": {
        "R": BM.SWIR["Phengitic"],
        "G": BM.SWIR["Muscovite"],
        "B": BM.SWIR["Kaolinite"],
    },

    "Clay, amphibole, laterite": {
        "R": BM.SWIR["Clay"],
        "G": BM.SWIR["Amphibole"],
        "B": BM.SWIR["Laterite"],
    },
}


TIR = {
    "Silica, carbonate, basic degree index": {
        "R": BM.TIR["Silica"],
        "G": BM.TIR["Carbonate"],
        "B": BM.TIR["SiO2-2"],
    },

    "Silica": {
        "R": BM.TIR["Silica-1"],
        "G": BM.TIR["Silica-2"],
        "B": BM.TIR["Silica-3"],
    },
}



VNIR_SWIR = {
    "Gossan, alteration, host rock - 1": {
        "R": BM.VNIR_SWIR["Gossan"],
        "G": BM.SWIR["Alteration"],
        "B": BM.SWIR["Host rock"],
    },

    "Gossan, alteration, host rock - 2": {
        "R": lambda b: b[6],
        "G": lambda b: b[2],
        "B": lambda b: b[1],
    },

    "Discrimination - 1": {
        "R": lambda b: np.true_divide(b[4], b[7]),
        "G": lambda b: np.true_divide(b[4], b[1]),
        "B": lambda b: np.true_divide(b[2], b[3]) * np.true_divide(b[4], b[3]),
    },

    "Discrimination - 2": {
        "R": lambda b: np.true_divide(b[4], b[7]),
        "G": lambda b: np.true_divide(b[4], b[3]),
        "B": lambda b: np.true_divide(b[2], b[1]),
    },

    "Enhanced structural features": {
        "R": lambda b: b[7],
        "G": lambda b: b[4],
        "B": lambda b: b[2],
    },
}


VNIR_SWIR_TIR = {
    "Discrimination for mapping": {
        "R": lambda b: np.true_divide(b[4], b[1]),
        "G": lambda b: np.true_divide(b[3], b[1]),
        "B": lambda b: np.true_divide(b[12], b[13]),

    },

    "Discrimination in sulphide rich areas": {
        "R": lambda b: b[12],
        "G": lambda b: b[5],
        "B": lambda b: b[3],
    },

    "Silica, Fe2+": {
        "R": BM.TIR["Quartz rich rocks"],
        "G": BM.VNIR_SWIR["Ferrous iron, Fe2+"],
        # TODO should be MNF 1
        "B": lambda b: b[1],
    },
}
