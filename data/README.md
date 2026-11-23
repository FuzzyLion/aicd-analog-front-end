# Simulation exports

These are the CSV files exported from the Cadence simulator, unchanged except for the file names.

| File | Original filename | Contents |
|---|---|---|
| [opamp/corners.csv](opamp/corners.csv) | `corner.csv` | Nominal values, the 64-corner grid, and 12 result expressions |
| [opamp/monte_carlo.csv](opamp/monte_carlo.csv) | `OPAMP_mcmc_new.csv` | 1000-point OPAMP Monte Carlo summary statistics |
| [pga/corners.csv](pga/corners.csv) | `pga_corner.csv` | All eight PGA codes and LPF nominal/corner results |
| [pga/monte_carlo.csv](pga/monte_carlo.csv) | `pga_mc.csv` | PGA/LPF summary statistics for 100 Monte Carlo points per code |

The corner files are not simple rectangular tables. They start with setup rows and then the results. The model-section names in them only label the run settings, and no model files are included.

The Monte Carlo files only have summary statistics and the reported yield, not the individual samples, so the yields cannot be recomputed from them.

[scripts/summarize_results.py](../scripts/summarize_results.py) reads these files and writes [docs/verification.md](../docs/verification.md). It needs only the Python 3 standard library.

Two files are left out. The full device operating-point export is not here, and the report keeps the values that explain the sizing. An older OPAMP Monte Carlo export, `MonteCarlo.0.csv`, came from a different testbench, so I used the final 1000-point export from my own testbenches instead.
