import time

from smu import SMU

smu = SMU()

# pre-phase
smu.set_smu_to_vsource(smu.out, value_v=5.0, limit_i=0.5)
smu.set_smu_to_vsource(smu.inp, value_v=0.0, limit_i=0.5)
time.sleep(20)

# measure (set Logic Pro to trigger on edge)
smu.set_smu_to_vsource(smu.out, value_v=0.0, limit_i=0.5)
smu.set_smu_to_vsource(smu.inp, value_v=5.0, limit_i=0.5)
# smu.set_smu_to_isource(smu.inp, value_i=1e-10, limit_v=5.0)
time.sleep(2)
