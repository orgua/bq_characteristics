from itertools import product
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from plot_statistics_bq import generator_bq
from plot_statistics_vsrc import generator_vsrc
from shepherd_cfg_bq import cfg_bq25570_base
from shepherd_cfg_bq import cfg_bq25570_eval

if __name__ == "__main__":
    results: dict = {
        "BQ-Reference": generator_bq(),
        "VSrc-Base": generator_vsrc(cfg_bq25570_base),
        "VSrc-Extra": generator_vsrc(cfg_bq25570_eval),
    }

    fig, axs = plt.subplots(4, 1, sharex="all", figsize=(10, 2 * 6), layout="tight")
    fig.suptitle("BQ25570 Eval Kit Characteristics")

    axs[0].set_ylabel("Duty Cycle [%]")

    axs[1].set_ylabel("Switch Rate [n/min]")

    axs[2].set_ylabel("On-duration [s]")
    axs[2].set_yscale("log")

    axs[3].set_ylabel("Efficiency [%]")
    axs[3].set_xlabel("LED-Intensity [%]")
    axs[3].set_xticks(np.arange(2, 23, 2))

    for _idx, result in enumerate(results.values()):
        axs[0].plot(result["intensity"], result["duty_on"])

        axs[1].plot(result["intensity"], result["rate_per_min"])

        axs[2].plot(result["intensity"], [np.min(_x) for _x in result["durations_on"]])
        axs[2].plot(result["intensity"], [np.mean(_x) for _x in result["durations_on"]])
        axs[2].plot(result["intensity"], [np.max(_x) for _x in result["durations_on"]])

        axs[3].plot(result["intensity"], result["efficiency1"])
        axs[3].plot(result["intensity"], result["efficiency2"])

    axs[0].legend(results.keys(), loc="lower right")
    axs[1].legend(results.keys(), loc="upper right")
    axs[2].legend(
        [" - ".join(_x) for _x in product(results.keys(), ["min", "mean", "max"])],
        loc="lower right",
    )
    axs[3].legend(
        [
            " - ".join(_x)
            for _x in product(results.keys(), ["vs. actual Input", "vs. max of IVCurve"])
        ],
        loc="lower right",
    )

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
