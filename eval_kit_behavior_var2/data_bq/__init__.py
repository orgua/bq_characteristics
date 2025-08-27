from pathlib import Path

import pandas as pd

data: dict = {
    "LED  3 %, 1k Load": "LED_003pc_1k",
    "LED  4 %, 1k Load": "LED_004pc_1k",
    "LED  4 %, no Load": "LED_004pc_OC",
    "LED  5 %, 1k Load": "LED_005pc_1k",
    "LED  6 %, 1k Load": "LED_006pc_1k",
    "LED  8 %, 1k Load": "LED_008pc_1k",
    "LED 10 %, 1k Load": "LED_010pc_1k",
    "LED 12 %, 1k Load": "LED_012pc_1k",
    "LED 14 %, 1k Load": "LED_014pc_1k",
    "LED 15 %, 1k Load": "LED_015pc_1k",
    "LED 16 %, 1k Load": "LED_016pc_1k",
    "LED 18 %, 1k Load": "LED_018pc_1k",
    "LED 20 %, 1k Load": "LED_020pc_1k",
    "LED 22 %, 1k Load": "LED_022pc_1k",
}

data_ts_voc: dict = {  # timestamp of first recorded VOC-meas
    "LED  3 %, 1k Load": 7.672,
    "LED  4 %, 1k Load": 10.953,
    "LED  4 %, no Load": 11.633,  # just a guess
    "LED  5 %, 1k Load": 3.815,
    "LED  6 %, 1k Load": 13.722,
    "LED  8 %, 1k Load": 13.901,
    "LED 10 %, 1k Load": 12.863,
    "LED 12 %, 1k Load": 13.109,
    "LED 14 %, 1k Load": 14.442,
    "LED 15 %, 1k Load": 4.383,
    "LED 16 %, 1k Load": 15.952,
    "LED 18 %, 1k Load": 14.619,
    "LED 20 %, 1k Load": 10.001,
    "LED 22 %, 1k Load": 14.375,
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
