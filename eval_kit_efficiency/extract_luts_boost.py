"""Convert measurements stored in CSV to Shepherds YAML (print to console).

NOTE: Edge-Regions are often not measured correctly,
      so they have to be manually corrected afterward.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import interpolate

v_cap = [2.50, 2.75, 3.00, 3.25]

LUT_input_V_min_log2_uV = 17
LUT_input_I_min_log2_nA = 13

i_inp_min = (2**LUT_input_I_min_log2_nA) * 1e-9
i_inp_mid = [i_inp_min / 2 * 2**x for x in range(12)]

v_inp_min = (2**LUT_input_V_min_log2_uV) * 1e-6
v_inp_mid = [v_inp_min / 2 + v_inp_min * x for x in range(12)]

path_here = Path(__file__).parent
path_data = path_here / "data_board_A_boost_LUT/boost_lut_processed.csv"

data_pd = pd.read_csv(path_data, sep=";", decimal=",")

for vc in v_cap:
    data_v = data_pd[data_pd["V_out_nom"] == vc]
    points = data_v[["I_inp", "V_inp"]].to_numpy()
    values = data_v["eta"].to_numpy()
    gridx = np.asarray(i_inp_mid)  # columns
    gridy = np.asarray(v_inp_mid)  # rows
    X, Y = np.meshgrid(gridx, gridy)
    lipol = interpolate.LinearNDInterpolator(points, values, fill_value=0.010)
    gridz = lipol(X, Y)
    # gridz = interpolate.griddata(points, values, (X, Y), method="nearest")
    print(f"{path_data.stem}_VCap{vc}V:")
    print("    LUT_input_efficiency: [")
    for _idx in range(gridz.shape[0]):
        row = np.round(gridz[_idx, :], 3).tolist()
        row = [str(elem).ljust(5, "0") for elem in row]
        print(f"      {row},")
    print("    ]")
    print(f"    LUT_input_V_min_log2_uV: {LUT_input_V_min_log2_uV}")
    print(f"    LUT_input_I_min_log2_nA: {LUT_input_I_min_log2_nA}")
