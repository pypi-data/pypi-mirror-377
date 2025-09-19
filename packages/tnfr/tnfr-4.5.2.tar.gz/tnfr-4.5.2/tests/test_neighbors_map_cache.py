from types import MappingProxyType

from tnfr.metrics.common import ensure_neighbors_map
from tnfr.cache import increment_edge_version


def test_neighbors_map_reuses_proxy(graph_canon):
    G = graph_canon()
    G.add_edge(1, 2)
    first = ensure_neighbors_map(G)
    assert isinstance(first, MappingProxyType)
    second = ensure_neighbors_map(G)
    assert first is second
    G.add_edge(2, 3)
    increment_edge_version(G)
    third = ensure_neighbors_map(G)
    assert third is not first
