# Configuration

APEM uses a model-scoped configuration format in `config.json` with three main sections:

- `run`: global run selection
- `unit_based_model`: settings used when `market_model=unit_based_model`
- `order_book_based_model`: settings used when `market_model=order_book_based_model`

## Minimal Example

```json
{
  "run": {
    "market_model": "order_book_based_model",
    "verbosity": true
  },
  "unit_based_model": {
    "dataset": "ARPA",
    "power_flow_model": { "type": "DCOPF" },
    "pricing_algorithm": "IP",
    "redispatch": {
      "algorithm": "MinCostRD",
      "constraint_units": false,
      "threshold": 0.001,
      "alpha": 0.01
    },
    "solver_configuration": {
      "time_limit": 3600,
      "slack_penalty": 1e15
    }
  },
  "order_book_based_model": {
    "dataset": "GME",
    "cut_type": "price based",
    "euphemia_configuration": {
      "max_iterations": 50
    }
  }
}
```

## Main Option Groups

- Market models: `unit_based_model`, `order_book_based_model`
- Unit-based datasets: `IEEE_RTS`, `PJM`, `PyPSAEurSmall`, `PyPSAEurLarge`, `ARPA`
- Order-book datasets: `Generated Small`, `Generated Large`, `OMIE`, `GME`, `IEEE_RTS`, `ARPA`
- Power-flow models: `DCOPF`, `Zonal_NTC_aggregated`, `Zonal_NTC_multiedge`, `Zonal_FBMC`
- Pricing algorithms: `ELMP`, `IP`, `MinMWP`, `Join`
- Redispatch algorithms: `MinCostRD`, `MinAbsCostRD`, `MinAbsVolRD`

## Validation Logic

Configuration parsing and validation are implemented in `apem.config_loader.ConfigLoader`.
See the API page for method-level behavior.
