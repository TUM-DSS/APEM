from dataclasses import dataclass

from implementation.data.models.us_model.node import Node


@dataclass(kw_only=True)
class Line:
    """A line that connects nodes in a transmission network.

    Attributes:
        id (str): The id of the line.
        max_capacity (float): The maximum amount of energy the line can transfer.
        susceptance (float): The susceptance of the line. Default is None.
        conductance (float): The conductance of the line. Default is None.
        origin (Node): The node that the line connects with the destination.
        destination (Node): The node that the line connects with the origin.
    """

    id: str
    max_capacity: float
    origin: Node
    destination: Node
    susceptance: float = None
    conductance: float = None

