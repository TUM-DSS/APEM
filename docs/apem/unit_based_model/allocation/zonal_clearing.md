# Zonal Clearing

Zonal-clearing allocation algorithms and redispatch routines.

```{toctree}
:maxdepth: 1
:hidden:

zonal_clearing/fbmc
zonal_clearing/ntc_aggregated
zonal_clearing/ntc_multiedge
zonal_clearing/redispatch
```

## Zonal Configurations

Zonal unit-based models map network nodes to bidding zones before solving the
zonal clearing problem. The mapping is selected with
`unit_based_model.zonal_configuration.type` in `config.json`.

```json
"zonal_configuration": {
  "type": "zonal_DE2-s",
  "factor": 0.8,
  "base_case": "BC4"
}
```

The built-in mappings are Germany-focused, coordinate-based approximations of
alternative bidding-zone layouts discussed in the European
[Bidding Zone Review (BZR)](https://www.entsoe.eu/network_codes/bzr/) process.
ACER describes the role of bidding-zone reviews and alternative bidding-zone
configurations on its [Bidding Zone Review](https://www.acer.europa.eu/electricity/market-rules/capacity-allocation-and-congestion-management/bidding-zone-review)
page. The mapping logic is implemented in
[`zonal_configuration.py`](https://github.com/teodora-dobos/APEM/blob/main/apem/unit_based_model/allocation/algorithms/zonal_clearing/zonal_configuration.py).

```{note}
The built-in zonal configurations are currently supported only for the
`PyPSAEurSmall` and `PyPSAEurLarge` unit-based datasets.
```

| configuration | zones | description |
|---|---:|---|
| `national` | 1 | Assigns all nodes to one German zone. |
| `zonal_DE2-k` | 2 | Two-zone German split based on a k-means-style BZR alternative. |
| `zonal_DE2-s` | 2 | Two-zone German split based on a spectral-style BZR alternative. |
| `zonal_DE3` | 3 | Three-zone German split with north-west, north-east, and south zones. |
| `zonal_DE4` | 4 | Four-zone German split with north-west, west, east, and south zones. |
| `zonal_DE5` | 5 | Five-zone German split with an additional northern zone. |

`factor` scales interzonal capacities in the NTC-based zonal models. For
`Zonal_FBMC`, `base_case` selects the FBMC base-case construction; see
[](zonal_clearing/fbmc) for the available base cases.

## Zonal Clearing Package

API path: `apem.unit_based_model.allocation.algorithms.zonal_clearing`

```{eval-rst}
.. automodule:: apem.unit_based_model.allocation.algorithms.zonal_clearing
   :members:
   :show-inheritance:
```

## Zonal Configuration

API path: `apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_configuration`

```{eval-rst}
.. automodule:: apem.unit_based_model.allocation.algorithms.zonal_clearing.zonal_configuration
   :members:
   :show-inheritance:
```
