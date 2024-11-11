from pathlib import Path

import pandas as pd
from bq_shepherd import simulate_source
from matplotlib import pyplot as plt
from shepherd_core.vsource import ResistiveTarget

from eval_kit_behavior_var1.data_bq import get_bq_analog
from eval_kit_behavior_var1.data_bq import get_bq_digital

# config - mainly for sim
path_here = Path(__file__).parent
path_input = path_here / "data_solar/solar-iv-900mA.ivcurve.csv"
target = ResistiveTarget(R_Ohm=983, controlled=False)
eval_runtime = 20

# open eval-data
eval_stats = get_bq_analog("LED  900mA, 1000R Load")
eval_pwrgd = get_bq_digital("LED  900mA, 1000R Load")
# allow visualisation for digital data
eval_d2 = eval_pwrgd.iloc[:-1, :]
eval_d2["Time [s]"] = eval_pwrgd["Time [s]"].iloc[1:].reset_index(drop=True) - 10e-9
eval_pwrgd = (
    pd.concat([eval_pwrgd, eval_d2], axis=0, ignore_index=True)
    .sort_values(by=["Time [s]"])
    .reset_index(drop=True)
)

# run simulation
sim_stats = simulate_source(
    target=target,
    path_ivcurve=path_input,
    runtime=eval_runtime,
    # path_output=file_output,
)

# Align data
# sim_stats["time"] = sim_stats["time"] + 21.45
eval_stats["Time [s]"] = eval_stats["Time [s]"] - 21.48
eval_pwrgd["Time [s]"] = eval_pwrgd["Time [s]"] - 21.48

# shorten timeframe
eval_runtime = min(eval_runtime, sim_stats["time"].max())
eval_stats = eval_stats.loc[eval_stats["Time [s]"] <= eval_runtime]
eval_stats = eval_stats.loc[eval_stats["Time [s]"] >= 0.0]
eval_pwrgd = eval_pwrgd.loc[eval_pwrgd["Time [s]"] <= eval_runtime]
eval_pwrgd = eval_pwrgd.loc[eval_pwrgd["Time [s]"] >= 0.0]
sim_stats = sim_stats.loc[sim_stats["time"] <= eval_runtime]
sim_stats = sim_stats.loc[sim_stats["time"] >= 0.0]

# Visualize
fig, axs = plt.subplots(5, 1, sharex="all", figsize=(20, 4 * 6), layout="tight")
fig.suptitle(f"BQ25570-Sim with Inp={path_input.stem}")  # , E={e_out_Ws} Ws")
axs[0].set_ylabel("Voltage Input [V]")
axs[0].plot(sim_stats["time"], sim_stats["V_inp"])
axs[0].plot(eval_stats["Time [s]"], eval_stats["V_IN"], alpha=0.7)
axs[0].legend(["Sim", "Eval"], loc="upper right")

axs[1].set_ylabel("Voltage Storage [V]")
axs[1].plot(sim_stats["time"], sim_stats["V_cap"])
axs[1].plot(eval_stats["Time [s]"], eval_stats["V_BAT"], alpha=0.7)
axs[1].legend(["Sim", "Eval"], loc="upper right")

axs[2].set_ylabel("Voltage Output [V]")
axs[2].plot(sim_stats["time"], sim_stats["V_out"])
axs[2].plot(eval_stats["Time [s]"], eval_stats["V_OUT"], alpha=0.7)
axs[2].legend(["Sim", "Eval"], loc="upper right")

axs[3].set_ylabel("PwrGood [n]")
axs[3].plot(sim_stats["time"], 0.9 * sim_stats["PwrGood"])
axs[3].plot(eval_pwrgd["Time [s]"], 0.9 * eval_pwrgd["BAT_OK"] + 1.0)
axs[3].legend(["Sim", "Eval"], loc="upper right")

axs[4].set_ylabel("Power Sim [mW]")
axs[4].plot(sim_stats["time"], 1e3 * sim_stats["P_inp"])
axs[4].plot(sim_stats["time"], 1e3 * sim_stats["P_out"], alpha=0.7)
axs[4].legend(["P_inp (Sim)", "P_out (Sim)"], loc="upper right")

axs[4].set_xlabel("Runtime [s]")

for ax in axs:
    # deactivates offset-creation for ax-ticks
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)

plt.savefig(Path(__file__).with_suffix(".png"))
# plt.savefig(Path(__file__).with_suffix(".svg"))
plt.close(fig)
plt.clf()

print(f"PowerGood - Ratio: {sim_stats["PwrGood"].sum() / sim_stats["PwrGood"].shape[0]:.3f}")
