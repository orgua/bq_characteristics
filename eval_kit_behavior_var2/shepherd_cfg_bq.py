
from shepherd_core.data_models import VirtualHarvesterConfig
from shepherd_core.data_models import VirtualSourceConfig


# baseline vsrc
# - feature-rollback to mid 2024 (core-lib v2024.8.2)
# - nominal params of modification of eval-board
cfg_bq25570_base = VirtualSourceConfig(
    name="BQ25570",
    harvester=VirtualHarvesterConfig(
        name="mppt_bq_solar",
        # rising=False,
        enable_linear_extrapolation=False,  # disable newer feature
        samples_n=1000,
        # TODO: fixes bug in CoreLib
        #  - samples_n is still default, so
        #  - voltage_step_mV = (5000 - 0) / 7 with 7 as sample_n (=8) - 1
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    C_intermediate_uF=100,
    V_intermediate_init_mV=4300,
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
        samples_n=1000,  # TODO: fixes bug in CoreLib
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    C_intermediate_uF=80,
    V_intermediate_init_mV=4300,
    V_intermediate_max_mV=5220,
    V_intermediate_enable_threshold_mV=4430,
    V_intermediate_disable_threshold_mV=4030,
    V_pwr_good_enable_threshold_mV=4430,
    V_pwr_good_disable_threshold_mV=4030,
    V_output_mV=1800,
    C_output_uF=23,
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