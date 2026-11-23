# Technical report

[AICD_Analog_Front_End.pdf](AICD_Analog_Front_End.pdf) is the lab report on the OPAMP, PGA and LPF, with the nominal, corner and Monte Carlo results. Compared with the submitted version, it leaves out the course cover, the student numbers, my teammate's name and their layout images. It also uses the standard LaTeX `report` class instead of the university template, so no logo files are needed to build it. The result values are unchanged.

## Build

You need TeX Live or MacTeX with LuaLaTeX and the packages listed in `report.tex`. From this directory:

```sh
mkdir -p build/chapters
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex
```

The output is `build/report.pdf`. Once it looks right, copy it over `AICD_Analog_Front_End.pdf`. Git ignores the `build` directory.

## Figures

The figures are original screenshots and exports from Cadence. Labels in some full-window screenshots are small, so take exact values from the report tables or the [CSV files](../data/).
