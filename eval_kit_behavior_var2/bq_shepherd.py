"""Simulate behavior of virtual source algorithms.

Slightly modified version of shepherd-core/vsource/virtual_source_simulation.py

The simulation recreates an observer-cape, the virtual Source and a virtual target
- input = hdf5-file with a harvest-recording
- output = optional as hdf5-file

The output file can be analyzed and plotted with shepherds tool suite.

NOTE: The Config is heavily optimized to match the 900mA BQ-behavior, BUT does not match the 400mA at all...
"""

from contextlib import ExitStack
from pathlib import Path

import numpy as np
import pandas as pd
from shepherd_core import CalibrationEmulator
from shepherd_core import Writer
from shepherd_core.commons import samplerate_sps_default
from shepherd_core.data_models import EnergyDType
from shepherd_core.data_models import VirtualHarvesterConfig
from shepherd_core.data_models import VirtualSourceConfig
from shepherd_core.vsource import VirtualSourceModel
from shepherd_core.vsource.target_model import TargetABC
from tqdm import tqdm

# baseline vsrc
# - feature-rollback to mid 2024 (core-lib v2024.8.2)
# - nominal params of modification of eval-board
cfg_bq25570_base = VirtualSourceConfig(
    name="BQ25570",
    harvester=VirtualHarvesterConfig(
        name="mppt_bq_solar",
        # rising=False,
        enable_linear_extrapolation=False,  # disable newer feature
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    C_intermediate_uF=100,
    V_intermediate_init_mV=4000,
    V_intermediate_max_mV=5220,
    V_intermediate_enable_threshold_mV=4430,
    V_intermediate_disable_threshold_mV=4030,
    V_pwr_good_enable_threshold_mV=4430,
    V_pwr_good_disable_threshold_mV=4030,
    V_output_mV=1800,
    C_output_uF=22,
)

# optimized vsrc
# - add newer extrapolation feature
# - further adapt to information gathered through recordings
# - add measured efficiencies
cfg_bq25570_eval = VirtualSourceConfig(
    name="BQ25570",
    harvester=VirtualHarvesterConfig(
        name="mppt_bq_solar",
        # rising=False,
        enable_linear_extrapolation=True,
        interval_ms=16650,  # from recording
        duration_ms=255,  # from recording
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    C_intermediate_uF=80,
    V_intermediate_init_mV=4000,
    V_intermediate_max_mV=5220,
    V_intermediate_enable_threshold_mV=4430,
    V_intermediate_disable_threshold_mV=4030,
    V_pwr_good_enable_threshold_mV=4430,
    V_pwr_good_disable_threshold_mV=4030,
    V_output_mV=1800,
    C_output_uF=22,
    interval_check_thresholds_ms=63.2,
    # add measured LUTs - the presets are too efficient
    # board_A_boost_VCap3V0
    LUT_input_efficiency=[
        [0.000, 0.001, 0.002, 0.004, 0.009, 0.018, 0.037, 0.075, 0.151, 0.273, 0.349, 0.500],
        [0.010, 0.010, 0.010, 0.012, 0.034, 0.077, 0.165, 0.339, 0.598, 0.620, 0.713, 0.730],
        [0.050, 0.052, 0.057, 0.066, 0.086, 0.133, 0.228, 0.419, 0.798, 0.802, 0.795, 0.780],
        [0.150, 0.278, 0.282, 0.291, 0.309, 0.344, 0.358, 0.553, 0.834, 0.835, 0.839, 0.835],
        [0.280, 0.397, 0.632, 0.647, 0.677, 0.738, 0.800, 0.822, 0.863, 0.856, 0.842, 0.850],
        [0.350, 0.516, 0.620, 0.798, 0.836, 0.839, 0.845, 0.857, 0.877, 0.828, 0.688, 0.825],
        [0.400, 0.582, 0.660, 0.802, 0.834, 0.841, 0.855, 0.881, 0.889, 0.889, 0.874, 0.880],
        [0.460, 0.650, 0.747, 0.812, 0.843, 0.848, 0.859, 0.880, 0.893, 0.895, 0.888, 0.882],
        [0.500, 0.690, 0.795, 0.841, 0.866, 0.874, 0.889, 0.890, 0.891, 0.895, 0.892, 0.880],
        [0.520, 0.710, 0.789, 0.852, 0.877, 0.884, 0.895, 0.900, 0.897, 0.894, 0.888, 0.881],
        [0.530, 0.770, 0.806, 0.834, 0.875, 0.883, 0.895, 0.901, 0.899, 0.895, 0.895, 0.879],
        [0.550, 0.800, 0.824, 0.848, 0.883, 0.890, 0.901, 0.906, 0.903, 0.898, 0.900, 0.885],
    ],
    LUT_input_V_min_log2_uV=17,
    LUT_input_I_min_log2_nA=13,
    # board_B_buck_VCap3.25V
    LUT_output_efficiency=[
        0.100,
        0.282,
        0.579,
        0.715,
        0.795,
        0.833,
        0.841,
        0.853,
        0.861,
        0.866,
        0.869,
        0.870,
    ],
    LUT_output_I_min_log2_nA=10,
)


def simulate_source(
    path_ivcurve: Path,
    target: TargetABC,
    config: VirtualSourceConfig = cfg_bq25570_eval,
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
    stats_internal = np.empty((samples_total, 12))

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
    stats_internal = pd.DataFrame(
        stats_internal,
        columns=[
            "time",
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
    return stats_internal
