from pathlib import Path

import numpy as np
from diode_shepherd import DiodeTarget
from diode_shepherd import shp_diode_sim
from diode_shepherd import shp_diode_target_sim
from matplotlib import pyplot as plt

U_start = -1.0
U_end = 3.0

# simulate shepherd @ 3 V, 1 mA for 1 s
shp1 = shp_diode_sim(
    U_start_V=U_start,
    U_end_V=U_end,
)
shp2 = shp_diode_target_sim(
    diode=DiodeTarget(V_forward_V=0.3, I_forward_A=20e-3, R_Ohm=1),
    U_start_V=U_start,
    U_end_V=U_end,
)
shp3 = shp_diode_target_sim(
    diode=DiodeTarget(V_forward_V=0.3, I_forward_A=20e-3, R_Ohm=10.0),
    U_start_V=U_start,
    U_end_V=U_end,
)


fig = plt.figure(figsize=(9, 8), layout="tight")

plt.plot(shp1["voltage"], shp1["current"], label="vsrc-diode shepherd (V-drop)")
plt.plot(shp2["voltage"], shp2["current"], label="diode-Target shepherd (1 Ohm)")
plt.plot(shp3["voltage"], shp3["current"], label="diode-Target shepherd (10 Ohm)")

plt.suptitle("Characteristic of Diode-Models")
plt.xlabel("voltage [V]")
plt.ylabel("current [A]")
plt.xticks(np.arange(U_start, U_end, 0.5))
plt.yticks(np.arange(0, 1, 0.2))
plt.ylim(bottom=0.0, top=1.0)
plt.grid(visible=True)
plt.legend(loc="lower right")
plt.tight_layout()
# force direct values on axis
for ax in fig.get_axes():
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.savefig(Path(__file__).with_suffix(".svg"))
plt.close(fig)
