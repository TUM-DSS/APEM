from dataclasses import dataclass, field

from implementation.data.models.us_model.buyer import Buyer
from implementation.data.models.us_model.seller import Seller


@dataclass()
class Node:
    """A node in a transmission network.

    Attributes:
        id (str): The id of a node.
        min_voltage_magnitude (float): The minimal value that the voltage magnitude can be at the node. Default is None.
        max_voltage_magnitude (float): The maximal value that the voltage magnitude can be at the node. Default is None.
        buyers (dict[str, Buyer]): The ids mapped to the buyers that are located at the node.
        sellers (dict[str, Seller]): The ids mapped to the sellers that are located at the node.
        zone (str): The zone that the node is located in. Default is None.
    """

    id: str
    min_voltage_magnitude: float = None
    max_voltage_magnitude: float = None
    buyers: dict[str, Buyer] = field(default_factory=dict)
    sellers: dict[str, Seller] = field(default_factory=dict)
    zone: str = None

    def get_number_of_supply_bids_per_period(self) -> dict[int, int]:
        """Get the number of supply bids grouped per period.
        Counts the number of supply bids from all sellers at this node.

        Returns:
            dict[int, int]: The number of supply bids per period. The key is the period. The number of supply bids are the values.

        """
        number_of_supply_bids_per_period = {}
        for sellers in self.sellers.values():
            number_of_supply_bids = sellers.get_number_of_supply_bids_per_period()
            for period, count in number_of_supply_bids.items():
                number_of_supply_bids_per_period[period] = (
                    number_of_supply_bids_per_period.get(period, 0) + count
                )

        return number_of_supply_bids_per_period

    def get_number_of_demand_bids_per_period(self) -> dict[int, int]:
        """Get the number of demand bids grouped per period.
         Counts the number of demand bids from all buyers at this node.

        Returns:
            dict[int, int]: The number of demand bids per period. The key is the period. The number of demand bids are the values.

        """
        number_of_demand_bids_per_period = {}
        for buyers in self.buyers.values():
            number_of_demand_bids = buyers.get_number_of_demand_bids_per_period()
            for period, count in number_of_demand_bids.items():
                number_of_demand_bids_per_period[period] = (
                    number_of_demand_bids_per_period.get(period, 0) + count
                )

        return number_of_demand_bids_per_period
