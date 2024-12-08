from shepherd_core.data_models import VirtualHarvesterConfig
from shepherd_core.data_models import VirtualSourceConfig

# baseline vsrc
# - feature-rollback to mid 2024 (core-lib v2024.8.2)
# - nominal params of modification of eval-board
cfg_bq25570_base = VirtualSourceConfig(
    name="BQ25570",
    harvester=VirtualHarvesterConfig(
        name="cv20",  # just the preset
        enable_linear_extrapolation=False,  # disable newer feature
        samples_n=900,
        # TODO: fixes bug in CoreLib
        #  - samples_n is still default, so
        #  - voltage_step_mV = (5000 - 0) / 7 with 7 as sample_n (=8) - 1
        voltage_mV=4900,
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    enable_boost=False,
    V_input_drop_mV=400,
    R_input_mOhm=100,
    LUT_input_efficiency= 12 * [12 * [1.00]],  # might be irrelevant
    # below is unchanged config from _var3
    C_intermediate_uF=100,
    V_intermediate_init_mV=4300,
    V_intermediate_max_mV=5220,
    V_intermediate_enable_threshold_mV=2400,
    V_intermediate_disable_threshold_mV=2030,  # difference to _var2
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
        name="cv20",
        enable_linear_extrapolation=True,
        samples_n=900,  # TODO: fixes bug in CoreLib
        voltage_mV=4800,
    ),
    enable_feedback_to_hrv=False,  # disable newer feature
    # eval board spec & modification
    enable_boost=False,
    V_input_drop_mV=400,
    R_input_mOhm=5000,
    LUT_input_efficiency=12 * [12 * [1.00]],  # might be irrelevant
    # below is unchanged config from _var3
    C_intermediate_uF=76.0,
    # Voltage Bias of Cap:
    # 79.8 uF @ 3.8 V
    # 67.2 uF @ 5.2 V
    V_intermediate_init_mV=4300,
    V_intermediate_max_mV=5220,
    V_intermediate_enable_threshold_mV=2400,
    V_intermediate_disable_threshold_mV=2030,  # difference to _var2
    V_pwr_good_enable_threshold_mV=4430,
    V_pwr_good_disable_threshold_mV=4030,
    V_output_mV=1800,
    C_output_uF=15,  # Enable-Drop is ~ 130 mV
    interval_check_thresholds_ms=63.2,
    # add measured LUTs - the presets are too efficient
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
