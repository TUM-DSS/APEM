from collections.abc import Hashable

import networkx as nx


def compute_node_degree_centrality(G: nx.Graph) -> dict[Hashable, float]:
    """
    Compute (unweighted) degree centrality for all nodes.

    Degree centrality of a node is its degree divided by the maximum possible degree (n-1), so scores lie in [0, 1].
    """
    deg_centrality = nx.degree_centrality(G)
    return deg_centrality


def compute_node_betweenness_centrality(G: nx.Graph) -> dict[Hashable, float]:
    """
    Compute betweenness centrality for all nodes in a graph.

    Betweenness centrality of a node is the fraction of all shortest paths
    between any two nodes that pass through this node. It measures how much
    a node acts as a "bridge" or bottleneck in the network.
    """
    # - weight=None → shortest paths are unweighted (all edges count as length 1).
    # - normalized=True → results are scaled to lie in [0,1].
    bet_centrality = nx.betweenness_centrality(G, weight=None, normalized=True)

    return bet_centrality


def compute_edge_betweenness(
    G: nx.Graph,
    weight: str | None = None,
    normalized: bool = True,
) -> dict[tuple[Hashable, Hashable], float]:
    """
    Compute betweeness centrality for all lines in a graph.
    """
    bet_centrality = nx.edge_betweenness_centrality(G, k=None, normalized=normalized, weight=weight)
    return bet_centrality
