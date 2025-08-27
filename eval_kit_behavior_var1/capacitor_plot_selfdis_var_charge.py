from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from eval_kit_behavior_var1.data_capacitor import data_selfvar

runtime = 100

fig = plt.figure(figsize=(9, 8), layout="tight")

for name, data in data_selfvar.items():
    plt.plot(data["time"], data["voltage"], label=name)

plt.suptitle("Self-Discharge of 100 uF MLCC1 Capacitor")
plt.xlabel("time [s]")
plt.ylabel("voltage [V]")
plt.xticks(np.arange(0.0, runtime + 0.1, 5))
plt.yticks(np.arange(0.0, 5.6, 0.2))
plt.ylim(bottom=1.5, top=5.0)
# plt.yscale("log")
plt.grid(visible=True)
plt.legend(loc="upper right")
plt.tight_layout()
# force direct values on axis
for ax in fig.get_axes():
    #    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.savefig(Path(__file__).with_suffix(".png"))

plt.ylim(bottom=1.6, top=2.0)
# plt.yscale("log")
plt.xlim(left=90, right=100)
plt.savefig(Path(__file__).with_suffix(".detail.png"))
plt.close(fig)
