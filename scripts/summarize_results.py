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
        "# Verification and limits", "",
        "This page is generated from the archived CSV exports by `python3 scripts/summarize_results.py`. The script recomputes corner pass counts from the 64 values and checks the exported extrema. Monte Carlo yields are reported summary values; individual sample data are not archived. No circuit simulation is run by this script.", "",
        "## OPAMP schematic baseline", "",
        "Nominal conditions: 1.8 V, 27 °C, 0.9 V common mode, and a 2 pF load. The 64-corner grid combines two MIM capacitor settings, two resistor settings, four transistor process settings, −25/85 °C, and 1.62/1.98 V. This is the lab's exported grid, not an exhaustive process or reliability qualification.", "",
        "Source: [corner export](../data/opamp/corners.csv).", "",
        "| Metric | Nominal | Corner min | Corner max | Passed |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in opamp:
        scale, label = units[row["Output"]]
        lines.append(f"| {label} | {fmt(row['Nominal'], scale)} | {fmt(row['Min'], scale)} | {fmt(row['Max'], scale)} | 64/64 |")
    lines += ["", "ICMR and output swing are absent from this corner export. The standalone nominal follower check gives a maximum error of 0.8503 mV over the specified 0.5–1.3 V input common-mode range. The wider 0–1.8 V sweep is the test range. The recorded output swing, 0.4302–1.4006 V, does not meet the 0.3–1.5 V target. These two standalone results are documented in the report and figures, not recomputed from the CSV.", "", "### OPAMP Monte Carlo", "", "The recorded setup uses variation `All`, random sampling, 1000 points per test, and seed 12345. Source: [Monte Carlo summary](../data/opamp/monte_carlo.csv).", "", "| Metric | Min | Max | Mean | σ | Reported yield |", "|---|---:|---:|---:|---:|---:|"]
    for row in opamp_mc:
        base = row["Name"].removesuffix("(summary)")
        scale, label = units[base]
        lines.append(f"| {label} | {fmt(row['Min'],scale)} | {fmt(row['Max'],scale)} | {fmt(row['Mean'],scale)} | {fmt(row['Std Dev'],scale)} | {row['Yield']} |")
    lines += ["", "Offset is the limiting reported yield: 28 of 1000 points exceed ±5 mV. A 1000-point reported yield is a result for that sample set, not a manufacturing yield guarantee. CMRR, noise, power, ICMR, and output swing are not covered by this eight-metric Monte Carlo summary.", "", "## PGA and LPF", "", "Sources: [corner export](../data/pga/corners.csv), [Monte Carlo summary](../data/pga/monte_carlo.csv). Gain tolerance is ±1.5 dB around each target. The gain-error expression is stored relative to `3 × gain_code` dB; the table adds that target back to show absolute gain.", "", "| Code | Target (dB) | Nominal (dB) | Corner min…max (dB) | Corners passed | MC mean ± σ (dB) | Reported MC yield |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row, mc in zip(gain_rows,gain_mc):
        code = int(row["code"])
        target = 3 * code
        absolute = lambda key: f"{target + number(row[key]):.5g}"
        lines.append(f"| {code:03b} | {target} | {absolute('Nominal')} | {absolute('Min')}…{absolute('Max')} | 64/64 | {target + number(mc['Mean']):.5g} ± {fmt(mc['Std Dev'])} | {mc['Yield']} |")
    bw = next(row for row in pga if row["Output"] == "BW_LPF_Scalar")
    bw_mc = next(row for row in pga_mc if row["Name"] == "BW_LPF_Scalar(summary)")
    lines += ["", f"LPF bandwidth is {fmt(bw['Nominal'],1e-3)} kHz nominally and {fmt(bw['Min'],1e-3)}–{fmt(bw['Max'],1e-3)} kHz across corners, within the 50–150 kHz specification. The MC summary reports {fmt(bw_mc['Min'],1e-3)}–{fmt(bw_mc['Max'],1e-3)} kHz, mean {fmt(bw_mc['Mean'],1e-3)} kHz, σ {fmt(bw_mc['Std Dev'],1e-3)} kHz, and {bw_mc['Yield']} yield. Identical LPF statistics appear in every code group; they are not treated as 800 independent LPF samples.", "", "## Scope and remaining work", "", "This portfolio covers schematic work. Teammate layout and physical-verification screenshots are excluded. No OPAMP, PGA, or LPF post-layout performance is claimed. The full device operating-point export is omitted; selected values remain in the report summary table.", "", "Other limits are the missing measured gain-switching transient, full PGA AC phase capture, per-code safe input range, and per-code stability/power summary. The controller is behavioral; static code sweeps do not verify a gate-level implementation or switching hazards. Later layout-oriented redraws have no separate exported simulation baseline. The native Cadence library and complete PGA hierarchy are not archived.", "", "## Checks during portfolio packaging", "", "The data script verifies all 12 OPAMP and 24 PGA/LPF expression rows against their nominal/corner limits, checks all eight gain codes, and checks the structure, ranges, reported errors, and expected yields of 32 MC summary rows. It regenerates this page from the included files. This is verification of the archived exports, separate from the original Cadence simulation work.", ""]
    output = ROOT / "docs/verification.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print("PASS: 12 OPAMP + 24 PGA/LPF expressions, each with 64 corners.")
    print("PASS: 8 PGA codes; 32 Monte Carlo summary rows; reported offset yield 972/1000.")
    print("Wrote docs/verification.md. No new circuit simulation was run.")


if __name__ == "__main__":
    main()
