# Design notes

The design uses two inverting stages around a 0.9 V common-mode reference: a programmable-gain stage followed by an active LPF. The OPAMP is reused in both stages. There is no ADC in the schematic or simulation.

## OPAMP

The first stage uses an NMOS differential pair, a PMOS current-mirror load, and an NMOS tail-current source. A PMOS common-source second stage drives an NMOS current-source load. A series resistor and Miller capacitor connect the first-stage node to the output.

The initial sizing used the gm/ID method. The final design came from iterating the transistor dimensions, bias current, and compensation against the full set of measurements. Raising current improved bandwidth and slew rate but increased power and reduced margin in other checks. Reducing the Miller capacitor improved slew rate while making stability harder; the series compensation resistor helped recover phase margin.

| Device or component | Simulated schematic baseline |
|---|---|
| M1/M2, NMOS input pair | Effective W/L = 36/0.60 µm |
| M3/M4, PMOS mirror | Effective W/L = 11/0.72 µm |
| M5, tail current source | Effective W/L = 15/2.00 µm |
| M6, second stage | Effective W/L ≈ 75/0.24 µm |
| M7, second-stage current source | Effective W/L = 45/0.72 µm |
| M8, bias reference | W/L = 4/0.48 µm |
| Bias resistance | Approximately 49.165 kΩ + 26.0031 kΩ |
| Miller compensation | CC = 600.625 fF; RZ ≈ 1.0359 kΩ |

At nominal conditions, M5 has the smallest recorded saturation margin, approximately 65 mV. It would be an early check after extraction. Output swing is the main unmet nominal specification. The design was retained for the stimuli used in the passing PGA runs; that does not establish a safe input-amplitude range for every gain code.

[Simulated-baseline schematic](../report/figures/opamp/schematic_final.png) · [Testbenches](../report/figures/opamp/testbench_final.png)

## PGA and control

Relative to the common-mode reference, the ideal gain is `-(Rfeedback / Rin)`. The target resistor ratio for a gain magnitude G in dB is `10^(G/20)`. Rin is approximately 10.0051 kΩ.

| Code | Target gain | Cumulative feedback resistance |
|---|---:|---:|
| 000 | 0 dB | 10.00530 kΩ |
| 001 | 3 dB | 14.13878 kΩ |
| 010 | 6 dB | 19.96719 kΩ |
| 011 | 9 dB | 28.19806 kΩ |
| 100 | 12 dB | 39.82946 kΩ |
| 101 | 15 dB | 56.25326 kΩ |
| 110 | 18 dB | 79.45566 kΩ |
| 111 | 21 dB | 112.23026 kΩ |

Each tap uses a CMOS transmission gate: PMOS 50/0.24 µm and NMOS 25/0.24 µm. The focused switch test records worst-case Ron of 232.1 Ω and Roff of 38.81 GΩ over 0.3–1.5 V. Finite on-resistance has the largest relative effect at the lowest feedback resistance, consistent with the larger nominal gain error at code 000.

The [Verilog-A model](../models/pga_controller.va) generates eight one-hot outputs and their complements. It thresholds inputs at half the supply and uses 1 ns output transitions. All-code PGA sweeps exercise the static decode path with the feedback network. A measured 010-to-101 switching transient is not archived, so dynamic switching behavior is not established by those sweeps.

[PGA core](../report/figures/pga/pga_core.jpeg) · [Wrapper](../report/figures/pga/pga_wrapper.jpeg)

The modular PGA/LPF screenshots document a later hierarchy update. The scalar results remain tied to the archived simulation baseline. The PGA run-deck archive refers to a sibling design netlist that is not available, so a complete native replay cannot be reconstructed from these files alone.

## Active LPF

The LPF is a unity-magnitude inverting first-order filter. Each input/feedback resistance path uses four series elements of approximately 401.65 kΩ, giving 1.6066 MΩ per path. The feedback capacitance is 884.64 fF, connected through an enable switch.

The ideal pole from `1/(2πRC)` is about 111.98 kHz. The simulated −3 dB bandwidth is 100.1 kHz, within the 50–150 kHz requirement. Finite OPAMP response and the switch are part of the implemented circuit. The large resistance remains an area risk; no measured layout dimensions are available to quantify it.

[LPF schematic](../report/figures/pga/lpf_schematic.jpeg) · [Response](../report/figures/pga/lpf_response.png)

The LPF is intended to attenuate out-of-band signals before a possible downstream ADC. No ADC or system-level alias-rejection test was implemented.
