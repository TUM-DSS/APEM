# APEM PF Relaxations

The `power_flow_relaxations` module provides a runner for comparing power-flow relaxation formulations on ARPA-derived subscenarios.

## Scope

- Run DCOPF and ACOPF relaxation models on connected network subgraphs.
- Compare model behavior across runtime, solve time, memory footprint, welfare, and feasibility violations.
- Produce CSV result files per model and subscenario size.

## Implemented Relaxations

- `DCOPF`
- `Shor SDP`
- `Chordal SDP`
- `Jabr SOCP`
- `QC` variants (local and global sampling modes)
- `NodalBaseModel` base class used by nodal relaxation formulations

## Models

```{toctree}
:maxdepth: 1

models/dcopf
Shor SDP <models/shor>
Chordal SDP <models/chordal_shor>
Jabr SOCP <models/jabr>
models/qc
models/nodal_base_model
```

## Default Run Behavior

`run_relaxations.py` currently defaults to:

- `--batch-size 1`
- subscenario sizes `32` and `160` nodes
- all available relaxation models

Results are written under:

- `relaxation_results/<MODEL_TAG>_<SIZE>_results.csv`

## Entrypoints

- module runner: `power_flow_relaxations.run_relaxations`
- plotting helper: `power_flow_relaxations.create_figures`
