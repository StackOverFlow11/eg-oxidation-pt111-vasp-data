# Derived data and workflow templates

This directory contains derived (non-raw) material copied from the manuscript
workspace at the time of archiving:

| File | Description |
|---|---|
| `harvest_ledger.csv` | 25-row grand-potential ledger: Ω, q_sol, ZPE, TS, Gcorr, G_φ for every production state |
| `harvest_ladder.csv` | Free-energy ladders at 0.4 and 0.9 V vs RHE (EG oxidation, OER, HER, thermal step) |
| `plot_fig1.py` | Script that generates Figure 1 from the ladder (requires `matplotlib`; outputs `fig1_gc.png/pdf` next to the script) |
| `workflow/templates/` | VASP INCAR/KPOINTS templates for the pre_opt / fine_opt / frq tiers |
| `workflow/conventions.md` | Frozen thermodynamic conventions (CHE, Ω, G_corr, G(O₂), pressures) |
| `workflow/rules.md` | Hard rules for constant-potential VASPsol++ runs and the acceptance checks |

The authoritative source of these files is the manuscript workspace
`GC_CHE/harvest`, `GC_CHE/analysis`, and `GC_CHE/workflow`. They are included
here so that the raw data can be traced to the reported ledger and figure
without a second repository.

`harvest_ledger.csv` uses Ω (the pinned VASP `E0`) directly; do not add a
manual `±Δn·μ_e` correction. See `workflow/conventions.md`.
