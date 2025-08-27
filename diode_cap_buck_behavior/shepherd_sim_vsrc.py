"""Simulate behavior of virtual source algorithms.

Slightly modified version of shepherd-core/vsource/virtual_source_simulation.py

The simulation recreates an observer-cape, the virtual Source and a virtual target
- input = hdf5-file with a harvest-recording
- output = optional as hdf5-file

The output file can be analyzed and plotted with shepherds tool suite.

NOTE: The Config is heavily optimized to match the 900mA BQ-behavior,
      BUT does not match the 400mA at all...
"""

from contextlib import ExitStack
from pathlib import Path

import numpy as np
import pandas as pd
from shepherd_core import CalibrationEmulator
from shepherd_core import Writer
from shepherd_core.commons import samplerate_sps_default
from shepherd_core.data_models import EnergyDType
from shepherd_core.data_models import VirtualSourceConfig
from shepherd_core.vsource import VirtualSourceModel
from shepherd_core.vsource.target_model import TargetABC
from tqdm import tqdm


def simulate_source(
    path_ivcurve: Path,
    target: TargetABC,
    config: VirtualSourceConfig,
    path_output: Path | None = None,
    runtime: float = 100,
) -> pd.DataFrame:
    """Simulate behavior of virtual source algorithms.

    FN returns the consumed energy of the target.
    """
    stack = ExitStack()
    ivcurve = pd.read_csv(path_ivcurve, sep=";", decimal=".", skipinitialspace=True)
    v_uV = 1e6 * ivcurve["Voltage [V]"].to_numpy()
    i_nA = 1e9 * ivcurve["Current [A]"].to_numpy()
    window_size = ivcurve.shape[0]

    samples_total = round(runtime * samplerate_sps_default)
    ivcurve_reps = np.ceil(samples_total / window_size)
    samples_total = round(ivcurve_reps * window_size)
    sample_interval_s = 1.0 / samplerate_sps_default
    time_s = np.arange(0.0, samples_total / samplerate_sps_default, sample_interval_s)
    cal_emu = CalibrationEmulator()

    if path_output:
        file_out = Writer(
            path_output,
            cal_data=cal_emu,
            mode="emulator",
            verbose=False,
            force_overwrite=True,
        )
        stack.enter_context(file_out)
        file_out.store_hostname("emu_sim_" + config.name)
        file_out.store_config(config.model_dump())
        cal_out = file_out.get_calibration_data()

    src = VirtualSourceModel(
        config,
        cal_emu,
        dtype_in=EnergyDType.ivcurve,
        log_intermediate=False,
        window_size=window_size,
    )
    print(f"dV_output_mV = {src.cnv.dV_enable_output_uV}")
    i_out_nA = 0
    e_out_Ws = 0.0
    stats_sample = 0
    stats_internal = np.empty((samples_total, 13))

    for _idx in tqdm(
        range(0, samples_total, window_size),
        total=ivcurve_reps,
        desc="sample",
        leave=False,
    ):
        _t = time_s[_idx : (_idx + window_size)]
        _v_out = np.zeros(shape=v_uV.shape)
        _i_out = np.zeros(shape=i_nA.shape)
        for _n in range(window_size):
            _v_out[_n] = src.iterate_sampling(
                V_inp_uV=int(v_uV[_n]),
                I_inp_nA=int(i_nA[_n]),
                I_out_nA=i_out_nA,
            )
            i_out_nA = target.step(int(_v_out[_n]), pwr_good=src.cnv.get_power_good())
            _i_out[_n] = i_out_nA

            if stats_internal is not None:
                stats_internal[stats_sample] = [
                    _t[_n],  # s
                    v_uV[_n] * 1e-6,
                    src.cnv.V_input_uV * 1e-6,
                    src.cnv.V_input_request_uV * 1e-6,  # V
                    src.hrv.voltage_set_uV * 1e-6,
                    src.cnv.V_mid_uV * 1e-6,
                    _v_out[_n] * 1e-6,
                    src.hrv.current_hold * 1e-9,  # A
                    src.hrv.current_delta * 1e-9,
                    i_out_nA * 1e-9,
                    src.cnv.P_inp_fW * 1e-15,  # W
                    src.cnv.P_out_fW * 1e-15,
                    src.cnv.get_power_good(),
                ]
                stats_sample += 1

        e_out_Ws += (_v_out * _i_out).sum() * 1e-15 * sample_interval_s
        if path_output:
            v_out = cal_out.voltage.si_to_raw(1e-6 * _v_out)
            i_out = cal_out.current.si_to_raw(1e-9 * _i_out)
            file_out.append_iv_data_raw(_t, v_out, i_out)

    stack.close()
    stats_internal = stats_internal[:stats_sample, :]
    return pd.DataFrame(
        stats_internal,
        columns=[
            "time",
            "V_ivcurve",
            "V_inp",
            "V_inp_Req",
            "V_cv_set",
            "V_cap",
            "V_out",
            "C_cv_hold",
            "C_cv_delta",
            "C_out",
            "P_inp",
            "P_out",
            "PwrGood",
        ],
    )
