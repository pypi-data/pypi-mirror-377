import networkx as nx

from tnfr.cache import ensure_node_offset_map
from tnfr.node import NodoNX


def test_nodonx_offset_uses_cached_mapping(graph_canon):
    graph = graph_canon()
    graph.add_nodes_from([0, 1, 2])
    ensure_node_offset_map(graph)

    node = NodoNX(graph, 2)

    expected_offset = ensure_node_offset_map(graph)[2]
    assert node.offset() == expected_offset


def test_nodonx_offset_defaults_to_zero():
    graph = nx.Graph()
    graph.add_node(0)

    node = NodoNX(graph, 0)

    assert node.offset() == 0
