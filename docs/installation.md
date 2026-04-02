# Installation

## Prerequisites

- Python 3.10 or newer.
- A virtual environment tool (`venv` recommended).
- A valid Gurobi license for optimization runs.

## Setup

1. Create a virtual environment:

```bash
python -m venv apem-venv
```

2. Activate it:

```bash
source ./apem-venv/bin/activate  # macOS/Linux
```

3. Install dependencies and package:

```bash
pip install -r requirements.txt
pip install -e .
```
