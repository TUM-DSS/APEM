import numpy as np
import networkx as nx


# -----------------------------
# DC power flow / PTDF helpers
# -----------------------------
def build_B_matrix(G: nx.Graph, b_attr: str = "B"):
    """
    Build nodal susceptance (Laplacian) matrix B for DC power flow.

    Parameters
    ----------
    G : nx.Graph
        Undirected graph with edge attribute `b_attr` = susceptance.
    b_attr : str
        Edge attribute name for susceptance.

    Returns
    -------
    B : (n, n) np.ndarray
        Nodal susceptance matrix.
    nodes : list
        Node labels in the order used for B.
    node_index : dict
        Map node label -> row/col index in B.
    """
    nodes = list(G.nodes())
    n = len(nodes)
    node_index = {node: idx for idx, node in enumerate(nodes)}

    B = np.zeros((n, n), dtype=float)

    for u, v, data in G.edges(data=True):
        if b_attr not in data:
            raise KeyError(f"Edge ({u}, {v}) missing '{b_attr}' attribute.")
        b = float(data[b_attr])

        i, j = node_index[u], node_index[v]
        # Laplacian construction
        B[i, i] += b
        B[j, j] += b
        B[i, j] -= b
        B[j, i] -= b

    return B, nodes, node_index


def invert_reduced_B(B: np.ndarray, slack_idx: int):
    """
    Invert reduced B (drop slack row/column).

    Returns
    -------
    Binv : (n-1, n-1) np.ndarray
        Inverse of the reduced B matrix.
    mask : list[int]
        Indices of non-slack buses kept in the reduced system.
    full2red : np.ndarray
        Map full-bus index -> reduced index (or -1 for slack).
    """
    n = B.shape[0]
    mask = [k for k in range(n) if k != slack_idx]
    Bred = B[np.ix_(mask, mask)]
    Binv = np.linalg.inv(Bred)

    full2red = np.full(n, -1, dtype=int)
    full2red[mask] = np.arange(n - 1)
    return Binv, mask, full2red


def compute_bus_angle_basis(Binv: np.ndarray, n: int, slack_idx: int, mask: list[int]):
    """
    Compute voltage angle responses θ for **unit injections at each non-slack bus**
    with withdrawal at the slack (i.e., columns are injections).

    Returns
    -------
    theta_full : (n, n-1) np.ndarray
        θ for each non-slack unit injection (slack angle fixed at 0).
        Column k corresponds to bus mask[k].
    """
    # For each non-slack bus r, the RHS is e_r in reduced coordinates.
    I = np.eye(n - 1)
    theta_red = Binv @ I  # (n-1, n-1)

    theta_full = np.zeros((n, n - 1))
    theta_full[np.ix_(mask, np.arange(n - 1))] = theta_red
    # slack angle is already zero row
    return theta_full


def compute_ptdf(G: nx.Graph, slack=None, b_attr: str = "B"):
    """
    Compute PTDF matrix (flows per 1 MW injection at each bus vs withdrawal at slack).

    Returns
    -------
    ptdf : (m, n-1) np.ndarray
        Rows = lines in `edges`, cols = non-slack buses (order = `mask`).
    edges : list[tuple]
        Edge list in the row order of `ptdf`.
    nodes : list
        Node labels in column/angle order used to build B.
    mask : list[int]
        Indices of non-slack buses (maps ptdf columns -> nodes[mask[c]]).
    slack_node : hashable
        The chosen slack node label.
    """
    B, nodes, node_index = build_B_matrix(G, b_attr=b_attr)

    # choose slack
    if slack is None:
        slack_node = nodes[0]
    else:
        slack_node = slack
        if slack_node not in node_index:
            raise ValueError(f"Slack node {slack_node} not in graph.")
    slack_idx = node_index[slack_node]

    # invert reduced B and build bus-angle basis
    Binv, mask, full2red = invert_reduced_B(B, slack_idx)
    theta_full = compute_bus_angle_basis(Binv, n=len(nodes), slack_idx=slack_idx, mask=mask)
    # theta_full: (n, n-1), columns correspond to non-slack buses in `mask`

    # Build PTDF rows for each edge using vectorized difference of angles
    edges = list(G.edges(data=True))
    m = len(edges)
    ncols = len(mask)
    ptdf = np.zeros((m, ncols))

    for row_idx, (u, v, data) in enumerate(edges):
        b = float(data[b_attr])
        iu, iv = node_index[u], node_index[v]
        # flow = b * (theta_u - theta_v) for all unit injections (vectorized over columns)
        ptdf[row_idx, :] = b * (theta_full[iu, :] - theta_full[iv, :])

    return ptdf, edges, nodes, mask, slack_node
