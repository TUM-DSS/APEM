from typing import NamedTuple


class SizeCostPoint(NamedTuple):
    """A size cost point that specifies a data point for a bid curve.

    Attributes:
        size (float): The size of the datapoint.
        cost (float): The cost of the datapoint.
    """

    size: float
    cost: float
