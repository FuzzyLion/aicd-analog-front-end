# Design notes

Both stages are inverting amplifiers around a 0.9 V common-mode reference, and both use the same OPAMP. This page explains how I picked the values. All numbers come from the simulated schematic baseline in the report.

## OPAMP

The first stage is an NMOS differential pair (M1/M2) with a PMOS mirror load (M3/M4) and an NMOS tail current source (M5). The second stage is a PMOS common-source device (M6) with an NMOS current-source load (M7). M8 and two series resistors set the bias. A resistor RZ in series with the Miller capacitor CC, from the first-stage output to the output, does the compensation.

I sized the first version with gm/ID hand calculations and then tuned it in simulation against the full spec list.

| Device | Role | First W/L (µm) | Final effective W/L (µm) |
|---|---|---|---|
| M1/M2 | NMOS input pair | 24/0.48 | 36/0.60 |
| M3/M4 | PMOS mirror load | 7.34/0.48 | 11/0.72 |
| M5 | Tail current source | 12.5/0.72 | 15/2.00 |
| M6 | Second stage | 50/0.24 | ≈ 75/0.24 |
| M7 | Second-stage current source | 45/0.72 | 45/0.72 |
| M8 | Bias reference | 4/0.48 | 4/0.48 |

The final bias resistors are 49.165 kΩ + 26.0031 kΩ, and the compensation is CC = 600.625 fF with RZ ≈ 1.0359 kΩ.

The tail and second-stage currents roughly tripled between my first check and the final design, from 7.11 to 21.15 µA and from 42.49 to 137.6 µA. More current bought GBW and positive slew rate, but it cost power and some phase-margin and CMRR headroom. Total power ended at 0.31 mW against the 0.6 mW limit.

Bigger devices did not always help. Widening M6 to 75 µm improved phase margin. M3/M4 at 22/1.44 µm, the same W/L at twice the size, pulled the worst-case CMRR down to 57.19 dB and the phase margin to 51.84°, both below spec, so they stayed at 11/0.72. A wider M7 cost power and negative slew rate, so M7 kept its first size.

For M5, a narrower 12/2.0 µm helped small-signal behavior but dropped SR+ to about 14.5 V/µs and SR− to 8.79 V/µs, under the 15 V/µs spec. Doubling W and L together was worse, as described in the [README](../README.md#how-i-tuned-the-opamp). M5 stayed at 15/2.0.

CC came down from 1.464 pF in the first schematic to about 0.60 pF for slew rate, and RZ recovered the phase margin this cost.

At nominal, M5 has the smallest saturation margin, about 65 mV. It is the first device I would recheck after extraction. Output swing is the one spec this OPAMP misses, and the [README](../README.md#results) explains why I left it.

[Schematic](../report/figures/opamp/schematic_final.png) · [Testbenches](../report/figures/opamp/testbench_final.png)

## PGA

The PGA is an inverting amplifier with a 10 kΩ input resistor, 10.0051 kΩ as implemented, and a tapped feedback string. Gain is `−Rf/Rin` around the 0.9 V reference, so a gain of G dB needs `Rf = Rin × 10^(G/20)`. I set the string so the cumulative resistance at each tap matches that ratio.

| Code | Target gain | Cumulative Rf | Passive gain |
|---|---:|---:|---:|
| 000 | 0 dB | 10.00530 kΩ | 0.00017 dB |
| 001 | 3 dB | 14.13878 kΩ | 3.00381 dB |
| 010 | 6 dB | 19.96719 kΩ | 6.00191 dB |
| 011 | 9 dB | 28.19806 kΩ | 8.99996 dB |
| 100 | 12 dB | 39.82946 kΩ | 11.99966 dB |
| 101 | 15 dB | 56.25326 kΩ | 14.99853 dB |
| 110 | 18 dB | 79.45566 kΩ | 17.99807 dB |
| 111 | 21 dB | 112.23026 kΩ | 20.99777 dB |

Before switch and loop effects, every tap is within 0.004 dB of its target.

Each tap is a CMOS transmission gate, PMOS 50/0.24 µm and NMOS 25/0.24 µm. I tested one in series with 100 kΩ while sweeping the input over 0.3–1.5 V. The worst case is 232.1 Ω on and 38.81 GΩ off. Relative to the feedback resistance, the on-resistance matters most at code 000, which is also the code with the largest gain error.

The [Verilog-A decoder](../models/pga_controller.va) is a behavioral model. It turns the three code bits into eight one-hot signals and their complements, with the threshold at half the supply and 1 ns edges. I swept all eight codes through the full PGA, which covers the static decoding together with the switches and the resistor string.

The report's [PGA core](../report/figures/pga/pga_core.jpeg) and [wrapper](../report/figures/pga/pga_wrapper.jpeg) screenshots show a later cleanup of the hierarchy into smaller cells. That version has no simulation export of its own, so all numbers here come from the earlier baseline.

## LPF

The LPF is a first-order inverting stage with unity gain. The input and feedback paths are each four 401.65 kΩ resistors in series, 1.6066 MΩ in total, and the 884.64 fF feedback capacitor sits behind an enable switch. The ideal pole `1/(2πRC)` is at 111.98 kHz. The simulated bandwidth is 100.1 kHz, pulled down by the switch and the finite OPAMP response. The spec is 50–150 kHz.

1.6 MΩ is well above the course guideline of about 1 MΩ. Getting below it would have meant a larger capacitor and redoing the filter, its layout and the simulations. I kept the resistors and treat the area as an open risk. There are no layout dimensions in this repo to say how large that risk is.

The filter is meant to clean up the signal before an ADC, but there is no ADC in this project, so system-level alias rejection was never tested.

[LPF schematic](../report/figures/pga/lpf_schematic.jpeg) · [Response](../report/figures/pga/lpf_response.png)
