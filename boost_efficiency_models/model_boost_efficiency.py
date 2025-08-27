"""Model for boost efficiency - used to fit parameters to measurement date.

Sources:
- https://www.electronicdesign.com/technologies/power/article/21190563/boost-converter-efficiency-through-accurate-calculations
- slva372d.pdf - Basic Calculation of a Boost Converter's Power Stage
- sluuaa7a.pdf - BQ25570 EVM users guide
"""

from itertools import product
from pathlib import Path

import numpy as np


def efficiency_boost_model(
    V_In: float,
    I_In: float,
    V_Out: float,
    R_ind: float,
    L_ind: float,
    R_sw_ds: float,
    # Q_sw_gate: float,
    R_diode: float,
    V_diode_forward: float,
    I_ic_quiet: float,
    t_trans: float,  # t_rise + t_fall
) -> float:
    PL: dict = {}  # losses
    f_switch_max = 1e6
    # starting values
    eta = 0.9
    for _ in range(10):
        duty = 1 - V_In * eta / V_Out
        I_Out = I_In * (1 - duty)
        P_In = V_In * I_In
        # P_Out = V_Out * I_Out

        # dI_L = V_In * duty / (f_SW * L_L)
        # I_out_max = (I_sw_max - dI_L/2) * (1-duty)

        # conduction loss
        PL["induct_r"] = R_ind * I_In**2
        # R_DS = R_sw_ds + R_DS_delta * (V_Out - 4.2)
        PL["switch_r"] = R_sw_ds * duty * I_In**2
        PL["diode_r"] = R_diode * I_Out**2 + V_diode_forward * I_Out

        # quiescent current when IC is running
        PL["ic_quiet"] = I_ic_quiet * V_Out

        # switching loss - gate charge
        E_inductor = L_ind * (I_In**2) / 2
        f_switch = min(f_switch_max, P_In / E_inductor)  # TODO: just a guess
        # PL["switch_gate"] = Q_sw_gate * 0.7 * f_switch
        # TODO: P_GC is probably part of PL_IC

        PL["switch_trans"] = 1 / 2 * V_In * I_In * t_trans * f_switch

        p_loss = sum(PL.values())
        eta = max(0.01, (P_In - p_loss) / P_In)
    return eta


def efficiency_boost_fit(
    xdata: np.ndarray,
    R_ind: float,
    L_ind: float,
    R_sw_ds: float,
    # Q_sw_gate: float,
    R_diode: float,
    V_diode_forward: float,
    I_ic_quiet: float,
    t_trans: float,  # t_rise + t_fall
) -> np.ndarray:
    xlen = xdata.shape[0]
    result = np.zeros(xlen)
    for index in range(xlen):
        result[index] = efficiency_boost_model(
            V_In=xdata[index, 0],
            I_In=xdata[index, 1],
            V_Out=xdata[index, 2],
            # inductor
            R_ind=R_ind,
            L_ind=L_ind,
            # mosfet
            R_sw_ds=R_sw_ds,
            # Q_sw_gate=Q_sw_gate,
            # diode
            R_diode=R_diode,
            V_diode_forward=V_diode_forward,
            I_ic_quiet=I_ic_quiet,
            t_trans=t_trans,
        )
    return result


params_datasheet = {
    "R_ind": 0.360,
    "L_ind": 22e-6,
    "R_sw_ds": 0.7,
    # "Q_sw_gate":0.36e-9,
    "R_diode": 2.3,
    "V_diode_forward": 0,  # because of mosfet instead of diode
    "I_ic_quiet": 488e-9,
    "t_trans": 1e-9,
}
params_bound_low = {
    "R_ind": 1e-3,
    "L_ind": 1e-6,
    "R_sw_ds": 0.1,
    # "Q_sw_gate":0.36e-9,
    "R_diode": 0.3,
    "V_diode_forward": 0.0,
    "I_ic_quiet": 1e-9,
    "t_trans": 0.1e-9,
}
params_bound_high = {
    "R_ind": 2.0,
    "L_ind": 100e-6,
    "R_sw_ds": 2.0,
    # "Q_sw_gate":0.36e-9,
    "R_diode": 5.0,
    "V_diode_forward": 0.3,
    "I_ic_quiet": 800e-9,
    "t_trans": 20e-9,
}


def efficiency_boost_datasheet(
    V_In: float,
    I_In: float,
    V_Out: float,
) -> float:
    return efficiency_boost_model(
        V_In=V_In,
        I_In=I_In,
        V_Out=V_Out,
        **params_datasheet,
    )


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    i_inp = [10e-6, 100e-6]
    v_storage = [2.0, 3.0]

    fig = plt.figure(figsize=(10, 4), layout="tight")

    for _ii, _vs in product(i_inp, v_storage):
        vin: list[float] = []
        eta: list[float] = []
        for vcc_mV in range(100, round(_vs * 1e3), 10):
            V_IN = vcc_mV * 1e-3
            vin.append(V_IN)
            eta.append(efficiency_boost_datasheet(V_IN, _ii, _vs))
        plt.plot(vin, eta, label=f"VStor={_vs}V, i_inp={_ii * 1e6}uA")

    plt.xlabel("V_In [V]")
    plt.xticks([x / 10 for x in range(0, 31, 2)])
    plt.ylabel("efficiency [n]")
    plt.yticks([y / 10 for y in range(11)])
    plt.grid(visible=True)
    plt.legend(loc="lower right")
    # plt.show()
    plt.savefig(Path(__file__).with_suffix(".svg"))
    plt.close(fig)
