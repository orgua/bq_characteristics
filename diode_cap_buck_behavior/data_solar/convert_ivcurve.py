"""Take hdf5-curves and convert them to csv.

NOTE: the generated ivcurves were manually altered afterward
 - remove first line (from previous ivcurve)
 - remove next lines with max voltage (>5V)
"""

from pathlib import Path

import numpy as np
from shepherd_core import Reader

path_here = Path(__file__).parent.absolute()

paths = [
    path_here / "LED_020pc.h5",
    path_here / "LED_021pc.h5",
    path_here / "LED_022pc.h5",
    path_here / "LED_023pc.h5",
    path_here / "LED_024pc.h5",
    path_here / "LED_025pc.h5",
    path_here / "LED_026pc.h5",
    path_here / "LED_027pc.h5",
    path_here / "LED_028pc.h5",
    path_here / "LED_029pc.h5",
    path_here / "LED_030pc.h5",
    path_here / "LED_031pc.h5",
    path_here / "LED_032pc.h5",
    path_here / "LED_033pc.h5",
    path_here / "LED_034pc.h5",
    path_here / "LED_035pc.h5",
]

cutoff_bin = list(range(90, 50, -2))

for _i, path in enumerate(paths):
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

    # fix spike at t0 and begin of current-curve
    for _j in range(cutoff_bin[_i] - 1, -1, -1):
        curve_i[_j] = max(0.0, float((1 + 1 / 4) * curve_i[_j + 1] - curve_i[_j + 5] / 4))

    # fix voltage-ramp
    curve_v[curve_v > 5.0] = 0.0
    curve_v[0 : curve_v.argmax()] = np.max(curve_v)

    separator = "; "
    csv_name = path.stem.split(".")[0]
    csv_path = path.with_stem(csv_name).with_suffix(".ivcurve.csv")
    if csv_path.exists():
        continue
    with csv_path.open("w", encoding="utf-8-sig") as csv_file:
        csv_file.write(separator.join(["Time [s]", "Voltage [V]", "Current [A]"]) + "\n")
        for idx in range(samples):
            csv_file.write(
                separator.join([str(curve_t[idx]), str(curve_v[idx]), str(curve_i[idx])]) + "\n"
            )
        csv_file.write("\n")
