from pathlib import Path

from data_bq import data_names as bq_names
from data_bq import data_ts_voc
from data_bq import get_bq_analog
from data_bq import get_bq_digital
from data_solar import data_paths as solar_paths
from data_solar import get_ivcurve
from matplotlib import pyplot as plt
from shepherd_cfg_bq import cfg_bq25570_eval
from shepherd_core.vsource import ResistiveTarget
from shepherd_sim_vsrc import simulate_source

# config - mainly for sim
path_here = Path(__file__).parent
target = ResistiveTarget(R_Ohm=983, controlled=False)
eval_runtime = 20

for name, path in solar_paths.items():
    print(f"now simulating {name}, path = {path}")
    ivcurve = get_ivcurve(name)

    sim_stats = simulate_source(
        path_ivcurve=path,
        target=target,
        config=cfg_bq25570_eval,
        runtime=eval_runtime,
    )

    # open eval-data
    eval_stats = eval_pwrgd = None
    ts_voc = 0
    for bq_name in bq_names:
        if name in bq_name:
            eval_stats = get_bq_analog(bq_name)
            eval_pwrgd = get_bq_digital(bq_name, plottable=True)
            ts_voc = data_ts_voc[bq_name]
            print(f"Chosen BQ-Record = {bq_name}")
            break

    if eval_stats is None or eval_pwrgd is None:
        raise ValueError(f"No bq-recording was found for {name}")

    # Align data
    eval_stats["Time [s]"] = eval_stats["Time [s]"] - ts_voc
    eval_pwrgd["Time [s]"] = eval_pwrgd["Time [s]"] - ts_voc

    # shorten timeframe
    eval_runtime = min(eval_runtime, sim_stats["time"].max())
    eval_stats = eval_stats.loc[eval_stats["Time [s]"] <= eval_runtime]
    eval_stats = eval_stats.loc[eval_stats["Time [s]"] >= 0.0]
    eval_pwrgd = eval_pwrgd.loc[eval_pwrgd["Time [s]"] <= eval_runtime]
    eval_pwrgd = eval_pwrgd.loc[eval_pwrgd["Time [s]"] >= 0.0]
    sim_stats = sim_stats.loc[sim_stats["time"] <= eval_runtime]
    sim_stats = sim_stats.loc[sim_stats["time"] >= 0.0]

    # Visualize
    fig, axs = plt.subplots(5, 1, sharex="all", figsize=(20, 4 * 6), layout="tight")
    fig.suptitle(f"BQ25570 & VSource-Sim with {name}")  # , E={e_out_Ws} Ws")
    axs[0].set_ylabel("Voltage Input [V]")
    axs[0].plot(sim_stats["time"], sim_stats["V_inp"])
    axs[0].plot(eval_stats["Time [s]"], eval_stats["V_IN"], alpha=0.7)
    axs[0].legend(["Sim", "Eval"], loc="upper right")

    axs[1].set_ylabel("Voltage Storage [V]")
    axs[1].plot(sim_stats["time"], sim_stats["V_cap"])
    axs[1].plot(eval_stats["Time [s]"], eval_stats["V_BAT"], alpha=0.7)
    axs[1].legend(["Sim", "Eval"], loc="upper right")

    axs[2].set_ylabel("Voltage Output [V]")
    axs[2].plot(sim_stats["time"], sim_stats["V_out"])
    axs[2].plot(eval_stats["Time [s]"], eval_stats["V_OUT"], alpha=0.7)
    axs[2].legend(["Sim", "Eval"], loc="upper right")

    axs[3].set_ylabel("PwrGood [n]")
    axs[3].plot(sim_stats["time"], 0.95 * sim_stats["PwrGood"] + 1)
    axs[3].plot(eval_pwrgd["Time [s]"], 0.95 * eval_pwrgd["BAT_OK"])
    axs[3].legend(["Sim", "Eval"], loc="upper right")

    axs[4].set_ylabel("Power Sim [mW]")
    axs[4].plot(sim_stats["time"], 1e3 * sim_stats["P_inp"], color="green")
    axs[4].plot(sim_stats["time"], 1e3 * sim_stats["P_out"], color="red", alpha=0.7)
    axs[4].legend(["P_inp (Sim)", "P_out (Sim)"], loc="upper right")

    axs[4].set_xlabel("Runtime [s]")

    for ax in axs:
        # deactivates offset-creation for ax-ticks
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)

    plt.savefig(Path(__file__).with_suffix("." + name + ".png"))
    # plt.savefig(Path(__file__).with_suffix(".svg"))
    plt.close(fig)
    plt.clf()

    print(f"PowerGood - Ratio: {sim_stats["PwrGood"].sum() / sim_stats["PwrGood"].shape[0]:.3f}")
