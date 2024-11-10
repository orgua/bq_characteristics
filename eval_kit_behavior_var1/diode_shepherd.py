import math
from contextlib import suppress

import numpy as np
import pandas as pd
from shepherd_core.vsource.target_model import TargetABC


class DiodeTarget(TargetABC):
    """Copy of shepherd-core with two bugfixes"""

    def __init__(
        self,
        V_forward_V: float,
        I_forward_A: float,
        R_Ohm: float,
        *,
        controlled: bool = False,
    ) -> None:
        if R_Ohm <= 1e-3:
            raise ValueError("Resistance must be greater than 1 mOhm.")
        if V_forward_V <= 0.2:
            raise ValueError("Forward-Voltage of diode must be greater than 200 mV.")
        if I_forward_A <= 0:
            raise ValueError("Forward-current of diode must be greater than 0 A.")

        k = 1.380649e-23  # boltzmann
        q = 1.6021766e-19  # elementary charge
        TJ = 100 + 273.15  # junction temperature

        V_T = k * TJ / q  # thermal voltage
        n = 2  # ideality factor
        self.c1 = V_T * n
        # NOTE: math.expm1(x) = math.exp(x) - 1 = e^x -1
        self.I_S = I_forward_A / math.expm1(V_forward_V / self.c1)  # scale current
        self.R_Ohm = R_Ohm
        self.ctrl = controlled

    def step(self, voltage_uV: int, *, pwr_good: bool) -> float:
        if pwr_good or not self.ctrl:
            V_CC = voltage_uV * 1e-6
            V_D = V_CC / 2
            I_R = I_D = 0
            # there is no direct formular, but this iteration converges fast
            for _ in range(10):
                # low voltages tend to produce log(x<0)=err
                with suppress(ValueError):
                    V_D = self.c1 * math.log(1 + (V_CC - V_D) / (self.R_Ohm * self.I_S))
                # both currents are positive and should be identical
                I_R = max(0.0, (V_CC - V_D) / self.R_Ohm)
                I_D = max(0.0, self.I_S * math.expm1(V_D / self.c1))
                with suppress(ZeroDivisionError):
                    if abs(I_R / I_D - 1) < 1e-6:
                        break
                # take mean of both currents and determine a new V_D
                V_D = V_CC - self.R_Ohm * (I_R + I_D) / 2
            return 1e9 * (I_R + I_D) / 2  # = nA
        return 0


def shp_diode_target_sim(diode: DiodeTarget, U_start_V: float, U_end_V: float) -> pd.DataFrame:
    voltages = np.arange(U_start_V, U_end_V, 1e-3)
    currents = np.zeros(shape=len(voltages))
    for idx in range(1, len(voltages)):
        currents[idx] = diode.step(voltage_uV=int(voltages[idx] * 1e6), pwr_good=True) * 1e-9
    result = pd.DataFrame(columns=["voltage", "current"])
    result["voltage"] = voltages
    result["current"] = currents
    return result


def shp_diode_sim(U_start_V: float, U_end_V: float) -> pd.DataFrame:
    V_drop = 0.3
    R_diode = 1e-3
    voltages = np.arange(U_start_V, U_end_V, 1e-3)
    currents = np.zeros(shape=len(voltages))
    for idx in range(1, len(voltages)):
        currents[idx] = max(0.0, voltages[idx] - V_drop) / R_diode
    result = pd.DataFrame(columns=["voltage", "current"])
    result["voltage"] = voltages
    result["current"] = currents
    return result
