from enum import Enum

from apem.US_market_model.allocation.algorithms.zonal_clearing.redispatch.min_abs_cost import MinAbsCostRD
from apem.US_market_model.allocation.algorithms.zonal_clearing.redispatch.min_abs_vol import MinAbsVolRD
from apem.US_market_model.allocation.algorithms.zonal_clearing.redispatch.min_cost import MinCostRD


class RedispatchAlgorithms(Enum):
    MinAbsCostRD = MinAbsCostRD()
    MinAbsVolRD = MinAbsVolRD()
    MinCostRD = MinCostRD()
