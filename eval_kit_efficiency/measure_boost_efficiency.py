"""Measures specified Grid and stores data sub-folder.

NOTE: needs SMU connected to BQ Eval Kit.

"""

from itertools import product
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from smu_measure import smu_measure_boost

# CONFIG
vs_inputs = [
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.7,
    0.8,
    1.0,
    1.5,
    2.0,
    2.5,
    3.0,
    3.5,
]
vs_output = [2.0, 2.5, 3.0, 3.5, 4.0]
is_input = [
    10e-6,
    20e-6,
    30e-6,
    40e-6,
    50e-6,
    60e-6,
    80e-6,
    100e-6,
    200e-6,
    300e-6,
    400e-6,
    500e-6,
    600e-6,
    800e-6,
    1e-3,
    2e-3,
    3e-3,
    4e-3,
    5e-3,
    6e-3,
    8e-3,
    10e-3,
    20e-3,
    30e-3,
    40e-3,
    50e-3,
]
is_input.reverse()  # avoids startup-problems for the BQ
# vs_inputs.reverse()
results_processed: list = []

path_here = Path(__file__).parent / "data_board_A_boost_full"

for vs_input in vs_inputs:
    path_result = path_here / f"boost_results_raw_vin{vs_input:.2f}.csv"
    vs_input = [vs_input]

    # measure or load
    if path_result.exists():
        results_pd = pd.read_csv(path_result, sep=";", decimal=",")
    else:
        results_pd = smu_measure_boost(vs_input, is_input, vs_output)
        results_pd.to_csv(path_result, sep=";", decimal=",", index=False)

    # process graph
    fig = plt.figure(figsize=(10, 8), layout="tight")

    for v_out, v_inp in product(vs_output, vs_input):
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
    plt.grid(visible=True)
    plt.legend(loc="lower right")
    plt.savefig(path_result.with_suffix(".svg"))
    plt.close(fig)

# store processed data
results_processed: pd.DataFrame = pd.concat(results_processed)
results_processed.to_csv(
    path_here / "boost_results_processed.csv",
    sep=";",
    decimal=",",
    index=False,
)
