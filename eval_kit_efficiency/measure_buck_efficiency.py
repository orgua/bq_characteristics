"""Measures specified Grid and stores data sub-folder.

NOTE: needs SMU connected to BQ Eval Kit.

"""

from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from smu_measure import smu_measure_buck

# CONFIG
v_inputs = [2.0, 2.5, 2.75, 3.0, 3.25, 3.5, 4.0, 4.5]
i_outputs = [
    500e-9,
    600e-9,
    700e-9,
    800e-9,
    900e-9,
    1e-6,
    2e-6,
    3e-6,
    4e-6,
    5e-6,
    6e-6,
    7e-6,
    8e-6,
    9e-6,
    10e-6,
    20e-6,
    30e-6,
    40e-6,
    50e-6,
    60e-6,
    70e-6,
    80e-6,
    9e-6,
    100e-6,
    200e-6,
    300e-6,
    400e-6,
    500e-6,
    600e-6,
    700e-6,
    800e-6,
    900e-6,
    1e-3,
    2e-3,
    3e-3,
    4e-3,
    5e-3,
    6e-3,
    7e-3,
    8e-3,
    9e-3,
    10e-3,
    20e-3,
    30e-3,
    40e-3,
    50e-3,
    60e-3,
    70e-3,
    80e-3,
]
v_output = 1.8  # nominal


path_here = Path(__file__).parent / "data_board_A_buck"

path_result = path_here / "buck_results_raw.csv"

# measure or load
if path_result.exists():
    results_pd = pd.read_csv(path_result, sep=";", decimal=",")
else:
    path_result.parent.mkdir(parents=True, exist_ok=True)
    results_pd = smu_measure_buck(v_inputs, v_output, i_outputs)
    results_pd.to_csv(path_result, sep=";", decimal=",", index=False)

# process & graph
fig = plt.figure(figsize=(10, 8), layout="tight")
results_processed: list = []

for v_inp in v_inputs:
    data: pd.DataFrame = results_pd.copy(deep=True)
    data = data.loc[(results_pd["V_inp_nom"] == v_inp)]
    countA = data.shape[0]
    filter_vinp = (data["V_inp"] / v_inp - 1).abs() < 0.10  # %
    filter_vinp |= (data["V_inp"] - v_inp).abs() < 0.05  # V
    data = data[filter_vinp]
    filter_vout = (data["V_out"] / v_output - 1).abs() < 0.05  # %
    data = data[filter_vout]
    filter_iout = abs(data["I_out"] / -data["I_out_nom"] - 1) < 0.05  # %
    data = data[filter_iout]
    filter_eta = data["eta"] >= 0.0
    filter_eta &= data["eta"] <= 1.0
    data = data[filter_eta]
    # data.loc[data["eta"] < 0.0, "eta"] = 0.0
    # data.loc[data["eta"] > 1.0, "eta"] = 1.0
    countD = data.shape[0]
    data = data.groupby("I_out_nom").median(numeric_only=True)
    countE = data.shape[0]
    results_processed.append(data)
    print(f"Plotgroup (VCap={v_inp}) has {countA} total entries, {countD} valid, {countE} medians")
    if len(data) <= 1:
        continue
    plt.plot(-data["I_out"], data["eta"], label=f"V_Stor={v_inp}V")

plt.xlabel("I_Output [A]")
plt.xscale("log")
# plt.xticks([x/10 for x in range(0, 31, 2)])
plt.ylabel("efficiency [n]")
plt.yticks([y / 10 for y in range(11)])
plt.grid(visible=True)
plt.legend(loc="lower right")
plt.savefig(path_result.with_suffix(".svg"))
plt.close(fig)

results_processed: pd.DataFrame = pd.concat(results_processed)
results_processed.to_csv(
    path_here / "buck_results_processed.csv",
    sep=";",
    decimal=",",
    index=False,
)
