# Project Structure

## Top-Level Layout

- `apem/`: core package.
- `node_ranking/`: standalone node ranking utilities and metrics.
- `tests/`: automated tests.
- `scripts/`: example and batch runs.
- `results/`: run outputs.
- `config.json`: runtime configuration.
- `main.py`: command-line entrypoint.

## Package Highlights

- `apem.execution_chain`: orchestrates scenario solve and analysis flow.
- `apem.config_loader`: reads and validates configuration.
- `apem.unit_based_model`: allocation, pricing, evaluation, and data parsing for unit-based workflows.
- `apem.order_book_based_model`: Euphemia-style order-book pipeline.
