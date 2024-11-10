import time
from itertools import product

import pandas as pd
from smu_class import SMU
from tqdm import tqdm


def smu_measure_boost(
    vs_input: list[float], is_input: list[float], vs_output: list[float]
) -> pd.DataFrame:
    """Measures states of BOOST-Converter at a specific set-point."""
    smu = SMU()
    results: list = []  # np.zeros(shape=(len(vs_input) * len(vs_output) * len(is_input), 8))
    total = len(vs_input) * len(vs_output) * len(is_input)
    for index, (v_out, v_inp, i_inp) in tqdm(
        enumerate(product(vs_output, vs_input, is_input)),
        total=total,
    ):
        # check if set-point is valid
        v_oc = v_inp * (100 / 78)
        if v_oc > v_out:
            print("SKIP - V_IN > V_OUT")
            continue

        # prepare set-point
        smu.set_smu_to_vsource(smu.out, value_v=v_out, limit_i=10 * i_inp)
        smu.set_smu_to_isource(smu.inp, value_i=i_inp, limit_v=v_oc)

        # wait for VOC-Measurement
        is_reached = False
        time_start = time.time()
        while not is_reached:
            iim = smu.inp.measure.i()
            is_reached = abs(iim) < 0.5 * i_inp
            if time.time() - time_start > 2 * 16:
                print("SKIP - Timeout while looking for VOC")
                break
        if not is_reached:
            continue

        # limit & autorange input for maximum resolution
        i_theory = 0.10 * i_inp * v_inp / v_out
        for _ in range(4):
            time.sleep(1)
            iom = smu.out.measure.i()
            print(f"AUTORANGING - measured {iom} A, theory_min = {i_theory} A")
            iom = max(abs(iom), i_theory)
            smu.out.source.limiti = min(max(1.4 * iom, -0.080), 0.080)
            smu.out.measure.autorangei = smu.inp.AUTORANGE_ON

        # give time to stabilize, measure & store
        time.sleep(1)
        time_start = time.time()
        result = []
        while time.time() < time_start + 5:
            vim = smu.inp.measure.v()
            iim = smu.inp.measure.i()
            vom = smu.out.measure.v()
            iom = smu.out.measure.i()

            # store results
            p_inp = vim * iim
            p_out = vom * max(0.0, -iom)
            try:
                eta = p_out / p_inp
            except ZeroDivisionError:
                continue
            result = [v_out, v_inp, i_inp, vim, iim, vom, iom, eta]
            results.append(result)
        print(result)
    smu.set_smu_off(smu.inp)
    smu.set_smu_off(smu.out)
    return pd.DataFrame(
        data=results,
        columns=["V_out_nom", "V_inp_nom", "I_inp_nom", "V_inp", "I_inp", "V_out", "I_out", "eta"],
        dtype=float,  # np.float256 ?
    )


def smu_measure_buck(v_input: list, v_output: float, i_output: list) -> pd.DataFrame:
    """Measures states of BUCK-Converter at specific set-points."""
    smu = SMU()
    results: list = []
    total = len(v_input) * len(i_output)

    for _, (v_inp, i_out) in tqdm(enumerate(product(v_input, i_output)), total=total):
        # prepare set-point
        smu.set_smu_to_vsource(smu.inp, value_v=v_inp, limit_i=20 * i_out)
        time.sleep(2)
        # enable load
        smu.set_smu_to_isource(smu.out, value_i=-i_out, limit_v=2.0)

        # stabilize capacitor-voltage
        time_start = time.time()
        is_reached = False
        while not is_reached:
            time.sleep(1)
            vim = smu.inp.measure.v()
            is_reached = abs(v_inp / vim - 1) < 0.01  # %
            if time.time() - time_start > 60:
                print(f"SKIP - Timeout while stabilizing, got {vim} V instead of {v_inp}")
                break

        # limit & autorange input for maximum resolution
        i_theory = i_out * 1.8 / v_inp / 0.90
        for _ in range(5):
            time.sleep(1)
            iim = smu.inp.measure.i()
            print(f"AUTORANGING - measured {iim} A, theory_min = {i_theory} A")
            iim = max(abs(iim), i_theory)
            smu.inp.source.limiti = min(max(1.4 * iim, -0.080), 0.080)
            smu.inp.measure.autorangei = smu.inp.AUTORANGE_ON

        # measure, verify, store
        counter = 0
        time_start = time.time()
        while counter < 10:
            vim = smu.inp.measure.v()
            vom = smu.out.measure.v()
            iim = smu.inp.measure.i()
            iom = smu.out.measure.i()

            is_reached = abs(vim / v_inp - 1) < 0.03 or abs(vim - v_inp) < 0.05  # % & V
            is_reached &= iim > 0
            is_reached &= abs(vom / v_output - 1) < 0.05  # %
            is_reached &= abs(iom / i_out + 1) < 0.05  # %

            p_inp = vim * iim
            p_out = vom * max(0.0, -iom)
            try:
                eta = p_out / p_inp
            except ZeroDivisionError:
                continue
            result = [v_inp, i_out, vim, iim, vom, iom, eta]

            is_reached &= eta >= 0.0
            is_reached &= eta <= 1.0

            # store results
            results.append(result)

            if time.time() - time_start > 60:
                print(f"SKIP - Timeout while measuring (n={counter}, last: {result}")
                break
            if not is_reached:
                # do not count invalid measurements
                continue
            counter += 1
        smu.set_smu_off(smu.out)
        print(result)

    smu.set_smu_off(smu.inp)
    smu.set_smu_off(smu.out)
    return pd.DataFrame(
        data=results,
        columns=["V_inp_nom", "I_out_nom", "V_inp", "I_inp", "V_out", "I_out", "eta"],
        dtype=float,  # np.float256 ?
    )
