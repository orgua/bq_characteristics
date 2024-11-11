from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent.absolute()

data_paths: dict = {
    "LED  3 %": path_here / "LED_003pc.ivcurve.csv",
    "LED  4 %": path_here / "LED_004pc.ivcurve.csv",
    "LED  5 %": path_here / "LED_005pc.ivcurve.csv",
    "LED  6 %": path_here / "LED_006pc.ivcurve.csv",
    "LED  8 %": path_here / "LED_008pc.ivcurve.csv",
    "LED 10 %": path_here / "LED_010pc.ivcurve.csv",
    "LED 12 %": path_here / "LED_012pc.ivcurve.csv",
    "LED 14 %": path_here / "LED_014pc.ivcurve.csv",
    "LED 15 %": path_here / "LED_015pc.ivcurve.csv",
    "LED 16 %": path_here / "LED_016pc.ivcurve.csv",
    "LED 18 %": path_here / "LED_018pc.ivcurve.csv",
    "LED 20 %": path_here / "LED_020pc.ivcurve.csv",
    "LED 22 %": path_here / "LED_022pc.ivcurve.csv",
}

data_names: list = list(data_paths.keys())


def get_ivcurve(name: str) -> pd.DataFrame:
    return pd.read_csv(data_paths[name], sep=";", decimal=".", skipinitialspace=True)
