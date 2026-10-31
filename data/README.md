# Simulation exports

These are unmodified simulator-export CSVs from the lab archive, renamed for navigation. The corner files contain setup rows followed by result tables; they are not single-header rectangular datasets. Model-section names identify run settings and do not contain the model implementations.

| File | Original filename | Contents |
|---|---|---|
| [opamp/corners.csv](opamp/corners.csv) | `corner.csv` | Nominal values, the 64-corner grid, and 12 result expressions |
| [opamp/monte_carlo.csv](opamp/monte_carlo.csv) | `OPAMP_mcmc_new.csv` | 1000-point OPAMP Monte Carlo summary statistics |
| [pga/corners.csv](pga/corners.csv) | `pga_corner.csv` | All eight PGA codes and LPF nominal/corner results |
| [pga/monte_carlo.csv](pga/monte_carlo.csv) | `pga_mc.csv` | PGA/LPF summary statistics for 100 Monte Carlo points per code |

The full device operating-point export is excluded. Selected operating-point values remain in the report summary table.

Monte Carlo CSVs provide summary statistics and reported yield, not all individual sample values. Their yields cannot be independently reconstructed sample by sample from this archive. `python3 scripts/summarize_results.py` checks the corner values against the exported limits and summarizes the reported Monte Carlo statistics. It generates [verification.md](../docs/verification.md) without third-party Python dependencies.

The older OPAMP `MonteCarlo.0.csv` used a different testbench context and is not included. This repository uses the final 1000-point export from the project's own testbenches.
