"""Simulate charging and discharging of the capacitor-model integrated into shepherd.

- the capacitor-model is encapsulated in .update_cap_storage()
- only uses VirtualConverterModel-class to initialize parameters
"""

import numpy as np
import pandas as pd
from shepherd_core.commons import samplerate_sps_default
from shepherd_core.data_models import VirtualSourceConfig
from shepherd_core.data_models.content.virtual_source import ConverterPRUConfig
from shepherd_core.vsource import PruCalibration
from shepherd_core.vsource.virtual_source_model import VirtualConverterModel

cnv = VirtualConverterModel(
    cfg=ConverterPRUConfig.from_vsrc(
        data=VirtualSourceConfig(name="BQ25570", C_intermediate_uF=100),
    ),
    cal=PruCalibration(),
)


def shp_cap_sim(
    U_start_V: float,
    U_inp_V: float,
    R_inp_Ohm: float,
    runtime: float = 1,
) -> pd.DataFrame:
    """Wrong approach - as the power-calc is only acceptable for the boost-case"""
    cnv.V_mid_uV = U_start_V * 1e6
    cnv.P_out_fW = 0
    timestamps = np.arange(0.0, runtime, 1.0 / samplerate_sps_default)
    voltages = np.zeros(shape=len(timestamps))
    for idx in range(len(voltages)):
        cnv.P_inp_fW = cnv.V_mid_uV * 1e-6 * (U_inp_V - cnv.V_mid_uV * 1e-6) / R_inp_Ohm * 1e15
        voltages[idx] = cnv.update_cap_storage()

    result = pd.DataFrame(columns=["time", "voltage"])
    result["time"] = timestamps
    result["voltage"] = voltages * 1e-6
    return result
