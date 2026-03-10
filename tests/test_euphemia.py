from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from apem.EU_market_model.euphemia.data.conversion.data_conversion import DataConversion
from apem.EU_market_model.euphemia.data.parsing.parse_eu import transform_step_orders
from apem.EU_market_model.euphemia.enums.cut_types import CutTypes
from apem.EU_market_model.euphemia.enums.datasets import EU_Datasets
from apem.EU_market_model.euphemia.euphemia_config import EuphemiaConfig
from apem.EU_market_model.euphemia.runner import solve_euphemia


def _dummy_conversion(periods=(1, 2, 3, 4)):
    scenario = SimpleNamespace(
        df_buyers=pd.DataFrame(),
        df_sellers=pd.DataFrame(),
        periods=list(periods),
        blocks_buyers=[1],
        blocks_sellers=[1],
    )
    return DataConversion(scenario)


def test_apply_overrides_updates_known_fields(monkeypatch):
    """Known euphemia overrides should be applied to config attributes."""
    monkeypatch.setattr(EuphemiaConfig, "set_dataset", lambda self, dataset: None)
    config = EuphemiaConfig()

    overrides = {
        "max_iterations": 7,
        "reinsertion_max_iterations": 3,
        "max_prb_reinsertion_attempts": 5,
        "output_flag": 1,
        "time_limit": 120,
        "mip_gap": 1e-5,
    }
    config.apply_overrides(overrides)

    assert config.max_iterations == 7
    assert config.reinsertion_max_iterations == 3
    assert config.max_prb_reinsertion_attempts == 5
    assert config.output_flag == 1
    assert config.time_limit == 120
    assert config.mip_gap == 1e-5


def test_apply_overrides_rejects_unknown_keys(monkeypatch):
    """Unknown euphemia override fields should raise a clear error."""
    monkeypatch.setattr(EuphemiaConfig, "set_dataset", lambda self, dataset: None)
    config = EuphemiaConfig()

    with pytest.raises(ValueError, match="Invalid Euphemia configuration key"):
        config.apply_overrides({"does_not_exist": 123})


def test_set_dataset_updates_dataset_name_and_scenario():
    """set_dataset should persist enum-name and parsed scenario object."""
    parsed_scenario = {"name": "dummy-scenario"}
    dataset = SimpleNamespace(
        name="DUMMY",
        value=SimpleNamespace(parse_data=lambda: parsed_scenario),
    )

    # Bypass __init__ to test set_dataset in isolation.
    config = object.__new__(EuphemiaConfig)
    config.set_dataset(dataset)

    assert config.dataset == "DUMMY"
    assert config.scenario == parsed_scenario


@patch("apem.EU_market_model.euphemia.runner.MasterProblem")
@patch("apem.EU_market_model.euphemia.runner.EuphemiaConfig")
def test_solve_euphemia_wires_config_and_runs(config_cls, master_problem_cls):
    """solve_euphemia should apply overrides, set dataset/cut type, and run master problem."""
    config = config_cls.return_value
    euphemia = master_problem_cls.return_value
    overrides = {"max_iterations": 11, "output_flag": 1}

    solve_euphemia(EU_Datasets.GME, CutTypes.PB, overrides)

    config.apply_overrides.assert_called_once_with(overrides)
    config.set_dataset.assert_called_once_with(EU_Datasets.GME)
    assert config.cutting_strategy == CutTypes.PB
    master_problem_cls.assert_called_once_with(config)
    euphemia.run.assert_called_once_with()


@patch("apem.EU_market_model.euphemia.runner.MasterProblem")
@patch("apem.EU_market_model.euphemia.runner.EuphemiaConfig")
def test_solve_euphemia_none_overrides_defaults_to_empty_dict(config_cls, master_problem_cls):
    """Passing None overrides should call apply_overrides with an empty dict."""
    config = config_cls.return_value

    solve_euphemia(EU_Datasets.OMIE, CutTypes.CB, None)

    config.apply_overrides.assert_called_once_with({})
    config.set_dataset.assert_called_once_with(EU_Datasets.OMIE)


def test_transform_step_orders_sell_side_increments_are_computed_per_period():
    orders = pd.DataFrame(
        [
            {"id": "s1", "t": 1, "p": 10, "q": 10},
            {"id": "s2", "t": 1, "p": 20, "q": 25},
            {"id": "s3", "t": 1, "p": 30, "q": 40},
            {"id": "s4", "t": 2, "p": 15, "q": 8},
        ]
    )

    transformed = transform_step_orders(orders, periods=[1, 2], sell=True)

    assert transformed["id"].tolist() == ["s1", "s2", "s3", "s4"]
    assert transformed["q"].tolist() == [10, 15, 15, 8]


def test_transform_step_orders_buy_side_keeps_last_level_for_period():
    orders = pd.DataFrame(
        [
            {"id": "b1", "t": 1, "p": 100, "q": -10},
            {"id": "b2", "t": 1, "p": 90, "q": -30},
            {"id": "b3", "t": 1, "p": 80, "q": -60},
        ]
    )

    transformed = transform_step_orders(orders, periods=[1], sell=False)

    # Current implementation explicitly sets last segment to previous level.
    assert transformed["q"].tolist()[-1] == -60


def test_transform_step_orders_filters_by_scalable_order_id():
    orders = pd.DataFrame(
        [
            {"id": "x1", "scalable_order_id": "A", "t": 1, "p": 10, "q": 5},
            {"id": "x2", "scalable_order_id": "A", "t": 1, "p": 20, "q": 9},
            {"id": "y1", "scalable_order_id": "B", "t": 1, "p": 30, "q": 11},
        ]
    )

    transformed = transform_step_orders(
        orders,
        periods=[1],
        sell=True,
        order_id="A",
        scalable=True,
    )

    assert transformed["id"].tolist() == ["x1", "x2"]
    assert transformed["scalable_order_id"].tolist() == ["A", "A"]


def test_block_signature_ignores_identifier_fields():
    conv = _dummy_conversion(periods=(1, 2))

    row_a = pd.Series(
        {
            "id": "r1",
            "block_type": "linked",
            "q1": 1.23456789,
            "q2": 5,
            "p": 42.00001,
            "MAR": 0,
        }
    )
    row_b = pd.Series(
        {
            "id": "r2",
            "block_type": "linked",
            "q1": 1.23456789,
            "q2": 5,
            "p": 42.00001,
            "MAR": 0,
        }
    )

    assert conv.block_signature(row_a) == conv.block_signature(row_b)


def test_compress_blocks_merges_identical_chains_and_updates_parent_reference():
    conv = _dummy_conversion(periods=(1, 2))

    df = pd.DataFrame(
        [
            {"id": "e1", "block_type": "exclusive", "code_prm": "grp", "p": 50, "q1": 10, "q2": 0, "MAR": 1},
            {"id": "l1", "block_type": "linked", "code_prm": "e1", "p": 60, "q1": 0, "q2": 4, "MAR": 0},
            {"id": "e2", "block_type": "exclusive", "code_prm": "grp", "p": 50, "q1": 10, "q2": 0, "MAR": 1},
            {"id": "l2", "block_type": "linked", "code_prm": "e2", "p": 60, "q1": 0, "q2": 4, "MAR": 0},
        ]
    )

    compressed = conv.compress_blocks(df)

    assert len(compressed) == 2

    parent = compressed[compressed["block_type"] == "exclusive"].iloc[0]
    child = compressed[compressed["block_type"] == "linked"].iloc[0]

    assert parent["q1"] == 20
    assert parent["q2"] == 0
    assert parent["MAR"] == 1
    assert "+" in parent["id"]

    assert child["q1"] == 0
    assert child["q2"] == 8
    assert child["code_prm"] == parent["id"]


def test_generate_contiguous_patterns_properties():
    conv = _dummy_conversion(periods=(1, 2, 3, 4))

    patterns = conv.generate_contiguous_patterns(min_uptime=2)

    # For T=4 and min_uptime=2 there are 6 contiguous patterns.
    assert len(patterns) == 6
    # Every pattern encodes all periods.
    assert all(sum(pattern) == 4 for pattern in patterns)
    # There is exactly one contiguous ON segment (>1) per pattern.
    assert all(sum(1 for v in pattern if v > 1) == 1 for pattern in patterns)
