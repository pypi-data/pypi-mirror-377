"""Tests for `_ensure_callbacks` behavior."""

from tnfr.callback_utils import (
    _normalize_callbacks,
    CallbackEvent,
    callback_manager,
)


def test_ensure_callbacks_drops_unknown_events(graph_canon):
    G = graph_canon()

    def cb(G, ctx):
        pass

    G.graph["callbacks"] = {
        "nope": [("cb", cb)],
        CallbackEvent.BEFORE_STEP.value: [("cb", cb)],
    }

    callback_manager._ensure_callbacks(G)

    assert list(G.graph["callbacks"]) == [CallbackEvent.BEFORE_STEP.value]


def test_register_callback_cleans_unknown_events(graph_canon):
    G = graph_canon()

    def cb(G, ctx):
        pass

    G.graph["callbacks"] = {"nope": [("cb", cb)]}

    callback_manager.register_callback(G, CallbackEvent.AFTER_STEP, cb, name="cb")

    assert list(G.graph["callbacks"]) == [CallbackEvent.AFTER_STEP.value]


def test_ensure_callbacks_only_processes_dirty_events(graph_canon):
    G = graph_canon()
    from collections import defaultdict

    dummy = object()
    G.graph["callbacks"] = defaultdict(
        list,
        {
            CallbackEvent.BEFORE_STEP.value: [dummy],
            CallbackEvent.AFTER_STEP.value: [dummy],
        },
    )
    G.graph["_callbacks_dirty"] = {CallbackEvent.BEFORE_STEP.value}

    callback_manager._ensure_callbacks(G)

    assert G.graph["callbacks"][CallbackEvent.BEFORE_STEP.value] == {}
    assert G.graph["callbacks"][CallbackEvent.AFTER_STEP.value] == {}


def test_normalize_callbacks_handles_sequences_and_mappings():
    def cb1(G, ctx):
        pass

    def cb2(G, ctx):
        pass

    seq = [("a", cb1), cb2, ("bad", 1)]
    res_seq = _normalize_callbacks(seq)

    assert set(res_seq.keys()) == {"a", "cb2"}
    assert res_seq["a"].func is cb1
    assert res_seq["cb2"].func is cb2

    mapping = {"x": ("a", cb1), "y": cb2, "z": object()}
    res_map = _normalize_callbacks(mapping)

    assert set(res_map.keys()) == {"a", "cb2"}
    assert res_map["a"].func is cb1
    assert res_map["cb2"].func is cb2


def test_normalize_callbacks_handles_iterables():
    def cb1(G, ctx):
        pass

    def cb2(G, ctx):
        pass

    entries = (e for e in [("a", cb1), cb2, ("bad", 1), object()])

    res = _normalize_callbacks(entries)

    assert set(res.keys()) == {"a", "cb2"}
    assert res["a"].func is cb1
    assert res["cb2"].func is cb2
