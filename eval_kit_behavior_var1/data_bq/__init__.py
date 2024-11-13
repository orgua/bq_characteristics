from pathlib import Path

import pandas as pd

data: dict = {
    # "LED  400mA, open-circuit": "OC, LED 400mA",
    "LED  400mA, 1000R Load": "R1k, LED 400mA",
    "LED  700mA, 1000R Load": "R1k, LED 700mA",
    "LED  900mA, 1000R Load": "R1k, LED 900mA",
    "LED 1100mA, 1000R Load": "R1k, LED 1100mA",
    # "LED  400mA, 100R Load": "R100, LED 400mA",
}

data_ts_voc: dict = {  # timestamp of first recorded VOC-meas
    "LED  400mA, open-circuit": 9.436,
    "LED  400mA, 1000R Load": 22.590,
    "LED  700mA, 1000R Load": 22.743,
    "LED  900mA, 1000R Load": 21.475,
    "LED 1100mA, 1000R Load": 21.279,
    "LED  400mA, 100R Load": 23.005,
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
