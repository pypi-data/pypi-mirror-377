"""Tests for dynamics helpers."""

import pytest

from tnfr.dynamics import (
    _init_dnfr_cache,
    _refresh_dnfr_vectors,
    _compute_neighbor_means,
    _choose_glyph,
    _prepare_dnfr,
    default_glyph_selector,
    run,
)
from tnfr.alias import get_attr, set_attr
from tnfr.constants import get_aliases
from tnfr.types import Glyph


def test_init_and_refresh_dnfr_cache(graph_canon):
    G = graph_canon()
    for i in range(2):
        G.add_node(i, theta=0.1 * i, EPI=float(i), VF=float(i))
    nodes = list(G.nodes())
    cache, idx, th, epi, vf, _cx, _sx, refreshed = _init_dnfr_cache(
        G, nodes, None, 1, False
    )
    assert refreshed
    _refresh_dnfr_vectors(G, nodes, cache)
    assert th[1] == pytest.approx(0.1)
    cache2, *_rest, refreshed2 = _init_dnfr_cache(G, nodes, cache, 1, False)
    assert not refreshed2
    assert cache2 is cache


def test_compute_neighbor_means_list(graph_canon):
    G = graph_canon()
    G.add_edge(0, 1)
    data = {
        "w_topo": 0.0,
        "theta": [0.0, 0.0],
        "epi": [0.0, 0.0],
        "vf": [0.0, 0.0],
        "cos_theta": [1.0, 1.0],
        "sin_theta": [0.0, 0.0],
        "idx": {0: 0, 1: 1},
        "nodes": [0, 1],
    }
    x = [1.0, 0.0]
    y = [0.0, 0.0]
    epi_sum = [2.0, 0.0]
    vf_sum = [0.0, 0.0]
    count = [1, 0]
    th_bar, epi_bar, vf_bar, deg_bar = _compute_neighbor_means(
        G, data, x=x, y=y, epi_sum=epi_sum, vf_sum=vf_sum, count=count
    )
    assert th_bar[0] == pytest.approx(0.0)
    assert epi_bar[0] == pytest.approx(2.0)
    assert vf_bar[0] == pytest.approx(0.0)
    assert deg_bar is None


def test_choose_glyph_respects_lags(graph_canon):
    G = graph_canon()
    G.add_node(0)

    def selector(G, n):
        return "RA"

    h_al = {0: 2}
    h_en = {0: 0}
    g = _choose_glyph(G, 0, selector, False, h_al, h_en, 1, 5)
    assert g == Glyph.AL
    h_al[0] = 0
    h_en[0] = 6
    g = _choose_glyph(G, 0, selector, False, h_al, h_en, 1, 5)
    assert g == Glyph.EN


def test_run_rejects_negative_steps(graph_canon):
    G = graph_canon()
    with pytest.raises(ValueError):
        run(G, steps=-1)


def test_default_selector_refreshes_norms(graph_canon):
    G = graph_canon()
    G.add_nodes_from((0, 1))

    dnfr_alias = get_aliases("DNFR")
    accel_alias = get_aliases("D2EPI")
    si_alias = get_aliases("SI")

    for node in G.nodes:
        set_attr(G.nodes[node], si_alias, 0.5)

    def assign_metrics(dnfr_map, accel_map):
        def _cb(graph):
            for node, value in dnfr_map.items():
                set_attr(graph.nodes[node], dnfr_alias, value)
            for node, value in accel_map.items():
                set_attr(graph.nodes[node], accel_alias, value)

        return _cb

    G.graph["compute_delta_nfr"] = assign_metrics(
        {0: 10.0, 1: 6.0},
        {0: 8.0, 1: 5.0},
    )
    _prepare_dnfr(G, use_Si=False)
    default_glyph_selector(G, 0)
    norms_initial = G.graph["_sel_norms"]
    assert norms_initial["dnfr_max"] == pytest.approx(10.0)
    assert norms_initial["accel_max"] == pytest.approx(8.0)

    G.graph["compute_delta_nfr"] = assign_metrics(
        {0: 4.0, 1: 2.0},
        {0: 3.0, 1: 1.0},
    )
    _prepare_dnfr(G, use_Si=False)
    default_glyph_selector(G, 0)
    norms_updated = G.graph["_sel_norms"]
    assert norms_updated["dnfr_max"] == pytest.approx(4.0)
    assert norms_updated["accel_max"] == pytest.approx(3.0)

    nd = G.nodes[0]
    dnfr_norm = abs(get_attr(nd, dnfr_alias, 0.0)) / norms_updated["dnfr_max"]
    accel_norm = abs(get_attr(nd, accel_alias, 0.0)) / norms_updated["accel_max"]
    assert dnfr_norm == pytest.approx(1.0)
    assert accel_norm == pytest.approx(1.0)
