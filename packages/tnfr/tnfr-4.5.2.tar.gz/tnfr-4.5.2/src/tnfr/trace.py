"""Trace logging.

Field helpers avoid unnecessary copying by reusing dictionaries stored on
the graph whenever possible.  Callers are expected to treat returned
structures as immutable snapshots.
"""

from __future__ import annotations

from functools import partial
from typing import Any, Callable, Optional, Protocol, NamedTuple, TypedDict, cast
from collections.abc import Iterable, Mapping

from .constants import TRACE
from .glyph_history import ensure_history, count_glyphs, append_metric
from .import_utils import cached_import
from .graph_utils import get_graph_mapping
from .collections_utils import is_non_string_sequence


class _KuramotoFn(Protocol):
    def __call__(self, G: Any) -> tuple[float, float]: ...


class _SigmaVectorFn(Protocol):
    def __call__(
        self, G: Any, weight_mode: str | None = None
    ) -> dict[str, float]: ...


class CallbackSpec(NamedTuple):
    """Specification for a registered callback."""

    name: str | None
    func: Callable[..., Any]


class TraceMetadata(TypedDict, total=False):
    """Metadata captured by trace field functions."""

    gamma: Mapping[str, Any]
    grammar: Mapping[str, Any]
    selector: str | None
    dnfr_weights: Mapping[str, Any]
    si_weights: Mapping[str, Any]
    si_sensitivity: Mapping[str, Any]
    callbacks: Mapping[str, list[str] | None]
    thol_open_nodes: int
    kuramoto: Mapping[str, float]
    sigma: Mapping[str, float]
    glyphs: Mapping[str, int]


class TraceSnapshot(TraceMetadata, total=False):
    """Trace snapshot stored in the history."""

    t: float
    phase: str


def _kuramoto_fallback(G: Any) -> tuple[float, float]:
    return 0.0, 0.0


kuramoto_R_psi: _KuramotoFn = cast(
    _KuramotoFn,
    cached_import("tnfr.gamma", "kuramoto_R_psi", fallback=_kuramoto_fallback),
)


def _sigma_fallback(
    G: Any, _weight_mode: str | None = None
) -> dict[str, float]:
    """Return a null sigma vector regardless of ``_weight_mode``."""

    return {"x": 0.0, "y": 0.0, "mag": 0.0, "angle": 0.0, "n": 0}


# Public exports for this module
__all__ = (
    "CallbackSpec",
    "TraceMetadata",
    "TraceSnapshot",
    "register_trace",
    "register_trace_field",
    "_callback_names",
    "gamma_field",
    "grammar_field",
)

# -------------------------
# Helpers
# -------------------------


def _trace_setup(
    G,
) -> tuple[
    Optional[dict[str, Any]], set[str], Optional[dict[str, Any]], Optional[str]
]:
    """Common configuration for trace snapshots.

    Returns the active configuration, capture set, history and key under
    which metadata will be stored. If tracing is disabled returns
    ``(None, set(), None, None)``.
    """

    cfg = G.graph.get("TRACE", TRACE)
    if not cfg.get("enabled", True):
        return None, set(), None, None

    capture: set[str] = set(cfg.get("capture", []))
    hist = ensure_history(G)
    key = cfg.get("history_key", "trace_meta")
    return cfg, capture, hist, key


def _callback_names(
    callbacks: Mapping[str, CallbackSpec] | Iterable[CallbackSpec],
) -> list[str]:
    """Return callback names from ``callbacks``."""
    if isinstance(callbacks, Mapping):
        callbacks = callbacks.values()
    return [
        cb.name
        if cb.name is not None
        else str(getattr(cb.func, "__name__", "fn"))
        for cb in callbacks
    ]


def mapping_field(G: Any, graph_key: str, out_key: str) -> TraceMetadata:
    """Helper to copy mappings from ``G.graph`` into trace output."""
    mapping = get_graph_mapping(
        G, graph_key, f"G.graph[{graph_key!r}] no es un mapeo; se ignora"
    )
    if mapping is None:
        return {}
    return cast(TraceMetadata, {out_key: mapping})


# -------------------------
# Builders
# -------------------------


def _new_trace_meta(
    G, phase: str
) -> Optional[
    tuple[TraceSnapshot, set[str], Optional[dict[str, Any]], Optional[str]]
]:
    """Initialise trace metadata for a ``phase``.

    Wraps :func:`_trace_setup` and creates the base structure with timestamp
    and current phase. Returns ``None`` if tracing is disabled.
    """

    cfg, capture, hist, key = _trace_setup(G)
    if not cfg:
        return None

    meta: TraceSnapshot = {"t": float(G.graph.get("_t", 0.0)), "phase": phase}
    return meta, capture, hist, key


# -------------------------
# Snapshots
# -------------------------


def _trace_capture(
    G, phase: str, fields: Mapping[str, Callable[[Any], TraceMetadata]]
) -> None:
    """Capture ``fields`` for ``phase`` and store the snapshot.

    A :class:`TraceSnapshot` is appended to the configured history when
    tracing is active. If there is no active history or storage key the
    capture is silently ignored.
    """

    res = _new_trace_meta(G, phase)
    if not res:
        return

    meta, capture, hist, key = res
    if not capture:
        return
    for name, getter in fields.items():
        if name in capture:
            meta.update(cast(TraceSnapshot, getter(G)))
    if hist is None or key is None:
        return
    append_metric(hist, key, meta)


# -------------------------
# Registry
# -------------------------


TRACE_FIELDS: dict[str, dict[str, Callable[[Any], TraceMetadata]]] = {}


def register_trace_field(
    phase: str, name: str, func: Callable[[Any], TraceMetadata]
) -> None:
    """Register ``func`` to populate trace field ``name`` during ``phase``."""

    TRACE_FIELDS.setdefault(phase, {})[name] = func


gamma_field = partial(mapping_field, graph_key="GAMMA", out_key="gamma")


grammar_field = partial(mapping_field, graph_key="GRAMMAR_CANON", out_key="grammar")


dnfr_weights_field = partial(
    mapping_field, graph_key="DNFR_WEIGHTS", out_key="dnfr_weights"
)


def selector_field(G: Any) -> TraceMetadata:
    sel = G.graph.get("glyph_selector")
    return cast(TraceMetadata, {"selector": getattr(sel, "__name__", str(sel)) if sel else None})


_si_weights_field = partial(mapping_field, graph_key="_Si_weights", out_key="si_weights")


_si_sensitivity_field = partial(
    mapping_field, graph_key="_Si_sensitivity", out_key="si_sensitivity"
)


def si_weights_field(G: Any) -> TraceMetadata:
    """Return sense-plane weights and sensitivity."""

    return cast(
        TraceMetadata,
        {
            **(_si_weights_field(G) or {"si_weights": {}}),
            **(_si_sensitivity_field(G) or {"si_sensitivity": {}}),
        },
    )


def callbacks_field(G: Any) -> TraceMetadata:
    cb = G.graph.get("callbacks")
    if not isinstance(cb, Mapping):
        return {}
    out: dict[str, list[str] | None] = {}
    for phase, cb_map in cb.items():
        if isinstance(cb_map, Mapping) or is_non_string_sequence(cb_map):
            out[phase] = _callback_names(cb_map)
        else:
            out[phase] = None
    return cast(TraceMetadata, {"callbacks": out})


def thol_state_field(G: Any) -> TraceMetadata:
    th_open = 0
    for _, nd in G.nodes(data=True):
        st = nd.get("_GRAM", {})
        if st.get("thol_open", False):
            th_open += 1
    return cast(TraceMetadata, {"thol_open_nodes": th_open})


def kuramoto_field(G: Any) -> TraceMetadata:
    R, psi = kuramoto_R_psi(G)
    return cast(TraceMetadata, {"kuramoto": {"R": float(R), "psi": float(psi)}})


def sigma_field(G: Any) -> TraceMetadata:
    sigma_vector_from_graph: _SigmaVectorFn = cast(
        _SigmaVectorFn,
        cached_import(
            "tnfr.sense",
            "sigma_vector_from_graph",
            fallback=_sigma_fallback,
        ),
    )
    sv = sigma_vector_from_graph(G)
    return cast(
        TraceMetadata,
        {
            "sigma": {
                "x": float(sv.get("x", 0.0)),
                "y": float(sv.get("y", 0.0)),
                "mag": float(sv.get("mag", 0.0)),
                "angle": float(sv.get("angle", 0.0)),
            }
        },
    )


def glyph_counts_field(G: Any) -> TraceMetadata:
    """Return glyph count snapshot.

    ``count_glyphs`` already produces a fresh mapping so no additional copy
    is taken.  Treat the returned mapping as read-only.
    """

    cnt = count_glyphs(G, window=1)
    return cast(TraceMetadata, {"glyphs": cnt})


# Pre-register default fields
register_trace_field("before", "gamma", gamma_field)
register_trace_field("before", "grammar", grammar_field)
register_trace_field("before", "selector", selector_field)
register_trace_field("before", "dnfr_weights", dnfr_weights_field)
register_trace_field("before", "si_weights", si_weights_field)
register_trace_field("before", "callbacks", callbacks_field)
register_trace_field("before", "thol_open_nodes", thol_state_field)

register_trace_field("after", "kuramoto", kuramoto_field)
register_trace_field("after", "sigma", sigma_field)
register_trace_field("after", "glyph_counts", glyph_counts_field)


# -------------------------
# API
# -------------------------


def register_trace(G) -> None:
    """Enable before/after-step snapshots and dump operational metadata
    to history.

    Trace snapshots are stored as :class:`TraceSnapshot` entries in
    ``G.graph['history'][TRACE.history_key]`` with:
      - gamma: active Γi(R) specification
      - grammar: canonical grammar configuration
      - selector: glyph selector name
      - dnfr_weights: ΔNFR mix declared in the engine
      - si_weights: α/β/γ weights and Si sensitivity
      - callbacks: callbacks registered per phase (if in
        ``G.graph['callbacks']``)
      - thol_open_nodes: how many nodes have an open THOL block
      - kuramoto: network ``(R, ψ)``
      - sigma: global sense-plane vector
      - glyphs: glyph counts after the step

    Field helpers reuse graph dictionaries and expect them to be treated as
    immutable snapshots by consumers.
    """
    if G.graph.get("_trace_registered"):
        return

    from .callback_utils import callback_manager

    for phase in TRACE_FIELDS.keys():
        event = f"{phase}_step"

        def _make_cb(ph):
            def _cb(G, ctx: dict[str, Any] | None = None):
                del ctx

                _trace_capture(G, ph, TRACE_FIELDS.get(ph, {}))

            return _cb

        callback_manager.register_callback(
            G, event=event, func=_make_cb(phase), name=f"trace_{phase}"
        )

    G.graph["_trace_registered"] = True
