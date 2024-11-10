from pathlib import Path

import numpy as np
from shepherd_core import Reader

path_here = Path(__file__).parent.absolute()

paths = [
    path_here / "LED_003pc.h5",
    path_here / "LED_004pc.h5",
    path_here / "LED_005pc.h5",
    path_here / "LED_006pc.h5",
    path_here / "LED_008pc.h5",
    path_here / "LED_010pc.h5",
    path_here / "LED_012pc.h5",
    path_here / "LED_014pc.h5",
    path_here / "LED_015pc.h5",
    path_here / "LED_016pc.h5",
    path_here / "LED_018pc.h5",
    path_here / "LED_020pc.h5",
    path_here / "LED_022pc.h5",
]

for path in paths:
    with Reader(path, verbose=False) as reader:
        samples = reader.get_window_samples()
        repetitions = int(reader.ds_time.shape[0] / samples)
        curve_t = reader.ds_time[0:samples]
        curve_v = np.zeros(samples)
        curve_i = np.zeros(samples)
        for _n in range(repetitions):
            start = _n * samples
            end = start + samples
            curve_v += reader.ds_voltage[start:end]
            curve_i += reader.ds_current[start:end]
        cal = reader.get_calibration_data()
        curve_v = cal.voltage.raw_to_si(curve_v) / repetitions
        curve_i = cal.current.raw_to_si(curve_i) / repetitions

    separator = "; "
    csv_name = path.stem.split(".")[0]
    csv_path = path.with_stem(csv_name).with_suffix(".ivcurve.csv")
    with csv_path.open("w", encoding="utf-8-sig") as csv_file:
        csv_file.write(separator.join(["Time [s]", "Voltage [V]", "Current [A]"]) + "\n")
        for idx in range(samples):
            csv_file.write(
                separator.join([str(curve_t[idx]), str(curve_v[idx]), str(curve_i[idx])]) + "\n"
            )
        csv_file.write("\n")
