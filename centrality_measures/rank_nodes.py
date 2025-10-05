import networkx as nx
import numpy as np

from apem.US_market_model.data.parsing.parse_pypsa_eur_large import ParsePyPSAEurLarge
from centrality_measures.graph_metrics import compute_node_betweenness_centrality, compute_node_degree_centrality
from centrality_measures.ptdf_computation import compute_ptdf


def rank_nodes_by_ptdf(ptdf: np.ndarray, edges, nodes, mask, G: nx.Graph, method: str = "sum",
                       fmax_attr: str = "F_max"):
    """
    Aggregate each column of PTDF (node impact) into a scalar score, then rank.

    Parameters
    ----------
    ptdf : (m, n-1) np.ndarray
        PTDF rows=lines, cols=non-slack buses (order = `mask`).
    edges : list[(u, v, data)]
        Edges matching ptdf rows.
    nodes : list
        All node labels (order used to build B).
    mask : list[int]
        Indices of non-slack buses corresponding to ptdf columns.
    G : nx.Graph
        Graph with edge attribute fmax_attr.
    method : {"sum","max","weighted_sum"}
        - "sum":          sum_l |PTDF_{l,k}|
        - "max":          max_l |PTDF_{l,k}|
        - "weighted_sum": sum_l |PTDF_{l,k}| * F_max(l)
    fmax_attr : str
        Edge attribute used as weight for "weighted_sum".

    Returns
    -------
    ranking : list[(node_label, score)]
        Sorted descending by score. Includes a zero score for the slack bus.
    """
    m, ncols = ptdf.shape

    # Build weights per line if requested (otherwise set to 1)
    if method == "weighted_sum":
        weights = np.array([
            float(G[u][v].get(fmax_attr, 1.0)) for (u, v, _) in edges
        ])
    else:
        weights = np.ones(m)

    # Absolute PTDF values (flow sensitivities cannot be negative)
    abs_ptdf = np.abs(ptdf)  # shape = (m, n-1)

    if method in ("sum", "weighted_sum"):
        # Sum over all lines, optionally weighted by line capacity
        scores_non_slack = (abs_ptdf * weights[:, None]).sum(axis=0)
    elif method == "max":
        # Take the maximum absolute PTDF per node
        scores_non_slack = abs_ptdf.max(axis=0)
    else:
        raise ValueError(f"Unknown method '{method}'.")

    # Place scores back into full node order (slack bus gets score 0)
    scores_full = np.zeros(len(nodes))
    scores_full[np.array(mask)] = scores_non_slack

    # Sort nodes by descending score
    ranking = sorted(zip(nodes, scores_full), key=lambda x: -x[1])
    return ranking


def rank_nodes_by_degree(G: nx.Graph):
    """
    Rank nodes by degree centrality.
    """
    # Compute centrality scores (normalized to [0,1])
    deg_centrality = compute_node_degree_centrality(G)
    ranking = sorted(deg_centrality.items(), key=lambda x: -x[1])
    return ranking


def rank_nodes_by_betweenness(G: nx.Graph):
    """
    Rank nodes by betweenness centrality.
    """
    bet_centrality = compute_node_betweenness_centrality(G)
    ranking = sorted(bet_centrality.items(), key=lambda x: -x[1])
    return ranking


if __name__ == "__main__":
    # Load your graph (with edge attrs: 'B' and 'F_max')
    PyPSAEurLarge = ParsePyPSAEurLarge()
    G = PyPSAEurLarge.parse_data().network

    # Compute PTDF matrix relative to a slack bus
    ptdf, edges, nodes, mask, slack_node = compute_ptdf(G, slack=None, b_attr="B")

    # Rank nodes using PTDF-based congestion-capacity weighting
    ranking = rank_nodes_by_ptdf(ptdf, edges, nodes, mask, G,
                                 method="weighted_sum", fmax_attr="F_max")

    print(f"Slack bus: {slack_node}")
    print("Top 10 important nodes (weighted_sum):")
    for node, score in ranking[:10]:
        print(node, score)

    # Rank by degree centrality
    deg_ranking = rank_nodes_by_degree(G)
    print("\nTop 10 important nodes (degree centrality):")
    for node, score in deg_ranking[:10]:
        print(node, score)

    # Rank by betweenness centrality
    bet_ranking = rank_nodes_by_betweenness(G)
    print("\nTop 10 important nodes (betweenness centrality):")
    for node, score in bet_ranking[:10]:
        print(node, score)
