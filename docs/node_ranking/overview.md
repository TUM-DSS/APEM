# Overview

The `node_ranking` package provides:

- Graph-based ranking metrics (degree and betweenness centrality, PTDF contribution).
- Market-based ranking metrics (dispatch, scarcity, congestion-related scores).
- Ranking helpers that return descending `(node, score)` lists.

Typical workflow:

1. Build or load market/network data.
2. Compute one or more node scores.
3. Rank nodes with the corresponding `rank_nodes_by_*` function.
