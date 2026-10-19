# EG oxidation on Pt(111) — VASP raw data

Raw VASP data for the DFT study of ethylene glycol (EG) oxidation on Pt(111).
The data are organized into two workflows:

| Workflow | Directory | Ensemble |
|---|---|---|
| Configuration screening | `screening/` | constant charge, vacuum, CHE, 450 eV |
| Production | `production/` | constant potential, VASPsol++, 0.4 / 0.9 V vs RHE |

## Layout

```
screening/
  che_eg_oxidation/      # EG oxidation species and candidate motifs (CHE 450 eV)
  che_oer/               # OER references (H2O, *OH, *O, *OOH)
  single_side_ox/        # single-side pathway candidates
  double_side_ox/        # dual-side path-selectivity candidates
  hor/                   # HER *H reference
production/
  <species>/<0.4V|0.9V|neutral>/{pre_opt,fine_opt,frq}/
derived/
  harvest_ledger.csv     # 25-row grand-potential ledger (Ω, q_sol, Gcorr, G_φ)
  harvest_ladder.csv     # free-energy ladders at 0.4 / 0.9 V
  plot_fig1.py           # Figure 1 plotting script
  workflow/              # templates and thermodynamic conventions used for production
manifest/
  jobs.csv               # one row per archived directory
  potcar.csv             # POTCAR metadata: element order, TITEL/VRHFIN, SHA-256
  checksums.sha256       # SHA-256 of every archived file
fetch/
  make_potcar.py         # rebuild a job's POTCAR from a licensed local potpaw library
  verify_checksums.sh    # verify the repository against manifest/checksums.sha256
```

The original directory names are preserved except for two Windows/URL-safe
replacements: `*` → `_` and `+` → `p`.

## Status values in `manifest/jobs.csv`

| Status | Meaning |
|---|---|
| `prod_final` | production state (pre_opt / fine_opt / frq) |
| `screen_selected` | screening candidate selected for the production workflow |
| `screen_candidate` | alternative candidate evaluated during screening |

Current counts: 74 production directories covering 20 adsorbate states at
0.4 / 0.9 V, 3 gas molecules, 2 slab references, and `*OOH` at both potentials;
87 screening `opt` directories (15 selected, 72 candidates).

## File selection

A complete archived `opt` / `pre_opt` / `fine_opt` directory contains:

- `INCAR`, `KPOINTS`, `POSCAR`, `CONTCAR`, `OSZICAR`
- `OUTCAR.gz` — full OUTCAR, gzip -9, not trimmed
- `vasprun.xml.gz`
- `POTCAR.sha256` — SHA-256 of the original POTCAR

A complete `frq` directory additionally contains `DYNMAT` (the
finite-displacement Hessian used by the thermal-correction script).

## POTCAR

**POTCAR files are not redistributed** because they are distributed under the
VASP license. For every job we provide:

1. `POTCAR.sha256` in the job directory (the hash of the original POTCAR);
2. a row in `manifest/potcar.csv` with the element order, `TITEL`/`VRHFIN`
   lines, POTCAR size, and SHA-256.

To rebuild a POTCAR from a licensed local `potpaw_PBE` library:

```bash
python fetch/make_potcar.py <job_id> /path/to/potpaw_PBE
```

`<job_id>` is the path relative to the repository root, e.g.
`production/_ch2ohcoo_p_h/0.4V/fine_opt`. The script concatenates the element
POTCARs in the recorded order, writes `POTCAR` in the job directory, and
verifies it against `POTCAR.sha256`.

## VASP versions

- **Production**: VASP 5.4.4 with the VASPsol++ patch (`ISOL=2`,
  nonlinear/nonlocal cavity, grand-canonical Fermi-level pinning).
- **Screening**: VASP 5.4.4, constant-charge CHE calculations.

## Thermodynamic conventions

The production free energies use the GC-CHE conventions frozen in
`derived/workflow/conventions.md`:

- `E_F,ref = ε_F,SHE − U_SHE = −4.52 − U_RHE + 0.826` eV;
  0.4 V → −4.094 eV, 0.9 V → −4.594 eV.
- `Ω = A − q_sol μ_e`; the pinned VASP `E0` is already Ω and state differences
  are taken by direct subtraction, with no manual `±Δn·μ_e` term.
- `G_φ = Ω + G_corr`; neutral gas-phase species enter with `Ω = G`.
- `(H⁺ + e⁻)` is referenced to ½H₂; `G(O₂) = 2G(H₂O) − 2G(H₂) + 4.92` eV.
- `T = 300.15 K`; gas-phase pressures: EG and H₂ 1 bar, H₂O 0.035 bar.
- Frequencies are neutral, solvent-free, fixed-charge calculations used only
  for the thermal correction; the energetics are constant-potential.

## Verification

```bash
# verify every archived file
bash fetch/verify_checksums.sh

# inspect a gzipped OUTCAR without decompressing
zgrep "energy(sigma->0)" production/_ch2ohcoo_p_h/0.4V/fine_opt/OUTCAR.gz | tail -1

# rebuild and verify a POTCAR (licensed library required)
python fetch/make_potcar.py production/_ch2ohcoo_p_h/0.4V/fine_opt /path/to/potpaw_PBE
```

The `OUTCAR.gz` files were produced with `gzip -9 -n`, so the checksums are
reproducible from the original files.

## Citation

If you use these data, please cite the corresponding manuscript (DOI to be
added). The derived ledger and ladder are also described in
`derived/README.md`.

## License

The non-POTCAR content of this repository (input files, VASP outputs, scripts,
manifests, and derived tables) is released under the MIT License. See
`LICENSE`.

POTCAR files are not included and remain subject to the VASP license.
