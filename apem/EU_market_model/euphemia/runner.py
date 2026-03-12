from typing import Any, Dict, Optional

from apem.EU_market_model.euphemia.enums.datasets import EU_Datasets
from apem.EU_market_model.euphemia.enums.cut_types import CutTypes
from apem.EU_market_model.euphemia.euphemia_config import EuphemiaConfig
from apem.EU_market_model.euphemia.master_problem.master_problem import MasterProblem


def solve_euphemia(
    dataset: EU_Datasets,
    cut_type: CutTypes,
    config_overrides: Optional[Dict[str, Any]] = None,
):
    """
    Solves an Euphemia scenario.
    Args:
        dataset (Datasets): Used dataset.
        cut_type (CutTypes): Cutting strategy to be used in the solver.

    Returns:

    """
    config = EuphemiaConfig()
    config.apply_overrides(config_overrides or {})
    config.set_dataset(dataset)
    config.cutting_strategy = cut_type
    euphemia = MasterProblem(config)
    euphemia.run()
