from pathlib import Path

import numpy as np
from bq_shepherd import cfg_bq25570_eval
from bq_shepherd import simulate_source
from data_solar import data_paths as solar_paths
from data_solar import get_ivcurve
from matplotlib import pyplot as plt
from shepherd_core.vsource import ResistiveTarget

result_eval: dict = {
    "name": [],
    "intensity": [],
    "duty_on": [],
    "rate_per_min": [],
    "durations_on": [],
    "efficiency1": [],
    "efficiency2": [],
}

target = ResistiveTarget(R_Ohm=1000, controlled=False)
eval_runtime = 50

for name, path in solar_paths.items():
    print(f"now simulating {name}")
    ivcurve = get_ivcurve(name)

    sim_stats = simulate_source(
        path_ivcurve=path,
        target=target,
        config=cfg_bq25570_eval,
        runtime=50,
    )

    result_eval["name"].append(name)
    result_eval["intensity"].append(float(name[4:6]))
    result_eval["duty_on"].append(sim_stats["PwrGood"].sum() / len(sim_stats["PwrGood"]))
    result_eval["rate_per_min"].append(0)
    result_eval["durations_on"].append([0])

    P_inp_max = float((ivcurve["Voltage [V]"] * ivcurve["Current [A]"]).max())
    P_inp_mean = float(sim_stats["P_inp"].sum()) / len(sim_stats["P_inp"])
    P_out_mean = float(sim_stats["P_out"].sum()) / len(sim_stats["P_out"])
    try:
        result_eval["efficiency1"].append(100 * P_out_mean / P_inp_mean)
    except ZeroDivisionError:
        result_eval["efficiency1"].append(0)
    result_eval["efficiency2"].append(min(100.0, 100 * P_out_mean / P_inp_max))

    # filter_on = data["BAT_OK"] == 1
    # durations_on = data.loc[filter_on, "duration"].to_numpy()
    # rate_per_min = filter_on.sum() / time_total * 60.0


fig, axs = plt.subplots(4, 1, sharex="all", figsize=(10, 2 * 6), layout="tight")
fig.suptitle("VSource Characteristics")

axs[0].set_ylabel("Duty Cycle [%]")
axs[0].plot(result_eval["intensity"], result_eval["duty_on"])
# axs[0].legend(["Sim", "Eval"], loc="upper right")

axs[1].set_ylabel("Switch Rate [n/min]")
axs[1].plot(result_eval["intensity"], result_eval["rate_per_min"])

axs[2].set_ylabel("On-duration [s]")
# axs[2].plot(result_eval["intensity"], [_x.min() for _x in result_eval["durations_on"]])
# axs[2].plot(result_eval["intensity"], [_x.mean() for _x in result_eval["durations_on"]])
# axs[2].plot(result_eval["intensity"], [_x.max() for _x in result_eval["durations_on"]])
# axs[2].legend(["min", "mean", "max"], loc="lower right")
# axs[2].set_yscale("log")

axs[3].set_ylabel("Efficiency [%]")
axs[3].plot(result_eval["intensity"], result_eval["efficiency1"])
axs[3].plot(result_eval["intensity"], result_eval["efficiency2"])
axs[2].legend(["vs. real Input", "vs. max of IVCurve"], loc="lower right")
axs[3].set_xlabel("LED-Intensity [%]")
axs[3].set_xticks(np.arange(2, 23, 2))

for ax in axs:
    # deactivates offset-creation for ax-ticks
    # ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.grid(True)

plt.savefig(Path(__file__).with_suffix(".png"))
plt.savefig(Path(__file__).with_suffix(".svg"))
plt.close(fig)
plt.clf()
