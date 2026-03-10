# Test 3-Node Dataset

Small EU EUPHEMIA test instance for validating zonal ATC constraints.

## Structure

- 3 zones (`Z1`, `Z2`, `Z3`)
- 1 period (`t=1`)
- Directed ATC links in `atc.csv`
- Simple step bids plus one block bid

## Files

- `periods.csv`
- `zones.csv`
- `atc.csv`
- `step_orders.csv`
- `block_orders.csv`
- empty placeholders:
  - `complex_orders.csv`
  - `complex_step_orders.csv`
  - `scalable_complex_orders.csv`
  - `scalable_step_orders.csv`
  - `piecewise_linear_orders.csv`

## Usage

Set in `config.json`:

- `run.market_model = "EU_model"`
- `eu_model.dataset = "TEST_3NODE"`

Then run `python main.py`.
