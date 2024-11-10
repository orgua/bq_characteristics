from pathlib import Path

import numpy as np
from data_capacitor import data_charge
from capacitor_shepherd import shp_cap_sim
from matplotlib import pyplot as plt

runtime = 1

shp_cap1 = shp_cap_sim(U_start_V=0, U_inp_V=5.0, R_inp_Ohm=1000, runtime=runtime)

fig = plt.figure(figsize=(9, 8), layout="tight")

plt.plot(shp_cap1["time"], shp_cap1["voltage"], label="100uF shepherd (ideal)")
for name, data in data_charge.items():
    plt.plot(data["time"], data["voltage"], label=name)

plt.suptitle("Charging of Capacitor-Models (RC, 1k, 100uF)")
plt.xlabel("time [s]")
plt.ylabel("voltage [V]")
plt.xticks(np.arange(0.0, runtime + 0.1, 0.1))
plt.yticks(np.arange(0.0, 5.6, 0.5))
plt.ylim(bottom=0.0)  # , top=1.0)
plt.grid(True)
plt.legend(loc="lower right")
plt.tight_layout()
# force direct values on axis
for ax in fig.get_axes():
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.savefig(Path(__file__).with_suffix(".png"))
plt.close(fig)
