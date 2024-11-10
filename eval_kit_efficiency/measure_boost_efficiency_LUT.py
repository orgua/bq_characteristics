"""Measures specified Grid and stores data sub-folder.

NOTE: needs SMU connected to BQ Eval Kit.

"""

from itertools import product
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from smu_measure import smu_measure_boost

# CONFIG
v_out = [2.50, 2.75, 3.00, 3.25]  # 2.52 .. 3.32

# LUT
v_inp_min = (2**17) * 1e-6
v_inp_low = [v_inp_min * x for x in range(12)]
v_inp_mid = [v_inp_min / 2 + v_inp_min * x for x in range(12)]
v_inp_hig = [v_inp_min * (x + 1) for x in range(12)]

i_inp_min = (2**13) * 1e-9
i_inp_mid = [i_inp_min / 2 * 2**x for x in range(12)]

# MAPPING
vs_input = v_inp_mid
vs_output = v_out
is_input = i_inp_mid

is_input.reverse()  # avoids startup-problems for the BQ
vs_input.reverse()
results_processed: list = []

path_here = Path(__file__).parent / "data_board_B_boost_LUT"
for v_output in vs_output:
    path_result = path_here / f"boost_lut_raw_vout{v_output:.3f}.csv"
    v_output = [v_output]

    # measure or load
    if path_result.exists():
        results_pd = pd.read_csv(path_result, sep=";", decimal=",")
    else:
        results_pd = smu_measure_boost(vs_input, is_input, v_output)
        results_pd.to_csv(path_result, sep=";", decimal=",", index=False)

    # process graph
    fig = plt.figure(figsize=(10, 8), layout="tight")

    for v_out, v_inp in product(v_output, vs_input):
        data: pd.DataFrame = results_pd.copy(deep=True)
        data = data.loc[(results_pd["V_out_nom"] == v_out)]
        data = data.loc[(results_pd["V_inp_nom"] == v_inp)]
        countA = data.shape[0]
        filter_vinp = (data["V_inp"] / v_inp - 1).abs() < 0.10  # %
        filter_vinp |= (data["V_inp"] - v_inp).abs() < 0.05  # V
        data = data[filter_vinp]
        filter_vout = (data["V_out"] / v_out - 1).abs() < 0.05  # %
        data = data[filter_vout]
        filter_iinp = abs(data["I_inp"] / data["I_inp_nom"] - 1) < 0.05  # %
        data = data[filter_iinp]
        countD = data.shape[0]
        data = data.groupby("I_inp_nom").median(numeric_only=True)
        countE = data.shape[0]
        results_processed.append(data)
        print(
            f"Plotgroup (VOut={v_out}, VInp={v_inp}) has "
            f"{countA} total entries, "
            f"{countD} valid, "
            f"{countE} medians",
        )
        if len(data) <= 1:
            continue
        plt.plot(data["I_inp"], data["eta"], label=f"V_Inp={v_inp}V,V_Stor={v_out}V")

    plt.xlabel("I_Input [A]")
    plt.xscale("log")
    # plt.xticks([x/10 for x in range(0, 31, 2)])
    plt.ylabel("efficiency [n]")
    plt.yticks([y / 10 for y in range(11)])
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.savefig(path_result.with_suffix(".svg"))
    plt.close(fig)

# store processed data
results_processed: pd.DataFrame = pd.concat(results_processed)
results_processed.to_csv(
    path_here / "boost_lut_processed.csv",
    sep=";",
    decimal=",",
    index=False,
)
