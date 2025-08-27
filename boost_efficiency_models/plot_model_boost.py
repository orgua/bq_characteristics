from itertools import product
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from model_boost_efficiency import efficiency_boost_datasheet

# config - copied from /eval_kit_efficiency/extract_LUTs_boost.py

v_cap = [2.50, 2.75, 3.00, 3.25]

LUT_input_V_min_log2_uV = 17
LUT_input_I_min_log2_nA = 13

i_inp_min = (2**LUT_input_I_min_log2_nA) * 1e-9
i_inp_mid = [i_inp_min / 2 * 2**x for x in range(12)]

v_inp_min = (2**LUT_input_V_min_log2_uV) * 1e-6
v_inp_mid = [v_inp_min / 2 + v_inp_min * x for x in range(12)]

for _vc in v_cap:
    # grid_xy = np.asarray(_data["LUT_input_efficiency"])
    # plt.plot(grid_xy)
    ii_iter = np.arange(12)  # column, i_inp
    vi_iter = np.arange(12)  # row; v_inp
    eta = np.zeros(shape=(12, 12))
    for _ii, _vi in product(ii_iter, vi_iter):
        i_inp = i_inp_mid[_ii]
        v_inp = v_inp_mid[_vi]
        v_stor = _vc
        eta[_ii, _vi] = efficiency_boost_datasheet(v_inp, i_inp, v_stor)

    fig = plt.figure(figsize=(9, 8), layout="tight")
    plt.pcolormesh(ii_iter, vi_iter, eta, vmin=0.0, vmax=1.0, cmap="RdYlGn")
    plt.colorbar()
    plt.suptitle(f"Efficiency Boost-Model VCap={_vc}V")
    plt.xlabel("I_Input [n]")
    plt.ylabel("V_Input [n]")
    plt.axis("equal")
    suffix = f".VCap{str(round(_vc, 2)).replace('.', 'V')}.png"
    plt.savefig(Path(__file__).with_suffix(suffix), bbox_inches="tight")
    plt.close(fig)
