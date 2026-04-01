from collections.abc import Hashable

import numpy as np


def congestion_rent_contribution_from_lambdas(
    ptdf: np.ndarray,
    nodes: list[Hashable],
    mask: list[int],
    lambda_lines: np.ndarray | list[float],
) -> dict[Hashable, float]:
    """
    Compute I_k = sum_ell lambda_ell * PTDF[ell, k] for each non-slack node k.
    Slack node gets 0 (since its PTDF column is not in ptdf).

    Parameters
    ----------
    ptdf : (m, n-1) array
        PTDF rows = lines, cols = non-slack buses (order = `mask`).
    nodes : list
        All node labels in the order used to build the PTDF.
    mask : list[int]
        Indices of non-slack nodes; ptdf[:, c] corresponds to nodes[mask[c]].
    lambda_lines : (m,) array-like
        Shadow prices (dual values) for each line in PTDF row order.

    Returns
    -------
    contrib : dict
        {node_label: contribution}, slack node(s) have value 0.
    """
    lam = np.asarray(lambda_lines).reshape(-1)
    # contributions for non-slack columns: ptdf^T @ lambda
    adders = ptdf.T @ lam  # shape (n-1,)

    contrib = {n: 0.0 for n in nodes}
    for col, bus_idx in enumerate(mask):
        contrib[nodes[bus_idx]] = float(adders[col])
    return contrib
