import pytest

from tnfr.constants import THETA_PRIMARY
from tnfr.metrics import (
    coherence_matrix,
    local_phase_sync,
    local_phase_sync_weighted,
)


def make_graph(graph_canon):
    G = graph_canon()
    G.add_edge(0, 1)
    G.nodes[0][THETA_PRIMARY] = 0.0
    G.nodes[1][THETA_PRIMARY] = 0.0
    return G


def test_local_phase_sync_unweighted(graph_canon):
    G = make_graph(graph_canon)
    r = local_phase_sync(G, 0)
    assert r == pytest.approx(1.0)


def test_local_phase_sync_with_weights(graph_canon):
    G = make_graph(graph_canon)
    nodes, W = coherence_matrix(G)
    r = local_phase_sync_weighted(G, nodes[0], nodes_order=nodes, W_row=W)
    assert r == pytest.approx(1.0)
