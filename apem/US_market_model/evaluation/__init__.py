"""Generic evaluation utilities for the US market model."""

from apem.US_market_model.evaluation.lost_opp_cost_analysis import (
    load_lost_opp_cost_table,
    validate_lost_opp_cost_table,
)
from apem.US_market_model.evaluation.price_analysis import (
    compare_price_algorithms,
    round_numeric_columns,
    summarize_prices,
    validate_price_table,
)
from apem.US_market_model.evaluation.plotting import (
    plot_average_prices_by_node,
    plot_average_prices_by_period,
    plot_lost_opp_cost_by_component,
    plot_price_boxplot_by_node,
    plot_price_boxplot_by_period,
    statistic_name,
)
from apem.US_market_model.evaluation.run_lookup import (
    ensure_lost_opp_cost_run_for_configuration,
    ensure_run_for_configuration,
    find_latest_matching_lost_opp_cost_run,
    find_latest_matching_run,
    load_lost_opp_costs_from_run,
    load_prices_from_run,
    normalize_run_dir,
    parse_run_config,
)

__all__ = [
    "compare_price_algorithms",
    "ensure_lost_opp_cost_run_for_configuration",
    "ensure_run_for_configuration",
    "find_latest_matching_lost_opp_cost_run",
    "find_latest_matching_run",
    "load_lost_opp_costs_from_run",
    "load_lost_opp_cost_table",
    "load_prices_from_run",
    "normalize_run_dir",
    "parse_run_config",
    "plot_average_prices_by_node",
    "plot_average_prices_by_period",
    "plot_lost_opp_cost_by_component",
    "plot_price_boxplot_by_node",
    "plot_price_boxplot_by_period",
    "round_numeric_columns",
    "statistic_name",
    "summarize_prices",
    "validate_lost_opp_cost_table",
    "validate_price_table",
]
