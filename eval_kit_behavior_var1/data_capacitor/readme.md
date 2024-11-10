# Measuring capacitor behavior

Capacitor1: 100 uF, 20%, 6.3 V, MLCC, Taiyo Yuden, JMK316ABJ107ML-T
Capacitor2: 100 uF, 20%, 6.3 V, MLCC, Taiyo Yuden, JMK316ABJ107ML-T
Capacitor3: 100 uF, 20%, 6.3 V, Tantal, AVX TAJB107M006RNJ
Resistor: 1 kOhm (cherrypick, measured 1000 Ohm)

Measured with

- SMU - Voltage Source with programmed switch
- Logic Analyzer with analog input, 2 MOhm Impedance
- roomtemp is 22°C

## Charge / Discharge

- let start-voltage settle for 20s
- switch & measure

## SelfDischarge

- run for 100s
- LogicPro has 2 MOhm Impedance
- SMU was connected & charged via 1k and switched to 100pA Current-Supply for the measurement (turning it off discharged the cap quickly)

## SelfDischarge 2

tldr: invalid results - probably due to warm-up of measurement equipment

- similar to prior experiment the discharge was observed for 100s
- the pre-charge-duration was varied from 10s to 800s
- due to the constantly increasing discharge-rate the first measurement was rechecked and invalidated all results!

## Cyclic Charging

- cap 1 was charged to 5 V then
- cyclic discharged to 3 V and charged to 5 V
- the duration between switching states was varied

## Analysis

- MLCC seem to fit a 73-75 uF Cap, 5.0V *(1-%e^(-0.1s/(1e3 Ohm * 73e-6 F))) = 3.73 V;
- The Tantal is a good fit for 100uF, 5.0V *(1-%e^(-0.1s/(1e3 Ohm * 100e-6 F))) = 3.16 V;
