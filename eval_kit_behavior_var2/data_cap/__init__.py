from pathlib import Path

import pandas as pd

data: dict = {
    "MLCC Charge Run 1": "cap_charge_1.pickle",
    "MLCC Charge Run 2": "cap_charge_2.pickle",
    "MLCC Charge Run 3": "cap_charge_3.pickle",
    "MLCC Discharge Run 1": "cap_discharge_1.pickle",
    "MLCC Discharge Run 2": "cap_discharge_2.pickle",
    "MLCC Discharge Run 3": "cap_discharge_3.pickle",
}

data_names: list = list(data.keys())

path_here: Path = Path(__file__).parent.absolute()
data_paths: dict = {name: path_here / value for name, value in data.items()}


def get_capacitor(name: str) -> pd.DataFrame:
    _data = pd.read_pickle(data_paths[name], compression="zstd")  # noqa: S301
    _data["Time [s]"] -= 0.016364380
    return _data
