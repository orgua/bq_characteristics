from pathlib import Path

import pandas as pd

data: dict = {
    "LED 20 %, 510R Load": "LED_020pc_510R",
    "LED 21 %, 510R Load": "LED_021pc_510R",
    "LED 22 %, 510R Load": "LED_022pc_510R",
    "LED 23 %, 510R Load": "LED_023pc_510R",
    "LED 24 %, 510R Load": "LED_024pc_510R",
    "LED 25 %, 510R Load": "LED_025pc_510R",
    "LED 26 %, 510R Load": "LED_026pc_510R",
    "LED 27 %, 510R Load": "LED_027pc_510R",
    "LED 28 %, 510R Load": "LED_028pc_510R",
    "LED 29 %, 510R Load": "LED_029pc_510R",
    "LED 30 %, 510R Load": "LED_030pc_510R",
    "LED 31 %, 510R Load": "LED_031pc_510R",
    "LED 32 %, 510R Load": "LED_032pc_510R",
    "LED 33 %, 510R Load": "LED_033pc_510R",
    "LED 34 %, 510R Load": "LED_034pc_510R",
    "LED 35 %, 510R Load": "LED_035pc_510R",
}

data_names: list = list(data.keys())

path_here = Path(__file__).parent.absolute()
paths_analog: dict = {name: path_here / (value + ".analog.pickle") for name, value in data.items()}
paths_digital: dict = {
    name: path_here / (value + ".digital.pickle") for name, value in data.items()
}


def get_bq_analog(name: str) -> pd.DataFrame:
    return pd.read_pickle(paths_analog[name], compression="zstd")


def get_bq_digital(name: str, plottable: bool = False) -> pd.DataFrame:
    pwr_good = pd.read_pickle(paths_digital[name], compression="zstd")
    if not plottable:
        return pwr_good
    # allow visualisation for digital data
    eval_d2 = pwr_good.iloc[:-1, :]
    eval_d2["Time [s]"] = pwr_good["Time [s]"].iloc[1:].reset_index(drop=True) - 10e-9
    return (
        pd.concat([pwr_good, eval_d2], axis=0, ignore_index=True)
        .sort_values(by=["Time [s]"])
        .reset_index(drop=True)
    )
