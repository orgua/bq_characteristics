from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent.absolute()

data_paths: dict = {
    "LED  400mA": path_here / "solar-iv-400mA.ivcurve.csv",
    "LED  900mA": path_here / "solar-iv-900mA.ivcurve.csv",
    "LED 1000mA": path_here / "solar-iv-1100mA.ivcurve.csv",
}

data_names: list = list(data_paths.keys())


def get_ivcurve(name: str) -> pd.DataFrame:
    return pd.read_csv(data_paths[name], sep=";", decimal=".", skipinitialspace=True)
