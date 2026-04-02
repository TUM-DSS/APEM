# Overview

This section groups unit-based scripts by workflow goal rather than by file name.

## Prerequisites

- Run from the repository root.
- Use the project virtual environment.
- Ensure datasets referenced by each script are available.

## Workflow Map

- `Price Analysis`: compare pricing outcomes across pricing algorithms or zonal models.
- `Cost Analysis`: compare welfare-derived costs and related metrics.
- `Redispatch Analysis`: compare redispatch algorithms and redispatch costs.
- `Node Ranking`: compute graph-based and market-metric-based node rankings.

## Results Location

Most scripts write timestamped outputs under:

`results/unit_based_model/<scenario>_results/evaluation/`
