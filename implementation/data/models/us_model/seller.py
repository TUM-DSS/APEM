from dataclasses import dataclass, field

from implementation.data.models.us_model.bid import SupplyBid


@dataclass(kw_only=True)
class Seller:
    """A seller in a transmission network that can submit supply bids.

    Attributes:
        id (str): The id of the seller.
        min_uptime (float): The minimum amount of time the seller needs to supply energy. Default is 0.
        min_downtime (float): The minimum amount of time the seller needs to be down after supplying energy. Default is 0.
        supply_bids (list[SupplyBid]): The supply bids that the seller submitted.
        node_id (str): The node id of the node the seller is located at.
    """

    id: str
    node_id: str
    min_uptime: float = 0
    min_downtime: float = 0
    supply_bids: list[SupplyBid] = field(default_factory=list)

    def get_supply_bids_per_period(self) -> dict[int, list[SupplyBid]]:
        """Get the supply bids of the seller grouped per period.

        Returns:
            dict[int, SupplyBid]: The supply bids per period. The key is the period. A list of supply bids are the values.

        """
        supply_bids_per_period = {}
        for bid in self.supply_bids:
            supply_bids_per_period.setdefault(bid.period, []).append(bid)

        return supply_bids_per_period

    def get_number_of_supply_bids_per_period(self) -> dict[int, int]:
        """Get the number of supply bids grouped per period.

        Returns:
            dict[int, int]: The number of supply bids per period. The key is the period. The number of supply bids are the values.

        """
        supply_bids_per_period = {}
        for bid in self.supply_bids:
            supply_bids_per_period[bid.period] = supply_bids_per_period.get(bid.period, 0) + 1

        return supply_bids_per_period
