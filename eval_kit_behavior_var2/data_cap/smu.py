from keithley2600 import Keithley2600
from keithley2600.keithley_driver import Keithley2600Base
from keithley2600.keithley_driver import KeithleyClass


class SMU:
    def __init__(self, ip: str = "10.0.0.24", pwrline_cycles: float = 8, mode_4wire: bool = True):
        self.kth: Keithley2600Base = Keithley2600(f"TCPIP0::{ip}::INSTR")
        self.kth.reset()
        self.inp: KeithleyClass = self.kth.smua
        self.out: KeithleyClass = self.kth.smub
        self.pwrline_cycles: float = pwrline_cycles
        self.mode_4wire: bool = mode_4wire

    def set_smu_auto_on(self, smu: KeithleyClass) -> None:
        smu.source.output = smu.OUTPUT_ON
        smu.measure.autozero = smu.AUTOZERO_AUTO
        smu.measure.autorangev = smu.AUTORANGE_ON
        smu.measure.autorangei = smu.AUTORANGE_ON
        smu.measure.nplc = self.pwrline_cycles

    def set_smu_off(self, smu: KeithleyClass) -> None:
        smu.source.output = smu.OUTPUT_OFF

    def set_smu_to_vsource(
        self,
        smu: KeithleyClass,
        value_v: float,
        limit_i: float,
    ) -> float:
        value_v = min(max(value_v, 0.0), 5.5)
        limit_i = min(max(limit_i, -0.080), 0.080)
        smu.sense = smu.SENSE_REMOTE if self.mode_4wire else smu.SENSE_LOCAL
        smu.source.levelv = value_v
        smu.source.limiti = limit_i
        smu.source.func = smu.OUTPUT_DCVOLTS
        smu.source.autorangev = smu.AUTORANGE_ON
        self.set_smu_auto_on(smu)
        return value_v

    def set_smu_to_isource(
        self,
        smu: KeithleyClass,
        value_i: float,
        limit_v: float = 5.0,
    ) -> float:
        value_i = min(max(value_i, -0.080), 0.080)
        limit_v = min(max(limit_v, 0.0), 5.5)
        smu.sense = smu.SENSE_REMOTE if self.mode_4wire else smu.SENSE_LOCAL
        smu.source.leveli = value_i
        smu.source.limitv = limit_v
        smu.source.func = smu.OUTPUT_DCAMPS
        smu.source.autorangei = smu.AUTORANGE_ON
        self.set_smu_auto_on(smu)
        return value_i
