# Getting Started

## Installation

1. Create and activate a virtual environment.

```bash
python -m venv apem-venv
source ./apem-venv/bin/activate  # macOS/Linux
```

2. Install dependencies.

```bash
pip install -r requirements.txt
pip install -e .
```

3. Make sure you have a valid Gurobi license if you plan to run optimization models.

## First Run

1. Update `config.json` in the repository root.
2. Run the entrypoint:

```bash
python main.py
```

Results are written to:

- `results/unit_based_model/...` for unit-based runs
- `results/order_book_based_model/...` for order-book-based runs

## Testing

Run test suite:

```bash
pytest
```
