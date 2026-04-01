from collections.abc import Hashable

import networkx as nx

from centrality_measures.graph_metrics import compute_edge_betweenness


def rank_lines_edge_betweenness(G: nx.Graph) -> list[tuple[tuple[Hashable, Hashable], float]]:
    """
    Rank lines by edge betweenness centrality.
    """
    bc = compute_edge_betweenness(G)
    return sorted(bc.items(), key=lambda kv: -kv[1])
