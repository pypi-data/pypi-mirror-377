from __future__ import annotations

from ..cache import cached_node_list
from ..rng import _rng_for_step, base_seed

__all__ = ("update_node_sample",)


def update_node_sample(G, *, step: int) -> None:
    """Refresh ``G.graph['_node_sample']`` with a random subset of nodes.

    The sample is limited by ``UM_CANDIDATE_COUNT`` and refreshed every
    simulation step. When the network is small (``< 50`` nodes) or the limit
    is non‑positive, the full node set is used and sampling is effectively
    disabled. A snapshot of nodes is cached via a
    :class:`~tnfr.cache.NodeCache` instance stored in
    ``G.graph['_node_list_cache']`` and reused across steps; it is only refreshed
    when the graph size changes. Sampling operates directly on the cached
    tuple of nodes.
    """
    graph = G.graph
    limit = int(graph.get("UM_CANDIDATE_COUNT", 0))
    nodes = cached_node_list(G)
    current_n = len(nodes)
    if limit <= 0 or current_n < 50 or limit >= current_n:
        graph["_node_sample"] = nodes
        return

    seed = base_seed(G)
    rng = _rng_for_step(seed, step)
    graph["_node_sample"] = rng.sample(nodes, limit)
