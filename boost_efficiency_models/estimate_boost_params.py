from pathlib import Path

import pandas as pd
from model_boost_efficiency import efficiency_boost_fit
from model_boost_efficiency import params_bound_high
from model_boost_efficiency import params_bound_low
from model_boost_efficiency import params_datasheet
from scipy.optimize import curve_fit

path_here = Path(__file__).parent
path_data = path_here / "meas_scripts/board_a/boost_results_processed.csv"
data: pd.DataFrame = pd.read_csv(path_data, sep=";", decimal=",")

xdata = data[["V_inp", "I_inp", "V_out"]].to_numpy()
ydata = data["eta"].to_numpy()

popt, pcov = curve_fit(
    f=efficiency_boost_fit,
    xdata=xdata,
    ydata=ydata,
    p0=list(params_datasheet.values()),
    bounds=(list(params_bound_low.values()), list(params_bound_high.values())),
    check_finite=True,
    method="trf",
)
params_fit = {}
for index, param in enumerate(params_datasheet.keys()):
    params_fit[param] = popt[index]
print(popt)
print(pcov)

# create LUT
v_out = [2.88]  # [2.52, 2.88, 3.32]  # 2.52 .. 3.32
# LUT
v_inp_min = (2**18) * 1e-6
# v_inp_low = [v_inp_min * x for x in range(12)]
v_inp_mid = [v_inp_min / 2 + v_inp_min * x for x in range(12)]
# v_inp_hig = [v_inp_min * (x + 1) for x in range(12)]
i_inp_min = (2**14) * 1e-9
i_inp_mid = [i_inp_min / 2 * 2**x for x in range(12)]


for vo in v_out:
    print("Model for V_OUT={vo}")
    lut_boost_model_fit: list = []
    for vi in v_inp_mid:
        for ii in i_inp_mid:
            # TODO: missing? never finished
            pass

print("done")
