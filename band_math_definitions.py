import numpy as np

VNIR = {
    # Iron
    "Ferric iron, Fe3+": lambda b: np.true_divide(b[2], b[1]), #2/1

    # Other
    "Vegetation": lambda b: np.true_divide(b[3], b[2]), #3/2
    "NDVI": lambda b: np.true_divide(b[3] - b[2], b[3] + b[2]), #(3-2)/(3+2)
}

SWIR = {
    # Iron
    "Laterite": lambda b: np.true_divide(b[4], b[5]), # 4/5
    "Ferrous silicates (biot, chl, amph)": lambda b: np.true_divide(b[5], b[4]), # 5/4

    # Carbonates / Mafic Minerals
    "Carbonate - chlorite - epidote": lambda b: np.true_divide(b[7] + b[9], b[8]), # (7+9)/8
    "Epidote - chlorite - amphibole": lambda b: np.true_divide(b[6] + b[9], b[7] + b[8]), # (6+9)/(7+8)
    "Amphibole - MgOH": lambda b: np.true_divide(b[6] + b[9], b[8]), # (6+9)/8
    "Amphibole": lambda b: np.true_divide(b[6], b[8]), # 6/8
    "Dolomite": lambda b: np.true_divide(b[6] + b[8], b[7]), # (6+8)/7

    # Silicates
    "Sericite - muscovite - illite - smectite": lambda b: np.true_divide(b[5] + b[7], b[6]), # (5+7)/6
    "Alunite - kaolinite - pyrophyllite": lambda b: np.true_divide(b[4] + b[6], b[5]), # (4+6)/5
    "Phengitic": lambda b: np.true_divide(b[5], b[6]), # 5/6
    "Muscovite": lambda b: np.true_divide(b[7], b[6]), # 7/6
    "Kaolinite": lambda b: np.true_divide(b[7], b[5]), # 7/5
    "Clay": lambda b: np.true_divide(b[5] * b[7], b[6] * b[6]), # (5x7)/6/6
    "Alteration": lambda b: np.true_divide(b[4], b[5]), # 4/5
    "Host rock": lambda b: np.true_divide(b[5], b[6]), # 5/6
}

VNIR_SWIR = {
    # Iron
    "Ferrous iron, Fe2+": lambda b: np.true_divide(b[5], b[3]) + np.true_divide(b[1], b[2]), # 5/3 + 1/2
    "Gossan": lambda b: np.true_divide(b[4], b[2]), # 4/2
    "Ferric oxides": lambda b: np.true_divide(b[4], b[3]), # 4/3
}

TIR = {
    "Carbonate": lambda b: np.true_divide(b[13], b[14]), # 13/14

    # Silica
    "Quartz rich rocks": lambda b: np.true_divide(b[14], b[12]), # 14/12
    "Silica": lambda b: np.true_divide(b[11] * b[11], b[10] * b[12]), # (11x11)/10/12
    "Basic degree index (gnt, cpx, epi, chl)": lambda b: np.true_divide(b[12], b[13]), # 12/13
    "SiO2-1": lambda b: np.true_divide(b[13], b[12]), # 13/12
    "SiO2-2": lambda b: np.true_divide(b[12], b[13]), # 12/13
    "Siliceous rocks": lambda b: np.true_divide(b[11] * b[11], b[10] * b[12]), # (11x11)/(10x12)
    "Silica-1": lambda b: np.true_divide(b[11], b[10]), # 11/10
    "Silica-2": lambda b: np.true_divide(b[11], b[12]), # 11/12
    "Silica-3": lambda b: np.true_divide(b[13], b[10]), # 13/10
}
