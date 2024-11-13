from pathlib import Path

import numpy as np
from data_bq import data_names as bq_names
from data_bq import get_bq_analog
from data_bq import get_bq_digital
from data_solar import get_ivcurve
from matplotlib import pyplot as plt

result_eval: dict = {
    "name": [],
    "intensity": [],
    "duty_on": [],
    "rate_per_min": [],
    "durations_on": [],
    "efficiency1": [],
    "efficiency2": [],
}

R_out = 1000

for name in bq_names:
    # first cmd throws away 1st & last entry to avoid partially sampled durations
    data_digital = get_bq_digital(name).iloc[1:-1, :]
    data_analog = get_bq_analog(name)
    timstamps_analog = data_analog["Time [s]"].to_numpy()
    eval_runtime = timstamps_analog[-1] - timstamps_analog[0]

    # generate Stats
    timestamps = data_digital["Time [s]"].to_numpy()
    if timestamps.shape[0] < 2:
        print(f"skipping {name} due to low BAT-OK activity")
        continue
    durations = timestamps[1:] - timestamps[:-1]
    time_total = timestamps[-1] - timestamps[0]
    data_digital = data_digital.iloc[:-1, :]  # last value is unusable for this
    data_digital["duration"] = durations
    filter_on = data_digital["BAT_OK"] == 1
    switches_n = np.sum(filter_on)

    if time_total < 0.5 * eval_runtime:
        print("discarding calculated t_total")
        time_total = eval_runtime
        switches_n += 1  # attempt to include the first and last discarded entries

    durations_on = data_digital.loc[filter_on, "duration"].to_numpy()
    if durations_on.shape[0] < 1:
        durations_on = [time_total]
    duty_on = 100 * durations_on.sum() / time_total
    rate_per_min = switches_n / time_total * 60.0
    print(
        f"{name}, duty = {duty_on:.1f} %, "
        f"switch_rate = {rate_per_min:.3f} n/min, "
        f"on-time min {1000*durations_on.min():.2f} ms, "
        f"mean {1000*durations_on.mean():.2f} ms, "
        f"max {1000*durations_on.max():.2f} ms"
    )
    # efficiency - combined with ivcurve
    ivcurve = get_ivcurve(name[:8])
    P_inp_max = (ivcurve["Voltage [V]"] * ivcurve["Current [A]"]).max()

    P_out = data_analog["V_OUT"] * data_analog["V_OUT"] / R_out
    # duration = data_analog["Time [s]"].iloc[-1] - data_analog["Time [s]"].iloc[0]
    i_array = ivcurve["Current [A]"].to_numpy()
    v_array = ivcurve["Voltage [V]"].to_numpy()

    # look for nearest voltage in ivcurve and store corresponding current
    data_analog["I_IN"] = data_analog["V_IN"].apply(
        lambda _v: i_array[(np.abs(v_array - _v)).argmin()]
    )

    P_inp = data_analog["V_IN"] * data_analog["I_IN"]
    P_inp_mean = P_inp.sum() / len(P_inp)
    P_out_mean = P_out.sum() / len(P_out)
    # save stats for plots
    result_eval["name"].append(name)
    result_eval["intensity"].append(float(name[4:6]))
    result_eval["duty_on"].append(duty_on)
    result_eval["rate_per_min"].append(rate_per_min)
    result_eval["durations_on"].append(durations_on)
    result_eval["efficiency1"].append(100 * P_out_mean / P_inp_mean)
    result_eval["efficiency2"].append(100 * P_out_mean / P_inp_max)


fig, axs = plt.subplots(4, 1, sharex="all", figsize=(10, 2 * 6), layout="tight")
fig.suptitle("BQ25570 Eval Kit Characteristics")

axs[0].set_ylabel("Duty Cycle [%]")
axs[0].plot(result_eval["intensity"], result_eval["duty_on"])
# axs[0].legend(["Sim", "Eval"], loc="upper right")

axs[1].set_ylabel("Switch Rate [n/min]")
axs[1].plot(result_eval["intensity"], result_eval["rate_per_min"])

axs[2].set_ylabel("On-duration [s]")
axs[2].plot(result_eval["intensity"], [_x.min() for _x in result_eval["durations_on"]])
axs[2].plot(result_eval["intensity"], [_x.mean() for _x in result_eval["durations_on"]])
axs[2].plot(result_eval["intensity"], [_x.max() for _x in result_eval["durations_on"]])
axs[2].legend(["min", "mean", "max"], loc="lower right")
axs[2].set_yscale("log")

axs[3].set_ylabel("Efficiency [%]")
axs[3].plot(result_eval["intensity"], result_eval["efficiency1"])
axs[3].plot(result_eval["intensity"], result_eval["efficiency2"])
axs[3].legend(["vs. actual Input", "vs. max of IVCurve"], loc="lower right")
axs[3].set_xlabel("LED-Intensity [%]")
axs[3].set_xticks(np.arange(2, 23, 2))

for ax in axs:
    # deactivates offset-creation for ax-ticks
    # ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.grid(True)

# TODO: add PwrIn, PwrOut

# plt.savefig(Path(__file__).with_suffix(".png"))
plt.savefig(Path(__file__).with_suffix(".svg"))
plt.close(fig)
plt.clf()
