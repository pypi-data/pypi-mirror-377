"""Reporting helpers for collected metrics."""

from __future__ import annotations

from typing import Any

from heapq import nlargest
from statistics import mean, fmean, StatisticsError

from ..glyph_history import ensure_history
from ..sense import sigma_rose
from .glyph_timing import for_each_glyph

__all__ = [
    "Tg_global",
    "Tg_by_node",
    "latency_series",
    "glyphogram_series",
    "glyph_top",
    "build_metrics_summary",
]


# ---------------------------------------------------------------------------
# Reporting functions
# ---------------------------------------------------------------------------


def Tg_global(G, normalize: bool = True) -> dict[str, float]:
    """Total glyph dwell time per class."""

    hist = ensure_history(G)
    tg_total: dict[str, float] = hist.get("Tg_total", {})
    total = sum(tg_total.values()) or 1.0
    out: dict[str, float] = {}

    def add(g):
        val = float(tg_total.get(g, 0.0))
        out[g] = val / total if normalize else val

    for_each_glyph(add)
    return out


def Tg_by_node(G, n, normalize: bool = False) -> dict[str, float | list[float]]:
    """Per-node glyph dwell summary."""

    hist = ensure_history(G)
    rec = hist.get("Tg_by_node", {}).get(n, {})
    if not normalize:
        out: dict[str, list[float]] = {}

        def copy_runs(g):
            out[g] = list(rec.get(g, []))

        for_each_glyph(copy_runs)
        return out
    out: dict[str, float] = {}

    def add(g):
        runs = rec.get(g, [])
        out[g] = float(mean(runs)) if runs else 0.0

    for_each_glyph(add)
    return out


def latency_series(G) -> dict[str, list[float]]:
    hist = ensure_history(G)
    xs = hist.get("latency_index", [])
    return {
        "t": [float(x.get("t", i)) for i, x in enumerate(xs)],
        "value": [float(x.get("value", 0.0)) for x in xs],
    }


def glyphogram_series(G) -> dict[str, list[float]]:
    hist = ensure_history(G)
    xs = hist.get("glyphogram", [])
    if not xs:
        return {"t": []}
    out: dict[str, list[float]] = {"t": [float(x.get("t", i)) for i, x in enumerate(xs)]}

    def add(g):
        out[g] = [float(x.get(g, 0.0)) for x in xs]

    for_each_glyph(add)
    return out


def glyph_top(G, k: int = 3) -> list[tuple[str, float]]:
    """Top-k structural operators by ``Tg_global`` fraction."""

    k = int(k)
    if k <= 0:
        raise ValueError("k must be a positive integer")
    tg = Tg_global(G, normalize=True)
    return nlargest(k, tg.items(), key=lambda kv: kv[1])


def build_metrics_summary(
    G, *, series_limit: int | None = None
) -> tuple[dict[str, Any], bool]:
    """Collect a compact metrics summary for CLI reporting.

    Parameters
    ----------
    G:
        Graph containing the recorded metrics.
    series_limit:
        Maximum number of samples to keep for each glyphogram series. ``None`` or
        non-positive values disable trimming and return the full history.
    """

    tg = Tg_global(G, normalize=True)
    latency = latency_series(G)
    glyph = glyphogram_series(G)
    rose = sigma_rose(G)

    latency_values = latency.get("value", [])
    try:
        latency_mean = fmean(latency_values)
    except StatisticsError:
        latency_mean = 0.0

    limit: int | None
    if series_limit is None:
        limit = None
    else:
        limit = int(series_limit)
        if limit <= 0:
            limit = None

    def _trim(values: list[Any]) -> list[Any]:
        seq = list(values)
        if limit is None:
            return seq
        return seq[:limit]

    glyph_summary = {k: _trim(v) for k, v in glyph.items()}

    summary = {
        "Tg_global": tg,
        "latency_mean": latency_mean,
        "rose": rose,
        "glyphogram": glyph_summary,
    }
    return summary, bool(latency_values)
