from enum import StrEnum


class BidSense(StrEnum):
    """Enum class for the sense of a bid.

    Enums:
        SUPPLY (str): Bid sense for supply bids.
        DEMAND (str): Bid sense for demand bids.
    """

    SUPPLY: str = "supply"
    DEMAND: str = "demand"
