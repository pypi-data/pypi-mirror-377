import tnfr
from tnfr.metrics import register_metrics_callbacks


def test_public_exports():
    expected = {
        "__version__",
        "step",
        "run",
        "preparar_red",
        "create_nfr",
    }
    if getattr(tnfr, "_HAS_RUN_SEQUENCE", False):
        expected.add("run_sequence")
    assert set(tnfr.__all__) == expected


def test_basic_flow():
    G, n = tnfr.create_nfr("n1")
    tnfr.preparar_red(G)
    register_metrics_callbacks(G)
    tnfr.step(G)
    tnfr.run(G, steps=2)
    assert len(G.graph["history"]["C_steps"]) == 3


def test_topological_remesh_not_exported():
    assert not hasattr(tnfr, "apply_topological_remesh")
