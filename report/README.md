# Technical report

[AICD_Analog_Front_End.pdf](AICD_Analog_Front_End.pdf) is the portfolio edition of the integrated lab report. It covers the OPAMP, PGA and LPF, nominal/corner/Monte Carlo verification, and the scope of the schematic work.

The course cover, student numbers and the teammate's name were removed. The chapters use a standard LaTeX `report` class instead of the university template; no university logo files are needed. The detailed contribution split is also available in [contributions.md](../docs/contributions.md).

## Build

Use a TeX Live or MacTeX installation with LuaLaTeX and the packages listed in `report.tex`. From this directory:

```sh
mkdir -p build/chapters
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
```

The result is `build/report.pdf`. After checking the PDF, copy it to `AICD_Analog_Front_End.pdf` to update the portfolio copy. The `build` directory is ignored by Git.

The figures are selected original screenshots and exports. Some full-window screenshots have small annotations; use the CSVs and report tables for exact values. Teammate layout and physical-verification images, and the full device operating-point CSV, are excluded. Selected operating-point values remain in the report.
