from dataclasses import dataclass, field

from implementation.data.models.us_model.line import Line
from implementation.data.models.us_model.node import Node


@dataclass
class TransmissionNetwork:
    """A transmission network consisting of nodes connected by lines.

    Attributes:
        is_per_unit (bool): Whether the data in the transmission network is specified on a per-unit basis. Default is False.
        base_mva (int): The per unit base value. Default is None.
        lines (dict[str, Line]): The lines of the network. The key is the id of the line.
        nodes (dict[str, Node]): The nodes of the network. The key is the id of the node.

    """

    is_per_unit: bool = False
    base_mva: int = None
    lines: dict[str, Line] = field(default_factory=dict)
    nodes: dict[str, Node] = field(default_factory=dict)

    def get_number_of_sellers(self) -> int:
        """Get the number of sellers in the network.

        Returns:
            int: The number of sellers in the network.

        """
        return sum([len(node.sellers) for node in self.nodes.values()])

    def get_number_of_buyers(self) -> int:
        """Get the number of buyers in the network.

        Returns:
            int: The number of buyers in the network.

        """
        return sum([len(node.buyers) for node in self.nodes.values()])

    def get_number_of_supply_bids_per_period(self) -> dict[int, int]:
        """Get the number of supply bids in the network grouped by period.

        Returns:
            dict[int, int]: The number of supply bids grouped by period. The key is the period. The number of supply bids are the values.

        """
        number_of_supply_bids_per_period = {}
        for node in self.nodes.values():
            number_of_supply_bids = node.get_number_of_supply_bids_per_period()
            for period, count in number_of_supply_bids.items():
                number_of_supply_bids_per_period[period] = (
                        number_of_supply_bids_per_period.get(period, 0) + count
                )

        return number_of_supply_bids_per_period

    def get_number_of_demand_bids_per_period(self) -> dict[int, int]:
        """Get the number of demand bids in the network grouped by period.

        Returns:
            dict[int, int]: The number of supply bids grouped by period. The key is the period. The number of demand bids are the values.

        """
        number_of_demand_bids_per_period = {}
        for buyers in self.nodes.values():
            number_of_demand_bids = buyers.get_number_of_demand_bids_per_period()
            for period, count in number_of_demand_bids.items():
                number_of_demand_bids_per_period[period] = (
                        number_of_demand_bids_per_period.get(period, 0) + count
                )

        return number_of_demand_bids_per_period
