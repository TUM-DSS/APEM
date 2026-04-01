from collections.abc import Hashable
from typing import Any

import networkx as nx
import numpy as np

from centrality_measures.graph_metrics import (
    compute_node_ptdf_contribution_scores,
    compute_node_betweenness_centrality,
    compute_node_degree_centrality,
)


def rank_nodes_by_ptdf(
    ptdf: np.ndarray,
    edges: list[tuple[Hashable, Hashable, dict[str, Any]]],
    nodes: list[Hashable],
    mask: list[int],
    G: nx.Graph,
    method: str = "sum",
    fmax_attr: str = "F_max",
) -> list[tuple[Hashable, float]]:
    """
    Rank nodes by PTDF contribution score.
    """
    scores = compute_node_ptdf_contribution_scores(
        ptdf=ptdf,
        edges=edges,
        nodes=nodes,
        mask=mask,
        G=G,
        method=method,
        fmax_attr=fmax_attr,
    )
    return sorted(scores.items(), key=lambda x: -x[1])


def rank_nodes_by_degree(G: nx.Graph) -> list[tuple[Hashable, float]]:
    """
    Rank nodes by degree centrality.
    """
    # Compute centrality scores (normalized to [0,1])
    deg_centrality = compute_node_degree_centrality(G)
    ranking = sorted(deg_centrality.items(), key=lambda x: -x[1])
    return ranking


def rank_nodes_by_betweenness(G: nx.Graph) -> list[tuple[Hashable, float]]:
    """
    Rank nodes by betweenness centrality.
    """
    bet_centrality = compute_node_betweenness_centrality(G)
    ranking = sorted(bet_centrality.items(), key=lambda x: -x[1])
    return ranking
