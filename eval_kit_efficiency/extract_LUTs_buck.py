"""Convert measurements stored in CSV to Shepherds YAML (print to console).

NOTE: Edge-Regions are often not measured correctly, so they have to be manually corrected afterward.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

v_inp = [2.50, 2.75, 3.00, 3.25]

LUT_output_I_min_log2_nA = 10
i_inp_min = (2**LUT_output_I_min_log2_nA) * 1e-9
i_inp_mid = [i_inp_min / 2 * 2**x for x in range(12)]

path_here = Path(__file__).parent
path_data = path_here / "data_board_A_buck/buck_results_processed.csv"
data_pd = pd.read_csv(path_data, sep=";", decimal=",")

for vi in v_inp:
    data_v = data_pd[data_pd["V_inp_nom"] == vi]
    ipol = interpolate.interp1d(
        data_v["I_inp"].to_numpy(),
        data_v["eta"].to_numpy(),
        fill_value="extrapolate",
        kind="linear",
    )
    xnew = np.asarray(i_inp_mid)
    ynew = ipol(xnew)
    plt.plot(data_v["I_inp"], data_v["eta"], "o", xnew, ynew, "-")
    plt.xlabel("I_Input [A]")
    plt.xscale("log")
    plt.ylabel("efficiency [n]")
    plt.yticks([y / 10 for y in range(11)])
    plt.grid(True)
    plt.show()
    plt.close()
    print(f"{path_data.stem}_VCap{vi}V:")
    print(f"    LUT_output_efficiency = {np.round(ynew, 3).tolist()}")
    print(f"    LUT_output_I_min_log2_nA = {LUT_output_I_min_log2_nA}")
