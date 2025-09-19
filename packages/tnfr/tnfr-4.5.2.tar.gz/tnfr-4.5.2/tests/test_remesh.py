"""Pruebas de remesh."""

from collections import deque

import pytest

from tnfr.alias import set_attr
from tnfr.callback_utils import CallbackEvent, callback_manager
from tnfr.constants import get_aliases, get_param, inject_defaults
from tnfr.glyph_history import ensure_history
from tnfr.operators import apply_remesh_if_globally_stable
from tnfr.operators.remesh import apply_network_remesh


def test_aplicar_remesh_usa_parametro_personalizado(graph_canon):
    G = graph_canon()
    G.add_node(0)
    inject_defaults(G)
    G.graph["REMESH_REQUIRE_STABILITY"] = False

    # Historial suficiente para el parámetro personalizado
    hist = G.graph.setdefault("history", {})
    hist["stable_frac"] = [1.0, 1.0, 1.0]

    # Historial de EPI necesario para apply_network_remesh
    tau = G.graph["REMESH_TAU_GLOBAL"]
    maxlen = max(2 * tau + 5, 64)
    G.graph["_epi_hist"] = deque(
        [{0: 0.0} for _ in range(tau + 1)], maxlen=maxlen
    )

    # Sin parámetro personalizado no se debería activar
    apply_remesh_if_globally_stable(G)
    assert "_last_remesh_step" not in G.graph

    # Con parámetro personalizado se activa con 3 pasos estables
    apply_remesh_if_globally_stable(G, pasos_estables_consecutivos=3)
    assert G.graph["_last_remesh_step"] == len(hist["stable_frac"])


def test_remesh_alpha_hard_ignores_glyph_factor(graph_canon):
    G = graph_canon()
    G.add_node(0)
    inject_defaults(G)
    G.graph["REMESH_REQUIRE_STABILITY"] = False
    hist = G.graph.setdefault("history", {})
    hist["stable_frac"] = [1.0, 1.0, 1.0]
    tau = G.graph["REMESH_TAU_GLOBAL"]
    maxlen = max(2 * tau + 5, 64)
    G.graph["_epi_hist"] = deque(
        [{0: 0.0} for _ in range(tau + 1)], maxlen=maxlen
    )
    G.graph["REMESH_ALPHA"] = 0.7
    G.graph["REMESH_ALPHA_HARD"] = True
    G.graph["GLYPH_FACTORS"]["REMESH_alpha"] = 0.1
    apply_remesh_if_globally_stable(G, pasos_estables_consecutivos=3)
    meta = G.graph.get("_REMESH_META", {})
    assert meta.get("alpha") == 0.7
    assert G.graph.get("_REMESH_ALPHA_SRC") == "REMESH_ALPHA"


def test_apply_network_remesh_triggers_callback(graph_canon):
    pytest.importorskip("networkx")

    G = graph_canon()
    nodes = [0, 1, 2]
    G.add_nodes_from(nodes)
    inject_defaults(G)

    alias_epi = get_aliases("EPI")
    for idx, node in enumerate(nodes):
        set_attr(G.nodes[node], alias_epi, float(idx))

    hist = ensure_history(G)
    hist.setdefault("C_steps", []).extend([0.0, 1.0])

    tau_g = int(get_param(G, "REMESH_TAU_GLOBAL"))
    tau_l = int(get_param(G, "REMESH_TAU_LOCAL"))
    tau_req = max(tau_g, tau_l)

    snapshots = []
    for offset in range(tau_req + 1):
        snapshots.append(
            {node: float(idx + offset) for idx, node in enumerate(nodes)}
        )

    maxlen = max(tau_req + 5, tau_req + 1)
    G.graph["_epi_hist"] = deque(snapshots, maxlen=maxlen)

    triggered: list[dict] = []

    def on_remesh(graph, ctx):
        triggered.append(ctx)
        assert graph is G

    callback_manager.register_callback(
        G, CallbackEvent.ON_REMESH, on_remesh
    )

    apply_network_remesh(G)

    assert triggered, "El callback ON_REMESH debería ejecutarse"
    ctx = triggered[-1]
    assert ctx["tau_global"] == tau_g
    assert ctx["tau_local"] == tau_l
    assert "alpha" in ctx
