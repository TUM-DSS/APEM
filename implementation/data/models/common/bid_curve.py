from dataclasses import dataclass, field

from implementation.data.models.common.size_cost_point import SizeCostPoint
from implementation.data.models.common.curve_type import CurveType


@dataclass()
class BidCurve:
    """The size cost curve of a bid.

    Attributes:
        curve_type (CurveType): The type of the curve. Default is CurveType.LINEAR.
        size_cost_points (list[SizeCostPoint]): The datapoints of the curve.
    """

    curve_type: CurveType = CurveType.LINEAR
    size_cost_points: list[SizeCostPoint] = field(default_factory=list)
