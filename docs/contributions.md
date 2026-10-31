# Contributions

This was a two-person course project by Qi Wu and one teammate, who is not named here. The division below follows the lab contribution record.

| Part | Qi Wu | Teammate |
|---|---|---|
| OPAMP | Overall integration, transistor sizing and tuning, testbench setup | Current-source and bias-section design |
| PGA and LPF | PGA schematic and calculations, testbench setup, transmission-gate/controller integration, LPF design | — |
| Schematic simulations | OPAMP verification; PGA nominal simulation and final corner/Monte Carlo reruns after updating the OPAMP; LPF verification and analysis | Initial PGA corner and Monte Carlo runs for the midterm submission |
| Layout | Handoff with schematic parameters, simulation baselines, and layout constraints | OPAMP, inverter, transmission-gate, and LPF layouts |
| Physical verification | Integrated the supplied status into the report | Available DRC/LVS checks; inverter and TG LVS matched, OPAMP LVS did not pass |
| Post-layout work | No complete-block PEX simulation work claimed | Inverter and TG simulations are listed in the contribution record; supporting result exports are not part of this repository |
| Report | Schematic sections, result and figure organization, final integration | Layout material and technical input |

The teammate's layout images and physical-verification screenshots are omitted from this portfolio. The task split remains explicit; no physical implementation is claimed as Qi Wu's work.

The controller is a behavioral Verilog-A model used and integrated in the lab. This repository does not present it as a synthesized or physically implemented digital decoder. The archived source retains its original comments about course acceptance.

AI assistance covered language and structure editing, numerical consistency checks, LaTeX/PDF formatting, and repository packaging. The design contribution claimed here is the student's circuit work, integration, simulation work, and engineering decisions described above. The archived report also contains its original AI-assistance declaration, updated to describe this portfolio edition's formatting.
