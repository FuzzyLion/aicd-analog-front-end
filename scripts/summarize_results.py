#!/usr/bin/env python3
"""Check archived corner exports and summarize their reported MC statistics.

This script reads simulator exports. It does not run an analog simulation or
reconstruct individual Monte Carlo samples from summary statistics.
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_csv(relative: str) -> list[list[str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def number(value: str) -> float:
    suffixes = {"M": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9}
    value = value.strip()
    result = float(value[:-1]) * suffixes[value[-1]] if value[-1:] in suffixes else float(value)
    require(math.isfinite(result), f"Non-finite value: {value}")
    return result


def meets_spec(value: float, spec: str) -> bool:
    fields = spec.split()
    if len(fields) == 3 and fields[0] == "range":
        return number(fields[1]) <= value <= number(fields[2])
    if len(fields) == 2 and fields[0] == ">":
        return value > number(fields[1])
    if len(fields) == 2 and fields[0] == "<":
        return value < number(fields[1])
    raise ValueError(f"Unsupported exported specification: {spec}")


def corners(relative: str) -> list[dict[str, str]]:
    rows = read_csv(relative)
    headers = next(row for row in rows if "Output" in row and "Pass/Fail" in row)
    expected = [f"Corner_{i}" for i in range(64)]
    require([h for h in headers if h.startswith("Corner_")] == expected, f"{relative}: expected 64 corners")
    results = []
    code = None
    for row in rows[rows.index(headers) + 1:]:
        if row and row[0].startswith("Parameters:"):
            match = re.search(r"gain_code=(\d+)", row[0])
            require(match is not None, f"Unrecognized sweep setting: {row[0]}")
            code = match.group(1)
        entry = dict(zip(headers, row))
        if not entry.get("Spec"):
            continue
        require(len(row) == len(headers), f"{relative}: incomplete result row")
        if code is not None:
            entry["code"] = code
        values = [number(entry[h]) for h in expected]
        spec = entry["Spec"]
        count = sum(meets_spec(value, spec) for value in values)
        label = f"{relative}: {entry['Output']} code={code}"
        require(meets_spec(number(entry["Nominal"]), spec), f"{label}: nominal limit failed")
        require(count == 64 and entry["Pass/Fail"] == "pass", f"{label}: corner limit failed ({count}/64)")
        for key, calculated in [("Min", min(values)), ("Max", max(values))]:
            require(math.isclose(number(entry[key]), calculated, rel_tol=2e-4, abs_tol=1e-12), f"{label}: {key} differs from corner values")
        results.append(entry)
    return results


def monte_carlo(relative: str) -> list[dict[str, str]]:
    rows = read_csv(relative)
    headers = rows[0]
    require(headers == ["Test", "Name", "Yield", "Min", "Target", "Max", "Mean", "Std Dev", "Cpk", "Errors"], f"{relative}: unexpected summary header")
    results = []
    code = None
    for row in rows[1:]:
        if row:
            match = re.search(r"gain_code=(\d+)", row[0])
            if match:
                code = match.group(1)
        entry = dict(zip(headers, row))
        if not entry.get("Name", "").endswith("(summary)"):
            continue
        require(len(row) == len(headers), f"{relative}: incomplete MC row")
        if code is not None:
            entry["code"] = code
        values = [number(entry[key]) for key in ("Min", "Mean", "Max")]
        require(values == sorted(values), f"{relative}: mean outside reported range")
        require(number(entry["Std Dev"]) >= 0 and entry["Errors"] == "0", f"{relative}: invalid statistics or reported simulator errors")
        results.append(entry)
    return results


def fmt(value: str, scale: float = 1) -> str:
    return f"{number(value) * scale:.5g}"


def main() -> None:
    opamp = corners("data/opamp/corners.csv")
    pga = corners("data/pga/corners.csv")
    opamp_mc = monte_carlo("data/opamp/monte_carlo.csv")
    pga_mc = monte_carlo("data/pga/monte_carlo.csv")
    require(len(opamp) == 12, "Expected 12 OPAMP expressions")
    require(len(pga) == 24, "Expected three PGA/LPF expressions per code")
    require(len(opamp_mc) == 8 and len(pga_mc) == 24, "Unexpected MC summary coverage")
    gain_rows = [row for row in pga if row["Output"] == "Gain_PGA_Err_tolerence"]
    gain_mc = [row for row in pga_mc if row["Name"] == "Gain_PGA_Err_tolerence(summary)"]
    require([row["code"] for row in gain_rows] == [str(i) for i in range(8)], "Missing or duplicate PGA corner code")
    require([row["code"] for row in gain_mc] == [str(i) for i in range(8)], "Missing or duplicate PGA MC code")
    offset = next(row for row in opamp_mc if row["Name"] == "Offset Voltage(summary)")
    require(offset["Yield"] == "97.2% (972/1000)", "OPAMP offset yield changed")
    require(all(row["Yield"] == "100% (1000/1000)" for row in opamp_mc if row is not offset), "OPAMP non-offset yield changed")
    require(all(row["Yield"] == "100% (100/100)" for row in pga_mc), "PGA/LPF reported yield changed")

    units = {
        "Offset Voltage": (1e3, "Offset (mV)"), "CMRR": (1, "CMRR (dB)"),
        "Noise_20k_nV": (1e9, "Input noise at 20 kHz (nV/√Hz)"),
        "OutputNoise_20k_nV": (1e9, "Output noise at 20 kHz (nV/√Hz)"),
        "SR+": (1e-6, "SR+ (V/µs)"), "SR-": (1e-6, "SR− (V/µs)"),
        "ST+": (1e9, "Settling high (ns)"), "ST-": (1e9, "Settling low (ns)"),
        "power": (1e3, "Power (mW)"), "DC Gain": (1, "DC gain (dB)"),
        "PM": (1, "Phase margin (°)"), "GBW": (1e-6, "GBW (MHz)"),
    }
    lines = [
        "# Verification", "",
        "`scripts/summarize_results.py` generates this page from the CSV exports in [data/](../data/). For each corner metric it recounts the passes from the 64 raw values and checks the reported min and max against them. For Monte Carlo it can only check the summary rows, such as ranges, simulator errors and reported yields, because the files have no per-sample data. It does not run any circuit simulation.", "",
        "## OPAMP corners", "",
        "Nominal is 1.8 V, 27 °C, 0.9 V common mode and a 2 pF load. The 64 corners combine two MIM capacitor settings, two resistor settings, four transistor process settings, −25/85 °C and 1.62/1.98 V. Source: [corner export](../data/opamp/corners.csv).", "",
        "| Metric | Nominal | Corner min | Corner max | Passed |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in opamp:
        scale, label = units[row["Output"]]
        lines.append(f"| {label} | {fmt(row['Nominal'], scale)} | {fmt(row['Min'], scale)} | {fmt(row['Max'], scale)} | 64/64 |")
    lines += ["", "ICMR and output swing are not in the corner export, and I checked them at nominal only. A unity follower stays within 0.8503 mV of its input over the specified 0.5–1.3 V common-mode range. Output swing is 0.4302–1.4006 V, which misses the 0.3–1.5 V target. Both numbers are taken from the report, because the CSV does not contain them.", "", "## OPAMP Monte Carlo", "", "The run uses 1000 points per test, variation `All`, random sampling and seed 12345. Source: [Monte Carlo summary](../data/opamp/monte_carlo.csv).", "", "| Metric | Min | Max | Mean | σ | Reported yield |", "|---|---:|---:|---:|---:|---:|"]
    for row in opamp_mc:
        base = row["Name"].removesuffix("(summary)")
        scale, label = units[base]
        lines.append(f"| {label} | {fmt(row['Min'],scale)} | {fmt(row['Max'],scale)} | {fmt(row['Mean'],scale)} | {fmt(row['Std Dev'],scale)} | {row['Yield']} |")
    lines += ["", "Offset is the only metric below 100%, with 28 of 1000 samples beyond ±5 mV. CMRR, noise, power, ICMR and output swing are not part of this Monte Carlo run.", "", "## PGA and LPF", "", "Sources: [corner export](../data/pga/corners.csv), [Monte Carlo summary](../data/pga/monte_carlo.csv). Each code has a ±1.5 dB window around its target. The export stores the gain error relative to `3 × gain_code` dB, and the table adds the target back to show the absolute gain.", "", "| Code | Target (dB) | Nominal (dB) | Corner min…max (dB) | Corners passed | MC mean ± σ (dB) | Reported MC yield |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row, mc in zip(gain_rows,gain_mc):
        code = int(row["code"])
        target = 3 * code
        absolute = lambda key: f"{target + number(row[key]):.5g}"
        lines.append(f"| {code:03b} | {target} | {absolute('Nominal')} | {absolute('Min')}…{absolute('Max')} | 64/64 | {target + number(mc['Mean']):.5g} ± {fmt(mc['Std Dev'])} | {mc['Yield']} |")
    bw = next(row for row in pga if row["Output"] == "BW_LPF_Scalar")
    bw_mc = next(row for row in pga_mc if row["Name"] == "BW_LPF_Scalar(summary)")
    lines += ["", f"The LPF bandwidth is {fmt(bw['Nominal'],1e-3)} kHz at nominal and {fmt(bw['Min'],1e-3)}–{fmt(bw['Max'],1e-3)} kHz across corners, inside the 50–150 kHz spec. Monte Carlo gives {fmt(bw_mc['Min'],1e-3)}–{fmt(bw_mc['Max'],1e-3)} kHz, mean {fmt(bw_mc['Mean'],1e-3)} kHz, σ {fmt(bw_mc['Std Dev'],1e-3)} kHz and {bw_mc['Yield']} yield. The export repeats the same LPF statistics in every code group, so they are one set of 100 samples.", "", "## Not verified", "", "- Post-layout performance. There are no extracted-view results for any block.", "- ICMR and output swing beyond nominal.", "- Switching between gain codes. The sweeps check each code statically, and there is no switching transient in the archive.", "- The decoder at gate level. The controller is a behavioral Verilog-A model.", "- The full PGA AC phase for all codes, the safe input range per code, and per-code stability and power.", ""]
    output = ROOT / "docs/verification.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print("PASS: 12 OPAMP + 24 PGA/LPF expressions, each with 64 corners.")
    print("PASS: 8 PGA codes; 32 Monte Carlo summary rows; reported offset yield 972/1000.")
    print("Wrote docs/verification.md. No new circuit simulation was run.")


if __name__ == "__main__":
    main()
