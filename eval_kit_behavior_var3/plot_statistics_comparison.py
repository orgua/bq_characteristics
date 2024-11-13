from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from plot_statistics_bq import generator_bq
from plot_statistics_vsrc import generator_vsrc

from eval_kit_behavior_var2.shepherd_cfg_bq import cfg_bq25570_eval
from eval_kit_behavior_var3.shepherd_cfg_bq import cfg_bq25570_base

if __name__ == "__main__":
    result_bq = generator_bq()
    result_vsrc1 = generator_vsrc(cfg_bq25570_base)
    result_vsrc2 = generator_vsrc(cfg_bq25570_eval)

    fig, axs = plt.subplots(4, 1, sharex="all", figsize=(10, 2 * 6), layout="tight")
    fig.suptitle("BQ25570 Eval Kit Characteristics")

    axs[0].set_ylabel("Duty Cycle [%]")
    axs[0].plot(result_bq["intensity"], result_bq["duty_on"])
    axs[0].plot(result_vsrc1["intensity"], result_vsrc1["duty_on"])
    axs[0].plot(result_vsrc2["intensity"], result_vsrc2["duty_on"])
    axs[0].legend(["BQ", "VSrcBase", "VSrcExtra"], loc="upper right")

    axs[1].set_ylabel("Switch Rate [n/min]")
    axs[1].plot(result_bq["intensity"], result_bq["rate_per_min"])
    axs[1].plot(result_vsrc1["intensity"], result_vsrc1["rate_per_min"])
    axs[1].plot(result_vsrc2["intensity"], result_vsrc2["rate_per_min"])
    axs[1].legend(["BQ", "VSrcBase", "VSrcExtra"], loc="upper right")

    axs[2].set_ylabel("On-duration [s]")
    axs[2].plot(result_bq["intensity"], [_x.min() for _x in result_bq["durations_on"]])
    axs[2].plot(result_bq["intensity"], [_x.mean() for _x in result_bq["durations_on"]])
    axs[2].plot(result_bq["intensity"], [_x.max() for _x in result_bq["durations_on"]])
    axs[2].legend(["min", "mean", "max"], loc="lower right")
    axs[2].set_yscale("log")

    axs[3].set_ylabel("Efficiency [%]")
    axs[3].plot(result_bq["intensity"], result_bq["efficiency1"])
    axs[3].plot(result_vsrc1["intensity"], result_vsrc1["efficiency1"])
    axs[3].plot(result_vsrc2["intensity"], result_vsrc2["efficiency1"])
    axs[3].legend(["BQ", "VSrcBase", "VSrcExtra"], loc="upper right")

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
