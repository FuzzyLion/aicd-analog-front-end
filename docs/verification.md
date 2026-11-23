# Verification

`scripts/summarize_results.py` generates this page from the CSV exports in [data/](../data/). For each corner metric it recounts the passes from the 64 raw values and checks the reported min and max against them. For Monte Carlo it can only check the summary rows, such as ranges, simulator errors and reported yields, because the files have no per-sample data. It does not run any circuit simulation.

## OPAMP corners

Nominal is 1.8 V, 27 °C, 0.9 V common mode and a 2 pF load. The 64 corners combine two MIM capacitor settings, two resistor settings, four transistor process settings, −25/85 °C and 1.62/1.98 V. Source: [corner export](../data/opamp/corners.csv).

| Metric | Nominal | Corner min | Corner max | Passed |
|---|---:|---:|---:|---:|
| Offset (mV) | -0.4516 | -0.7204 | -0.266 | 64/64 |
| CMRR (dB) | 68.53 | 61.54 | 74.5 | 64/64 |
| Input noise at 20 kHz (nV/√Hz) | 32.78 | 29.17 | 45.73 | 64/64 |
| Output noise at 20 kHz (nV/√Hz) | 32.79 | 29.18 | 45.74 | 64/64 |
| SR+ (V/µs) | 35.17 | 22.34 | 49.14 | 64/64 |
| SR− (V/µs) | 27.43 | 16.04 | 34.9 | 64/64 |
| Settling high (ns) | 16.39 | 11.77 | 26.36 | 64/64 |
| Power (mW) | 0.3113 | 0.2663 | 0.3678 | 64/64 |
| Settling low (ns) | 23.17 | 18.11 | 41.74 | 64/64 |
| DC gain (dB) | 79.93 | 76.32 | 82.76 | 64/64 |
| Phase margin (°) | 61.97 | 59.57 | 68.81 | 64/64 |
| GBW (MHz) | 51.31 | 32.28 | 72.94 | 64/64 |

ICMR and output swing are not in the corner export, and I checked them at nominal only. A unity follower stays within 0.8503 mV of its input over the specified 0.5–1.3 V common-mode range. Output swing is 0.4302–1.4006 V, which misses the 0.3–1.5 V target. Both numbers are taken from the report, because the CSV does not contain them.

## OPAMP Monte Carlo

The run uses 1000 points per test, variation `All`, random sampling and seed 12345. Source: [Monte Carlo summary](../data/opamp/monte_carlo.csv).

| Metric | Min | Max | Mean | σ | Reported yield |
|---|---:|---:|---:|---:|---:|
| SR+ (V/µs) | 27.06 | 44.66 | 35.16 | 2.742 | 100% (1000/1000) |
| SR− (V/µs) | 21.82 | 35.37 | 27.43 | 2.072 | 100% (1000/1000) |
| Settling high (ns) | 12.94 | 21.31 | 16.48 | 1.282 | 100% (1000/1000) |
| Settling low (ns) | 17.94 | 29.65 | 23.31 | 1.786 | 100% (1000/1000) |
| DC gain (dB) | 79.09 | 80.75 | 79.93 | 0.2452 | 100% (1000/1000) |
| Phase margin (°) | 56.28 | 66.4 | 61.93 | 1.479 | 100% (1000/1000) |
| GBW (MHz) | 42.09 | 63.05 | 51.42 | 3.25 | 100% (1000/1000) |
| Offset (mV) | -7.447 | 5.518 | -0.4735 | 2.212 | 97.2% (972/1000) |

Offset is the only metric below 100%, with 28 of 1000 samples beyond ±5 mV. CMRR, noise, power, ICMR and output swing are not part of this Monte Carlo run.

## PGA and LPF

Sources: [corner export](../data/pga/corners.csv), [Monte Carlo summary](../data/pga/monte_carlo.csv). Each code has a ±1.5 dB window around its target. The export stores the gain error relative to `3 × gain_code` dB, and the table adds the target back to show the absolute gain.

| Code | Target (dB) | Nominal (dB) | Corner min…max (dB) | Corners passed | MC mean ± σ (dB) | Reported MC yield |
|---|---:|---:|---:|---:|---:|---:|
| 000 | 0 | 0.1463 | 0.04996…1.221 | 64/64 | 0.1461 ± 0.02701 | 100% (100/100) |
| 001 | 3 | 3.1058 | 3.0319…3.8869 | 64/64 | 3.1059 ± 0.02387 | 100% (100/100) |
| 010 | 6 | 6.0723 | 6.0165…6.6357 | 64/64 | 6.0721 ± 0.02253 | 100% (100/100) |
| 011 | 9 | 9.0475 | 9.0117…9.4463 | 64/64 | 9.0474 ± 0.02347 | 100% (100/100) |
| 100 | 12 | 12.03 | 12.005…12.313 | 64/64 | 12.029 ± 0.02074 | 100% (100/100) |
| 101 | 15 | 15.017 | 15…15.209 | 64/64 | 15.015 ± 0.02022 | 100% (100/100) |
| 110 | 18 | 18.006 | 17.982…18.13 | 64/64 | 18.005 ± 0.02069 | 100% (100/100) |
| 111 | 21 | 20.997 | 20.955…21.098 | 64/64 | 20.997 ± 0.02288 | 100% (100/100) |

The LPF bandwidth is 100.1 kHz at nominal and 72.88–121.8 kHz across corners, inside the 50–150 kHz spec. Monte Carlo gives 82.8–119.5 kHz, mean 100 kHz, σ 6.796 kHz and 100% (100/100) yield. The export repeats the same LPF statistics in every code group, so they are one set of 100 samples.

## Not verified

- Post-layout performance. There are no extracted-view results for any block.
- ICMR and output swing beyond nominal.
- Switching between gain codes. The sweeps check each code statically, and there is no switching transient in the archive.
- The decoder at gate level. The controller is a behavioral Verilog-A model.
- The full PGA AC phase for all codes, the safe input range per code, and per-code stability and power.
