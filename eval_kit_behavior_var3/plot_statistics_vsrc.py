from pathlib import Path

import numpy as np
from data_solar import data_paths as solar_paths
from data_solar import get_ivcurve
from matplotlib import pyplot as plt
from shepherd_cfg_bq import cfg_bq25570_eval
from shepherd_core.data_models import VirtualSourceConfig
from shepherd_core.vsource import ResistiveTarget
from shepherd_sim_vsrc import simulate_source


def generator_vsrc(config: VirtualSourceConfig) -> dict:
    target = ResistiveTarget(R_Ohm=984, controlled=True)
    eval_runtime = 50

    result_eval: dict = {
        "name": [],
        "intensity": [],
        "duty_on": [],
        "rate_per_min": [],
        "durations_on": [],
        "efficiency1": [],
        "efficiency2": [],
    }

    for name, path in solar_paths.items():
        print(f"now simulating {name}")
        ivcurve = get_ivcurve(name)

        sim_stats = simulate_source(
            path_ivcurve=path,
            target=target,
            config=config,
            runtime=eval_runtime,
        )

        result_eval["name"].append(name)
        result_eval["intensity"].append(float(name[4:6]))
        result_eval["duty_on"].append(100 * sim_stats["PwrGood"].sum() / len(sim_stats["PwrGood"]))

        # calculate two kinds of efficiency
        P_inp_max = float((ivcurve["Voltage [V]"] * ivcurve["Current [A]"]).max())
        P_inp_mean = float(sim_stats["P_inp"].sum()) / len(sim_stats["P_inp"])
        P_out_mean = float(sim_stats["P_out"].sum()) / len(sim_stats["P_out"])
        try:
            result_eval["efficiency1"].append(100 * P_out_mean / P_inp_mean)
        except ZeroDivisionError:
            result_eval["efficiency1"].append(0)
        result_eval["efficiency2"].append(min(100.0, 100 * P_out_mean / P_inp_max))

        # generate BAT_OK_flank-timestamps
        bat_ok_long = sim_stats["PwrGood"].to_numpy()
        filter_flanks = (bat_ok_long[1:] - bat_ok_long[:-1]) != 0
        bat_ok_short = bat_ok_long[1:]
        bat_ok = bat_ok_short[filter_flanks != 0]

        # get matching TS for bat_ok_short
        timestamps = (sim_stats["time"].to_numpy()[1:])[filter_flanks]
        if timestamps.shape[0] < 2:
            print(f"skipping {name} due to low BAT-OK activity")
            result_eval["rate_per_min"].append(1)
            result_eval["durations_on"].append([eval_runtime])
            continue
        durations = timestamps[1:] - timestamps[:-1]
        time_total = timestamps[-1] - timestamps[0]
        filter_on = bat_ok == 1
        switches_n = np.sum(filter_on)
        if time_total < 0.5 * eval_runtime:
            print("discarding calculated t_total")
            time_total = eval_runtime
            switches_n += 1  # attempt to include the first and last discarded entries
        result_eval["rate_per_min"].append(switches_n / time_total * 60.0)
        durations_on = durations[filter_on[:-1]]
        if durations_on.shape[0] < 1:
            durations_on = [time_total]
        result_eval["durations_on"].append(durations_on)
    return result_eval


if __name__ == "__main__":
    result_eval = generator_vsrc(cfg_bq25570_eval)

    fig, axs = plt.subplots(4, 1, sharex="all", figsize=(10, 2 * 6), layout="tight")
    fig.suptitle("VSource Characteristics")

    axs[0].set_ylabel("Duty Cycle [%]")
    axs[0].plot(result_eval["intensity"], result_eval["duty_on"])
    # axs[0].legend(["Sim", "Eval"], loc="upper right")

    axs[1].set_ylabel("Switch Rate [n/min]")
    axs[1].plot(result_eval["intensity"], result_eval["rate_per_min"])

    axs[2].set_ylabel("On-duration [s]")
    axs[2].plot(result_eval["intensity"], [np.min(_x) for _x in result_eval["durations_on"]])
    axs[2].plot(result_eval["intensity"], [np.mean(_x) for _x in result_eval["durations_on"]])
    axs[2].plot(result_eval["intensity"], [np.max(_x) for _x in result_eval["durations_on"]])
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
        ax.grid(visible=True)

    # plt.savefig(Path(__file__).with_suffix(".png"))
    plt.savefig(Path(__file__).with_suffix(".svg"))
    plt.close(fig)
    plt.clf()
