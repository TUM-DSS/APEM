from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

from implementation.data.models.common.bid_curve import BidCurve
from implementation.data.models.common.bid_sense import BidSense


@dataclass(kw_only=True, init=False)
class Bid(ABC):
    """An abstract bid that specifies the structure for supply and demand bids.

    Attributes:
        period (int): The period the bid belongs to.
        min_real_power (float): The minimum real power or inelastic demand. Default is None.
        max_real_power (float): The maximum real power that the bidder can handle/provide. Default is None.
        min_reactive_power (float): The minimum reactive power. Default is None.
        max_reactive_power (float): The maximum reactive power. Default is None.
        max_ramp_up_rate (float): The maximum ramp up rate. Default is None.
        max_ramp_down_rate (float): The maximum ramp down rate. Default is None.
        bid_curve (BidCurve): The bid curve of the bid.
    """

    period: int
    bid_curve: BidCurve
    min_real_power: float = None
    max_real_power: float = None
    min_reactive_power: float = None
    max_reactive_power: float = None


@dataclass
class SupplyBid(Bid):
    """A supply bid.

    Attributes:
        sense (BidSense): Class variable defining the bid sense of a supply bid as SUPPLY.
        no_load_cost (float): The no load cost of a supplier.
        startup_cost (float): The startup cost of a supplier.
    """

    sense: ClassVar[BidSense] = BidSense.SUPPLY
    no_load_cost: float = 0
    startup_cost: float = 0
    max_ramp_up_rate: float = None
    max_ramp_down_rate: float = None

@dataclass()
class DemandBid(Bid):
    """A demand bid.

    Attributes:
        sense (BidSense): Class variable defining the bid sense of a supply bid as DEMAND.
    """

    sense: ClassVar[BidSense] = BidSense.DEMAND
