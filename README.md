# Programmable-Gain Analog Front End

I worked on this 1.8 V analog front end in the Advanced Integrated Circuit Design Lab at TU Darmstadt in summer 2026. It combines a two-stage Miller-compensated OPAMP, an eight-step PGA covering 0–21 dB, and an active low-pass filter with a simulated nominal bandwidth of 100.1 kHz.

My part was OPAMP integration and sizing, the PGA and LPF schematics, testbenches, final schematic simulations, and putting the report together. This was a two-person project; the [contribution statement](docs/contributions.md) explains who did what.

[Technical report](report/AICD_Analog_Front_End.pdf) · [Design decisions](docs/design-notes.md) · [Verification and limits](docs/verification.md)

The implemented signal path is:

```text
Analog input -> programmable inverting PGA -> active LPF -> analog output
```

The PGA uses a resistor feedback string and transmission-gate taps, selected by a behavioral Verilog-A 3-to-8 decoder. A downstream ADC is application context and is outside this project.

![Nominal PGA gain for all eight digital codes](assets/gain-vs-code.png)

## Results

These are archived Cadence schematic-level results. The nominal OPAMP setup is 1.8 V, 27 °C, 0.9 V common mode, and a 2 pF load.

| Measurement | Result |
|---|---:|
| OPAMP DC gain | 79.93 dB |
| Gain-bandwidth product | 51.31 MHz |
| Phase margin | 61.97° |
| OPAMP power | 0.3113 mW |
| PGA gain settings | 0–21 dB in 3 dB steps |
| PGA gain tolerance | All eight codes within ±1.5 dB across 64 corners and 100 Monte Carlo samples per code |
| LPF bandwidth | 100.1 kHz nominal; 72.88–121.8 kHz across 64 corners |

The OPAMP still misses the output-swing target. It reaches 0.4302–1.4006 V against the required 0.3–1.5 V. Its Monte Carlo offset yield is 972/1000 against a ±5 mV limit. All 12 expressions in the 64-corner OPAMP export pass, but that export does not cover ICMR or output swing.

I am sharing the schematic design and verification here. Physical layout was my teammate's part, and their layout and verification images are left out. I have no complete extracted-view or PEX performance results to report.

## Design work

For the OPAMP, a smaller Miller capacitor helped slew rate but cost phase margin. I settled on about 0.60 pF and used a series resistor near 1 kΩ to recover margin.

- Sized and tuned the OPAMP around gain, bandwidth, stability, slew rate, noise, and power.
- Designed the eight-tap PGA feedback network and integrated the transmission gates and behavioral controller.
- Designed the active LPF and evaluated its bandwidth, including corner and Monte Carlo variation.
- Built the testbenches, reviewed the final simulation exports, and prepared the schematic-to-layout handoff.

The report shows the sizing progression, selected operating-point values, and testbenches. The OPAMP figure matches the simulated schematic baseline. I have left out the full device operating-point CSV.

## Repository

| Folder | Contents |
|---|---|
| [report/](report/) | Portfolio PDF, editable LaTeX chapters, and selected original figures |
| [data/](data/) | Original CSV exports for OPAMP, PGA, and LPF results |
| [models/](models/) | Behavioral controller used in the PGA testbench |
| [docs/](docs/) | Design notes, contributions, and verification details |
| [scripts/](scripts/) | Checks and summaries for the archived CSV exports |

To check the data with Python 3, run `python3 scripts/summarize_results.py`. [Report build instructions](report/README.md) are included. These checks read existing exports; rerunning the circuits requires Cadence and the licensed course PDK. Native Cadence libraries, PDK models, and a complete replayable PGA netlist are not included.

I used AI tools for language editing, report formatting, data checks, and packaging this repository. The numerical results come from the archived simulator exports. See the report's AI declaration and [attribution notes](NOTICE.md).
