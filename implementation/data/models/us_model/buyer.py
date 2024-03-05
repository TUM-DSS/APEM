from dataclasses import dataclass, field

from implementation.data.models.us_model.bid import DemandBid


@dataclass(kw_only=True)
class Buyer:
    """A buyer in a transmission network that can submit demand bids.

    Attributes:
        id (str): The id of the buyer.
        demand_bids (list[DemandBid]): The demand bids that the buyer submitted.
        node_id (str): The node id of the node the buyer is located at.
    """

    id: str
    node_id: str
    demand_bids: list[DemandBid] = field(default_factory=list)

    def get_demand_bids_per_period(self) -> dict[int, DemandBid]:
        """Get the demand bids of the buyer grouped by period.

        Returns:
            dict[int, DemandBid]: The demand bids by period. The key is the period. A list of demand bids are the values.

        """
        demand_bids_per_period = {}
        for bid in self.demand_bids:
            demand_bids_per_period.setdefault(bid.period, []).append(bid)

        return demand_bids_per_period

    def get_number_of_demand_bids_per_period(self) -> dict[int, int]:
        """Get the number of demand bids grouped by period.

        Returns:
            dict[int, int]: The number of demand bids by period. The key is the period. The number of demand bids are the values.

        """
        demand_bids_per_period = {}
        for bid in self.demand_bids:
            demand_bids_per_period[bid.period] = demand_bids_per_period.get(bid.period, 0) + 1

        return demand_bids_per_period
