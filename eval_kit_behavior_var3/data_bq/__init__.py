from pathlib import Path

import pandas as pd

data: dict = {
    "LED  3 %, 1k Load": "LED_003pc_sw_1k",
    "LED  4 %, 1k Load": "LED_004pc_sw_1k",
    "LED  6 %, 1k Load": "LED_006pc_sw_1k",
    "LED  8 %, 1k Load": "LED_008pc_sw_1k",
    "LED 10 %, 1k Load": "LED_010pc_sw_1k",
    "LED 12 %, 1k Load": "LED_012pc_sw_1k",
    "LED 14 %, 1k Load": "LED_014pc_sw_1k",
    "LED 16 %, 1k Load": "LED_016pc_sw_1k",
    "LED 18 %, 1k Load": "LED_018pc_sw_1k",
    "LED 20 %, 1k Load": "LED_020pc_sw_1k",
    "LED 22 %, 1k Load": "LED_022pc_sw_1k",
}

data_ts_voc: dict = {  # timestamp of first recorded VOC-meas
    "LED  3 %, 1k Load": 13.510,
    "LED  4 %, 1k Load": 14.208,
    "LED  6 %, 1k Load": 14.164,
    "LED  8 %, 1k Load": 14.005,
    "LED 10 %, 1k Load": 3.363,
    "LED 12 %, 1k Load": 13.031,
    "LED 14 %, 1k Load": 13.453,
    "LED 16 %, 1k Load": 14.589,
    "LED 18 %, 1k Load": 15.508,
    "LED 20 %, 1k Load": 22.974,
    "LED 22 %, 1k Load": 12.796,
}

data_names: list = list(data.keys())

path_here = Path(__file__).parent.absolute()
paths_analog: dict = {name: path_here / (value + ".analog.pickle") for name, value in data.items()}
paths_digital: dict = {
    name: path_here / (value + ".digital.pickle") for name, value in data.items()
}


def get_bq_analog(name: str) -> pd.DataFrame:
    return pd.read_pickle(paths_analog[name], compression="zstd")  # noqa: S301


def get_bq_digital(name: str, *, plottable: bool = False) -> pd.DataFrame:
    pwr_good = pd.read_pickle(paths_digital[name], compression="zstd")  # noqa: S301
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
