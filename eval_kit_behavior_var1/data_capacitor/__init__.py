from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent

paths_charge: dict = {
    "100uF MLCC1 run1": path_here / "cap1_s1_chg.csv",
    "100uF MLCC1 run2": path_here / "cap1_s2_chg.csv",
    "100uF MLCC2 run1": path_here / "cap2_s1_chg.csv",
    "100uF MLCC2 run2": path_here / "cap2_s2_chg.csv",
    "100uF Tantal run1": path_here / "cap3_s1_chg.csv",
    "100uF Tantal run2": path_here / "cap3_s2_chg.csv",
}
paths_discharge: dict = {
    "100uF MLCC1 run1": path_here / "cap1_s1_dis.csv",
    "100uF MLCC1 run2": path_here / "cap1_s2_dis.csv",
    "100uF MLCC2 run1": path_here / "cap2_s1_dis.csv",
    "100uF MLCC2 run2": path_here / "cap2_s2_dis.csv",
    "100uF Tantal run1": path_here / "cap3_s1_dis.csv",
    "100uF Tantal run2": path_here / "cap3_s2_dis.csv",
}
paths_selfdis: dict = {
    "100uF MLCC1": path_here / "cap1_selfdis.csv",
    "100uF MLCC2": path_here / "cap2_selfdis.csv",
    "100uF Tantal": path_here / "cap3_selfdis.csv",
}
# varying charging-durations
paths_selfvar: dict = {
    "100uF MLCC1,  10s charge@5V": path_here / "cap1_selfdis_charge010s.csv",
    "100uF MLCC1,  20s charge@5V": path_here / "cap1_selfdis_charge020s.csv",
    "100uF MLCC1,  50s charge@5V": path_here / "cap1_selfdis_charge050s.csv",
    "100uF MLCC1, 100s charge@5V": path_here / "cap1_selfdis_charge100s.csv",
    "100uF MLCC1, 200s charge@5V": path_here / "cap1_selfdis_charge200s.csv",
    "100uF MLCC1, 400s charge@5V": path_here / "cap1_selfdis_charge400s.csv",
    "100uF MLCC1, 800s charge@5V": path_here / "cap1_selfdis_charge800s.csv",
    "confirmation,  10s charge@5V": path_here / "cap1_selfdis_charge010s_check.csv",
}

paths_cyclic: dict = {
    "100uF MLCC1, 3V to 5V,  40 ms": path_here / "cap1_cycle_3V0_to_5V0_40ms.csv",
    "100uF MLCC1, 3V to 5V, 228 ms": path_here / "cap1_cycle_3V0_to_5V0_228ms.csv",
}

col_rename: dict = {"Time [s]": "time", "Dbg10": "voltage"}

data_charge: dict = {
    name: pd.read_csv(path, sep=",", decimal=".").rename(columns=col_rename)
    for name, path in paths_charge.items()
}
data_discharge: dict = {
    name: pd.read_csv(path, sep=",", decimal=".").rename(columns=col_rename)
    for name, path in paths_discharge.items()
}
data_selfdis: dict = {
    name: pd.read_csv(path, sep=",", decimal=".").rename(columns=col_rename)
    for name, path in paths_selfdis.items()
}
data_selfvar: dict = {
    name: pd.read_csv(path, sep=",", decimal=".").rename(columns=col_rename)
    for name, path in paths_selfvar.items()
}
data_cyclic: dict = {
    name: pd.read_csv(path, sep=",", decimal=".").rename(columns=col_rename)
    for name, path in paths_cyclic.items()
}
