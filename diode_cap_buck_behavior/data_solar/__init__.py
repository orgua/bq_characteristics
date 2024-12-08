from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent.absolute()

data_paths: dict = {
    "LED 20 %": path_here / "LED_020pc.ivcurve.csv",
    "LED 21 %": path_here / "LED_021pc.ivcurve.csv",
    "LED 22 %": path_here / "LED_022pc.ivcurve.csv",
    "LED 23 %": path_here / "LED_023pc.ivcurve.csv",
    "LED 24 %": path_here / "LED_024pc.ivcurve.csv",
    "LED 25 %": path_here / "LED_025pc.ivcurve.csv",
    "LED 26 %": path_here / "LED_026pc.ivcurve.csv",
    "LED 27 %": path_here / "LED_027pc.ivcurve.csv",
    "LED 28 %": path_here / "LED_028pc.ivcurve.csv",
    "LED 29 %": path_here / "LED_029pc.ivcurve.csv",
    "LED 30 %": path_here / "LED_030pc.ivcurve.csv",
    "LED 31 %": path_here / "LED_031pc.ivcurve.csv",
    "LED 32 %": path_here / "LED_032pc.ivcurve.csv",
    "LED 33 %": path_here / "LED_033pc.ivcurve.csv",
    "LED 34 %": path_here / "LED_034pc.ivcurve.csv",
    "LED 35 %": path_here / "LED_035pc.ivcurve.csv",
}

data_names: list = list(data_paths.keys())


def get_ivcurve(name: str) -> pd.DataFrame:
    return pd.read_csv(data_paths[name], sep=";", decimal=".", skipinitialspace=True)
