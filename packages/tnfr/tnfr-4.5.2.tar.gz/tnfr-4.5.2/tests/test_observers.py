"""Pruebas de observers."""

import math
import statistics as st
from collections import deque
import pytest

import tnfr.import_utils as import_utils

from tnfr.constants import get_aliases
from tnfr.observers import (
    phase_sync,
    kuramoto_order,
    kuramoto_metrics,
    glyph_load,
    wbar,
)
from tnfr.gamma import kuramoto_R_psi
from tnfr.sense import sigma_vector
from tnfr.constants_glyphs import ANGLE_MAP
from tnfr.helpers.numeric import angle_diff
from tnfr.alias import set_attr
from tnfr.callback_utils import CallbackEvent
from tnfr.observers import attach_standard_observer

ALIAS_THETA = get_aliases("THETA")


def test_phase_observers_match_manual_calculation(graph_canon):
    G = graph_canon()
    angles = [0.0, math.pi / 2, math.pi]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    X = [math.cos(th) for th in angles]
    Y = [math.sin(th) for th in angles]
    th_mean = math.atan2(sum(Y), sum(X))
    var = st.pvariance(angle_diff(th, th_mean) for th in angles)
    expected_sync = 1.0 / (1.0 + var)
    ps = phase_sync(G)
    assert 0.0 <= ps <= 1.0
    assert math.isclose(ps, expected_sync)

    R = ((sum(X) ** 2 + sum(Y) ** 2) ** 0.5) / len(angles)
    assert math.isclose(kuramoto_order(G), float(R))

    R_calc, psi_calc = kuramoto_R_psi(G)
    ps_again = phase_sync(G, R_calc, psi_calc)
    R_again = kuramoto_order(G, R_calc, psi_calc)
    assert math.isclose(ps_again, ps)
    assert math.isclose(R_again, R)


def test_phase_sync_equivalent_with_without_numpy(monkeypatch, graph_canon):
    pytest.importorskip("numpy")
    G = graph_canon()
    angles = [0.1, -2.0, 2.5, 3.0]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    ps_np = phase_sync(G)
    monkeypatch.setattr(import_utils, "cached_import", lambda *a, **k: None)
    monkeypatch.setattr("tnfr.observers.get_numpy", import_utils.get_numpy)
    ps_py = phase_sync(G)
    assert ps_np == pytest.approx(ps_py)


# NumPy and pure-Python variants should match numerically
def test_phase_sync_numpy_and_python_consistent(monkeypatch, graph_canon):
    pytest.importorskip("numpy")
    G = graph_canon()
    angles = [0.2, -1.0, 1.5, 2.1]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    ps_np = phase_sync(G)
    monkeypatch.setattr("tnfr.import_utils.get_numpy", lambda: None)
    monkeypatch.setattr("tnfr.observers.get_numpy", lambda: None)
    ps_py = phase_sync(G)
    assert ps_np == pytest.approx(ps_py)


def test_phase_sync_bounds(graph_canon):
    G = graph_canon()
    angles = [0.1, 1.2, -2.5, 3.6]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    ps = phase_sync(G)
    assert 0.0 <= ps <= 1.0


def test_kuramoto_order_matches_kuramoto_R_psi(graph_canon):
    G = graph_canon()
    angles = [0.1, 1.5, 2.9]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    R_ok = kuramoto_order(G)
    R, psi = kuramoto_R_psi(G)
    assert math.isclose(R_ok, R)
    assert math.isclose(kuramoto_order(G, R, psi), R)
    assert math.isclose(phase_sync(G, R, psi), phase_sync(G))


def test_phase_sync_and_kuramoto_order_share_metrics(monkeypatch, graph_canon):
    G = graph_canon()
    angles = [0.1, 1.5, 2.9]
    for idx, th in enumerate(angles):
        G.add_node(idx)
        set_attr(G.nodes[idx], ALIAS_THETA, th)

    calls = {"count": 0}

    def wrapped(G_inner):
        calls["count"] += 1
        return kuramoto_R_psi(G_inner)

    monkeypatch.setattr("tnfr.observers.kuramoto_R_psi", wrapped)

    R, psi = kuramoto_metrics(G)
    assert calls["count"] == 1

    ps = phase_sync(G, R, psi)
    R_val = kuramoto_order(G, R, psi)

    assert calls["count"] == 1

    var = st.pvariance(angle_diff(th, psi) for th in angles)
    expected_ps = 1.0 / (1.0 + var)
    assert ps == pytest.approx(expected_ps)
    assert R_val == pytest.approx(R)


def test_glyph_load_uses_module_constants(monkeypatch, graph_canon):
    G = graph_canon()
    G.add_node(0, glyph_history=["A"])
    G.add_node(1, glyph_history=["B"])

    # Patch constants to custom categories
    monkeypatch.setattr(
        "tnfr.observers.GLYPH_GROUPS",
        {"estabilizadores": ["A"], "disruptivos": ["B"]},
    )

    dist = glyph_load(G)

    assert dist["_estabilizadores"] == pytest.approx(0.5)
    assert dist["_disruptivos"] == pytest.approx(0.5)


def test_sigma_vector_consistency():
    # Distribución ficticia de glyphs
    dist = {"IL": 0.4, "RA": 0.3, "ZHIR": 0.1, "AL": 0.2}

    res = sigma_vector(dist)
    n = res["n"]

    # Cálculo esperado con el mapa de ángulos canónico
    keys = list(dist.keys())
    angles = {k: ANGLE_MAP[k] for k in keys}
    x = sum(dist[k] * math.cos(angles[k]) for k in keys) / len(keys)
    y = sum(dist[k] * math.sin(angles[k]) for k in keys) / len(keys)
    mag = math.hypot(x, y)
    ang = math.atan2(y, x)

    assert n == len(keys)
    assert math.isclose(res["x"], x)
    assert math.isclose(res["y"], y)
    assert math.isclose(res["mag"], mag)
    assert math.isclose(res["angle"], ang)


def test_wbar_accepts_deque(graph_canon):
    G = graph_canon()
    cs = deque([0.1, 0.5, 0.9], maxlen=10)
    G.graph["history"] = {"C_steps": cs}
    assert wbar(G, window=2) == pytest.approx((0.5 + 0.9) / 2)


def test_wbar_list_and_deque_same_result(graph_canon):
    G = graph_canon()
    data = [0.1, 0.5, 0.9]
    expected = (0.5 + 0.9) / 2

    G.graph["history"] = {"C_steps": data}
    assert wbar(G, window=2) == pytest.approx(expected)

    G.graph["history"] = {"C_steps": deque(data, maxlen=10)}
    assert wbar(G, window=2) == pytest.approx(expected)


@pytest.mark.parametrize("w", [0, -1])
def test_wbar_rejects_non_positive_window(graph_canon, w):
    G = graph_canon()
    G.graph["history"] = {"C_steps": [0.1, 0.2]}
    with pytest.raises(ValueError):
        wbar(G, window=w)


@pytest.mark.parametrize("w", [-1])
def test_glyph_load_rejects_non_positive_window(graph_canon, w):
    G = graph_canon()
    with pytest.raises(ValueError):
        glyph_load(G, window=w)


def test_glyph_load_zero_window(graph_canon):
    G = graph_canon()
    assert glyph_load(G, window=0) == {"_count": 0}


def test_wbar_uses_default_window(monkeypatch, graph_canon):
    G = graph_canon()
    hist = G.graph.setdefault("history", {})
    hist["C_steps"] = [0.5, 1.0, 1.5]
    monkeypatch.setattr("tnfr.observers.DEFAULT_WBAR_SPAN", 2)
    assert wbar(G) == pytest.approx((1.0 + 1.5) / 2)


def test_attach_standard_observer_registers_callbacks(graph_canon):
    G = graph_canon()
    attach_standard_observer(G)
    for ev in CallbackEvent:
        assert ev in G.graph["callbacks"]


def test_attach_standard_observer_idempotent(graph_canon):
    G = graph_canon()
    attach_standard_observer(G)
    callbacks = {ev: dict(cbs) for ev, cbs in G.graph["callbacks"].items()}
    attach_standard_observer(G)
    assert {
        ev: dict(cbs) for ev, cbs in G.graph["callbacks"].items()
    } == callbacks
