# Verification and limits

This page is generated from the archived CSV exports by `python3 scripts/summarize_results.py`. The script recomputes corner pass counts from the 64 values and checks the exported extrema. Monte Carlo yields are reported summary values; individual sample data are not archived. No circuit simulation is run by this script.

## OPAMP schematic baseline

Nominal conditions: 1.8 V, 27 °C, 0.9 V common mode, and a 2 pF load. The 64-corner grid combines two MIM capacitor settings, two resistor settings, four transistor process settings, −25/85 °C, and 1.62/1.98 V. This is the lab's exported grid, not an exhaustive process or reliability qualification.

Source: [corner export](../data/opamp/corners.csv).

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

ICMR and output swing are absent from this corner export. The standalone nominal follower check gives a maximum error of 0.8503 mV over the specified 0.5–1.3 V input common-mode range. The wider 0–1.8 V sweep is the test range. The recorded output swing, 0.4302–1.4006 V, does not meet the 0.3–1.5 V target. These two standalone results are documented in the report and figures, not recomputed from the CSV.

### OPAMP Monte Carlo

The recorded setup uses variation `All`, random sampling, 1000 points per test, and seed 12345. Source: [Monte Carlo summary](../data/opamp/monte_carlo.csv).

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

Offset is the limiting reported yield: 28 of 1000 points exceed ±5 mV. A 1000-point reported yield is a result for that sample set, not a manufacturing yield guarantee. CMRR, noise, power, ICMR, and output swing are not covered by this eight-metric Monte Carlo summary.

## PGA and LPF

Sources: [corner export](../data/pga/corners.csv), [Monte Carlo summary](../data/pga/monte_carlo.csv). Gain tolerance is ±1.5 dB around each target. The gain-error expression is stored relative to `3 × gain_code` dB; the table adds that target back to show absolute gain.

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

LPF bandwidth is 100.1 kHz nominally and 72.88–121.8 kHz across corners, within the 50–150 kHz specification. The MC summary reports 82.8–119.5 kHz, mean 100 kHz, σ 6.796 kHz, and 100% (100/100) yield. Identical LPF statistics appear in every code group; they are not treated as 800 independent LPF samples.

## Scope and remaining work

This portfolio covers schematic work. Teammate layout and physical-verification screenshots are excluded. No OPAMP, PGA, or LPF post-layout performance is claimed. The full device operating-point export is omitted; selected values remain in the report summary table.

Other limits are the missing measured gain-switching transient, full PGA AC phase capture, per-code safe input range, and per-code stability/power summary. The controller is behavioral; static code sweeps do not verify a gate-level implementation or switching hazards. Later layout-oriented redraws have no separate exported simulation baseline. The native Cadence library and complete PGA hierarchy are not archived.

## Checks during portfolio packaging

The data script verifies all 12 OPAMP and 24 PGA/LPF expression rows against their nominal/corner limits, checks all eight gain codes, and checks the structure, ranges, reported errors, and expected yields of 32 MC summary rows. It regenerates this page from the included files. This is verification of the archived exports, separate from the original Cadence simulation work.
