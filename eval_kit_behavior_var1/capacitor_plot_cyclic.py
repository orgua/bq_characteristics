from pathlib import Path

import numpy as np

from matplotlib import pyplot as plt

from eval_kit_behavior_var1.data_capacitor import data_cyclic

runtime = 1

fig = plt.figure(figsize=(9, 8), layout="tight")

for name, data in data_cyclic.items():
    plt.plot(data["time"], data["voltage"], label=name)

plt.suptitle("Cyclic Charging of Capacitor-Models (3V..5V, RC, 1k, 100uF)")
plt.xlabel("time [s]")
plt.ylabel("voltage [V]")
plt.xticks(np.arange(0.0, runtime + 0.1, 0.1))
plt.yticks(np.arange(0.0, 5.6, 0.5))
plt.ylim(bottom=2.5)  # , top=1.0)
plt.xlim(left=0.0, right=0.6)
plt.grid(True)
plt.legend(loc="lower right")
plt.tight_layout()
# force direct values on axis
for ax in fig.get_axes():
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.savefig(Path(__file__).with_suffix(".png"))
plt.close(fig)
