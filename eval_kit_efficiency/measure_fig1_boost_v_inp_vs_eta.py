from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from smu_measure import smu_measure_boost

# CONFIG

vs_input = np.flip(
    np.concat(
        (
            np.arange(100e-3, 600e-3, 50e-3),
            np.arange(600e-3, 3.001, 100e-3),
        ),
    ),
)
vs_output = [2.0, 3.0, 4.0, 5.0]
is_input = [100e-6]

path_here = Path(__file__).parent
path_result = path_here / "boost_v_inp_vs_efficiency.csv"

# INIT

if path_result.exists():
    results_pd = pd.read_csv(path_result, sep=";", decimal=",")
else:
    results_pd = smu_measure_boost(vs_input, is_input, vs_output)
    results_pd.to_csv(path_result, sep=";", decimal=",", index=False)

# graph

from matplotlib import pyplot as plt

fig = plt.figure(figsize=(10, 4), layout="tight")

for v_out, i_inp in product(vs_output, is_input):
    data = results_pd.loc[(results_pd["V_out_nom"] == v_out) & (results_pd["I_inp_nom"] == i_inp)]
    if len(data) <= 1:
        continue
    plt.plot(data["V_inp"], data["eta"], label=f"i_inp={i_inp}A,v_out={v_out}V")

plt.xlabel("V_Input [V]")
plt.xticks([x / 10 for x in range(0, 31, 2)])
plt.ylabel("efficiency [n]")
plt.yticks([y / 10 for y in range(11)])
plt.grid(True)
plt.legend(loc="lower right")
plt.savefig(path_result.with_suffix(".png"))
plt.close(fig)
