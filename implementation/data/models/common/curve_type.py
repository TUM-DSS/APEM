from enum import StrEnum


class CurveType(StrEnum):
    """Specification of the type of bid curves.

    Curve type definitions taken from https://www.nemo-committee.eu/assets/files/euphemia-public-description.pdf

    Enums:
        STEPWISE (str): Stepwise curve type. Stepwise curves containing only step orders (i.e., two consecutive
                  points always have either the same price or the same quantity).
        LINEAR (str): Linear curve type. Linear piecewise curves containing only interpolated orders (i.e., two
                consecutive points of the monotonous curve cannot have the same
                price, except for the first two points defined at the maximum /
                minimum prices of the bidding zone).
    """

    STEPWISE: str = "stepwise"
    LINEAR: str = "linear"
