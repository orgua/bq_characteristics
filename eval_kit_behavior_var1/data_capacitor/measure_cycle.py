import time

from smu import SMU

smu = SMU()

# pre-phase
smu.set_smu_to_vsource(smu.out, value_v=5.0, limit_i=0.5)
smu.set_smu_to_vsource(smu.inp, value_v=5.0, limit_i=0.5)
time.sleep(2)

# measure (set Logic Pro to trigger on edge)
smu.set_smu_to_vsource(smu.out, value_v=0.0, limit_i=0.5)

for iter in range(10):
    smu.set_smu_to_vsource(smu.inp, value_v=3.0, limit_i=0.5)
    time.sleep(1.0 / 160)
    smu.set_smu_to_vsource(smu.inp, value_v=5.0, limit_i=0.5)
    time.sleep(1.0 / 160)
