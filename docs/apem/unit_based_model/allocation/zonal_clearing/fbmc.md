# FBMC

Flow-based market coupling zonal-clearing algorithms.

The FBMC implementation and base-case variants follow Byers and Hug (2020), [*Modeling flow-based market coupling: Base case, redispatch, and unit commitment matter*](https://doi.org/10.1109/EEM49802.2020.9221922).

## FBMC Base Cases

`Zonal_FBMC` uses a base case to construct expected nodal net positions before deriving the flow-based network representation. Select the base case through:

```json
{
  "unit_based_model": {
    "zonal_configuration": {
      "base_case": "BC4"
    }
  }
}
```

Supported base cases are:

| Base case | Description |
|---|---|
| `BC1` | Solves the standard nodal UC/DCOPF model and uses the resulting nodal injections directly. |
| `BC2` | Uses the same nodal model as `BC1`, but adds zero zonal net-position constraints for every zone and snapshot. |
| `BC3.1` | Uses the same nodal model as `BC1`, but scales all loads by +20% before solving. |
| `BC3.2` | Uses the same nodal model as `BC1`, but applies random load perturbations in `[-20%, +20%]`. This case is stochastic unless a NumPy random seed is set beforehand. |
| `BC4` | Uses a two-step construction: first relaxes intrazonal line capacities and solves the nodal model to derive zonal reference net positions, then re-solves the original nodal model while fixing zonal net positions to that reference. |

## Zonal FBMC

API path: `apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_fbmc`

```{eval-rst}
.. automodule:: apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_fbmc
   :members:
   :show-inheritance:
```

## Zonal FBMC Included

API path: `apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_fbmc_included`

```{eval-rst}
.. automodule:: apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_fbmc_included
   :members:
   :show-inheritance:
```
