"""ΔNFR (dynamic network field response) utilities and strategies.

This module provides helper functions to configure, cache and apply ΔNFR
components such as phase, epidemiological state and vortex fields during
simulations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from ..collections_utils import normalize_weights
from ..constants import DEFAULTS, get_aliases, get_param
from ..cache import cached_nodes_and_A
from ..helpers.numeric import angle_diff
from ..metrics.trig import neighbor_phase_mean, _phase_mean_from_iter
from ..alias import (
    get_attr,
    set_dnfr,
)
from ..metrics.trig_cache import compute_theta_trig
from ..metrics.common import merge_and_normalize_weights
from ..import_utils import get_numpy
ALIAS_THETA = get_aliases("THETA")
ALIAS_EPI = get_aliases("EPI")
ALIAS_VF = get_aliases("VF")




@dataclass
class DnfrCache:
    idx: dict[Any, int]
    theta: list[float]
    epi: list[float]
    vf: list[float]
    cos_theta: list[float]
    sin_theta: list[float]
    degs: dict[Any, float] | None = None
    deg_list: list[float] | None = None
    theta_np: Any | None = None
    epi_np: Any | None = None
    vf_np: Any | None = None
    cos_theta_np: Any | None = None
    sin_theta_np: Any | None = None
    deg_array: Any | None = None
    checksum: Any | None = None


__all__ = (
    "default_compute_delta_nfr",
    "set_delta_nfr_hook",
    "dnfr_phase_only",
    "dnfr_epi_vf_mixed",
    "dnfr_laplacian",
)


def _write_dnfr_metadata(
    G, *, weights: dict, hook_name: str, note: str | None = None
) -> None:
    """Write a ``_DNFR_META`` block in ``G.graph`` with the mix and hook name.

    ``weights`` may include arbitrary components (phase/epi/vf/topo/etc.).
    """
    weights_norm = normalize_weights(weights, weights.keys())
    meta = {
        "hook": hook_name,
        "weights_raw": dict(weights),
        "weights_norm": weights_norm,
        "components": [k for k, v in weights_norm.items() if v != 0.0],
        "doc": "ΔNFR = Σ w_i·g_i",
    }
    if note:
        meta["note"] = str(note)
    G.graph["_DNFR_META"] = meta
    G.graph["_dnfr_hook_name"] = hook_name  # string friendly


def _configure_dnfr_weights(G) -> dict:
    """Normalise and store ΔNFR weights in ``G.graph['_dnfr_weights']``.

    Uses ``G.graph['DNFR_WEIGHTS']`` or default values. The result is a
    dictionary of normalised components reused at each simulation step
    without recomputing the mix.
    """
    weights = merge_and_normalize_weights(
        G, "DNFR_WEIGHTS", ("phase", "epi", "vf", "topo"), default=0.0
    )
    G.graph["_dnfr_weights"] = weights
    return weights


def _init_dnfr_cache(G, nodes, prev_cache: DnfrCache | None, checksum, dirty):
    """Initialise or reuse cached ΔNFR arrays."""
    if prev_cache and prev_cache.checksum == checksum and not dirty:
        return (
            prev_cache,
            prev_cache.idx,
            prev_cache.theta,
            prev_cache.epi,
            prev_cache.vf,
            prev_cache.cos_theta,
            prev_cache.sin_theta,
            False,
        )

    idx = {n: i for i, n in enumerate(nodes)}
    theta = [0.0] * len(nodes)
    epi = [0.0] * len(nodes)
    vf = [0.0] * len(nodes)
    cos_theta = [1.0] * len(nodes)
    sin_theta = [0.0] * len(nodes)
    cache = DnfrCache(
        idx=idx,
        theta=theta,
        epi=epi,
        vf=vf,
        cos_theta=cos_theta,
        sin_theta=sin_theta,
        degs=prev_cache.degs if prev_cache else None,
        checksum=checksum,
    )
    G.graph["_dnfr_prep_cache"] = cache
    return (
        cache,
        cache.idx,
        cache.theta,
        cache.epi,
        cache.vf,
        cache.cos_theta,
        cache.sin_theta,
        True,
    )


def _ensure_numpy_vectors(cache: DnfrCache, np):
    """Ensure NumPy copies of cached vectors are initialised and up to date."""

    if cache is None:
        return (None, None, None, None, None)

    arrays = []
    for attr_np, source_attr in (
        ("theta_np", "theta"),
        ("epi_np", "epi"),
        ("vf_np", "vf"),
        ("cos_theta_np", "cos_theta"),
        ("sin_theta_np", "sin_theta"),
    ):
        src = getattr(cache, source_attr)
        arr = getattr(cache, attr_np)
        if src is None:
            setattr(cache, attr_np, None)
            arrays.append(None)
            continue
        if arr is None or len(arr) != len(src):
            arr = np.array(src, dtype=float)
        else:
            np.copyto(arr, src, casting="unsafe")
        setattr(cache, attr_np, arr)
        arrays.append(arr)
    return tuple(arrays)


def _ensure_numpy_degrees(cache: DnfrCache, deg_list, np):
    """Initialise/update NumPy array mirroring ``deg_list``."""

    if cache is None or deg_list is None:
        if cache is not None:
            cache.deg_array = None
        return None
    arr = cache.deg_array
    if arr is None or len(arr) != len(deg_list):
        arr = np.array(deg_list, dtype=float)
    else:
        np.copyto(arr, deg_list, casting="unsafe")
    cache.deg_array = arr
    return arr


def _refresh_dnfr_vectors(G, nodes, cache: DnfrCache):
    """Update cached angle and state vectors for ΔNFR."""
    np = get_numpy()
    trig = compute_theta_trig(((n, G.nodes[n]) for n in nodes), np=np)
    use_numpy = np is not None and G.graph.get("vectorized_dnfr")
    for i, n in enumerate(nodes):
        nd = G.nodes[n]
        cache.theta[i] = trig.theta[n]
        cache.epi[i] = get_attr(nd, ALIAS_EPI, 0.0)
        cache.vf[i] = get_attr(nd, ALIAS_VF, 0.0)
        cache.cos_theta[i] = trig.cos[n]
        cache.sin_theta[i] = trig.sin[n]
    if use_numpy and np is not None:
        _ensure_numpy_vectors(cache, np)
    else:
        cache.theta_np = None
        cache.epi_np = None
        cache.vf_np = None
        cache.cos_theta_np = None
        cache.sin_theta_np = None


def _prepare_dnfr_data(G, *, cache_size: int | None = 128) -> dict:
    """Precompute common data for ΔNFR strategies."""
    weights = G.graph.get("_dnfr_weights")
    if weights is None:
        weights = _configure_dnfr_weights(G)

    np = get_numpy()
    use_numpy = np is not None and G.graph.get("vectorized_dnfr")

    nodes, A = cached_nodes_and_A(G, cache_size=cache_size)
    cache: DnfrCache | None = G.graph.get("_dnfr_prep_cache")
    checksum = G.graph.get("_dnfr_nodes_checksum")
    dirty = bool(G.graph.pop("_dnfr_prep_dirty", False))
    cache, idx, theta, epi, vf, cos_theta, sin_theta, refreshed = (
        _init_dnfr_cache(G, nodes, cache, checksum, dirty)
    )
    if cache is not None:
        _refresh_dnfr_vectors(G, nodes, cache)

    w_phase = float(weights.get("phase", 0.0))
    w_epi = float(weights.get("epi", 0.0))
    w_vf = float(weights.get("vf", 0.0))
    w_topo = float(weights.get("topo", 0.0))
    degs = cache.degs if cache else None
    if w_topo != 0 and (dirty or degs is None):
        degs = dict(G.degree())
        cache.degs = degs
    elif w_topo == 0:
        degs = None
        if cache is not None:
            cache.degs = None

    G.graph["_dnfr_prep_dirty"] = False

    deg_list: list[float] | None = None
    if w_topo != 0.0 and degs is not None:
        if cache.deg_list is None or dirty or len(cache.deg_list) != len(nodes):
            cache.deg_list = [float(degs.get(node, 0.0)) for node in nodes]
        deg_list = cache.deg_list
    else:
        cache.deg_list = None

    if use_numpy and np is not None:
        theta_np, epi_np, vf_np, cos_theta_np, sin_theta_np = _ensure_numpy_vectors(
            cache, np
        )
        deg_array = _ensure_numpy_degrees(cache, deg_list, np)
    else:
        theta_np = None
        epi_np = None
        vf_np = None
        cos_theta_np = None
        sin_theta_np = None
        deg_array = None
        cache.deg_array = None

    return {
        "weights": weights,
        "nodes": nodes,
        "idx": idx,
        "theta": theta,
        "epi": epi,
        "vf": vf,
        "cos_theta": cos_theta,
        "sin_theta": sin_theta,
        "theta_np": theta_np,
        "epi_np": epi_np,
        "vf_np": vf_np,
        "cos_theta_np": cos_theta_np,
        "sin_theta_np": sin_theta_np,
        "w_phase": w_phase,
        "w_epi": w_epi,
        "w_vf": w_vf,
        "w_topo": w_topo,
        "degs": degs,
        "deg_list": deg_list,
        "deg_array": deg_array,
        "A": A,
        "cache_size": cache_size,
        "cache": cache,
    }


def _apply_dnfr_gradients(
    G,
    data,
    th_bar,
    epi_bar,
    vf_bar,
    deg_bar=None,
    degs=None,
):
    """Combine precomputed gradients and write ΔNFR to each node."""
    nodes = data["nodes"]
    theta = data["theta"]
    epi = data["epi"]
    vf = data["vf"]
    w_phase = data["w_phase"]
    w_epi = data["w_epi"]
    w_vf = data["w_vf"]
    w_topo = data["w_topo"]
    if degs is None:
        degs = data.get("degs")

    for i, n in enumerate(nodes):
        g_phase = -angle_diff(theta[i], th_bar[i]) / math.pi
        g_epi = epi_bar[i] - epi[i]
        g_vf = vf_bar[i] - vf[i]
        if w_topo != 0.0 and deg_bar is not None and degs is not None:
            if isinstance(degs, dict):
                deg_i = float(degs.get(n, 0))
            else:
                deg_i = float(degs[i])
            g_topo = deg_bar[i] - deg_i
        else:
            g_topo = 0.0
        dnfr = (
            w_phase * g_phase + w_epi * g_epi + w_vf * g_vf + w_topo * g_topo
        )
        set_dnfr(G, n, float(dnfr))


def _init_bar_arrays(data, *, degs=None, np=None):
    """Prepare containers for neighbour means.

    If ``np`` is provided, NumPy arrays are created; otherwise lists are used.
    ``degs`` is optional and only initialised when the topological term is
    active.
    """

    theta = data["theta"]
    epi = data["epi"]
    vf = data["vf"]
    w_topo = data["w_topo"]
    if np is None:
        np = get_numpy()
    if np is not None:
        th_bar = np.array(theta, dtype=float)
        epi_bar = np.array(epi, dtype=float)
        vf_bar = np.array(vf, dtype=float)
        deg_bar = (
            np.array(degs, dtype=float)
            if w_topo != 0.0 and degs is not None
            else None
        )
    else:
        th_bar = list(theta)
        epi_bar = list(epi)
        vf_bar = list(vf)
        deg_bar = list(degs) if w_topo != 0.0 and degs is not None else None
    return th_bar, epi_bar, vf_bar, deg_bar


def _compute_neighbor_means(
    G,
    data,
    *,
    x,
    y,
    epi_sum,
    vf_sum,
    count,
    deg_sum=None,
    degs=None,
    np=None,
):
    """Return neighbour mean arrays for ΔNFR."""
    w_topo = data["w_topo"]
    theta = data["theta"]
    is_numpy = np is not None and isinstance(count, np.ndarray)
    th_bar, epi_bar, vf_bar, deg_bar = _init_bar_arrays(
        data, degs=degs, np=np if is_numpy else None
    )

    if is_numpy:
        mask = count > 0
        if np.any(mask):
            th_bar[mask] = np.arctan2(
                y[mask] / count[mask], x[mask] / count[mask]
            )
            epi_bar[mask] = epi_sum[mask] / count[mask]
            vf_bar[mask] = vf_sum[mask] / count[mask]
            if w_topo != 0.0 and deg_bar is not None and deg_sum is not None:
                deg_bar[mask] = deg_sum[mask] / count[mask]
        return th_bar, epi_bar, vf_bar, deg_bar

    n = len(theta)
    cos_th = data["cos_theta"]
    sin_th = data["sin_theta"]
    idx = data["idx"]
    nodes = data["nodes"]
    deg_list = data.get("deg_list")
    for i in range(n):
        c = count[i]
        if c:
            node = nodes[i]
            th_bar[i] = _phase_mean_from_iter(
                ((cos_th[idx[v]], sin_th[idx[v]]) for v in G.neighbors(node)),
                theta[i],
            )
            epi_bar[i] = epi_sum[i] / c
            vf_bar[i] = vf_sum[i] / c
            if w_topo != 0.0 and deg_bar is not None and deg_sum is not None:
                deg_bar[i] = deg_sum[i] / c
    return th_bar, epi_bar, vf_bar, deg_bar


def _compute_dnfr_common(
    G,
    data,
    *,
    x,
    y,
    epi_sum,
    vf_sum,
    count,
    deg_sum=None,
    degs=None,
):
    """Compute neighbour means and apply ΔNFR gradients."""
    np = get_numpy()
    th_bar, epi_bar, vf_bar, deg_bar = _compute_neighbor_means(
        G,
        data,
        x=x,
        y=y,
        epi_sum=epi_sum,
        vf_sum=vf_sum,
        count=count,
        deg_sum=deg_sum,
        degs=degs,
        np=np,
    )
    _apply_dnfr_gradients(G, data, th_bar, epi_bar, vf_bar, deg_bar, degs)


def _init_neighbor_sums(data, *, np=None):
    """Initialise containers for neighbour sums."""
    nodes = data["nodes"]
    n = len(nodes)
    w_topo = data["w_topo"]
    if np is not None:
        x = np.zeros(n, dtype=float)
        y = np.zeros(n, dtype=float)
        epi_sum = np.zeros(n, dtype=float)
        vf_sum = np.zeros(n, dtype=float)
        count = np.zeros(n, dtype=float)
        deg_sum = np.zeros(n, dtype=float) if w_topo != 0.0 else None
        degs = None
    else:
        x = [0.0] * n
        y = [0.0] * n
        epi_sum = [0.0] * n
        vf_sum = [0.0] * n
        count = [0] * n
        deg_list = data.get("deg_list")
        if w_topo != 0 and deg_list is not None:
            deg_sum = [0.0] * n
            degs = list(deg_list)
        else:
            deg_sum = None
            degs = None
    return x, y, epi_sum, vf_sum, count, deg_sum, degs


def _build_neighbor_sums_common(G, data, *, use_numpy: bool):
    np = get_numpy()
    nodes = data["nodes"]
    w_topo = data["w_topo"]
    if use_numpy:
        if np is None:  # pragma: no cover - runtime check
            raise RuntimeError(
                "numpy no disponible para la versión vectorizada",
            )
        if not nodes:
            return None
        x, y, epi_sum, vf_sum, count, deg_sum, degs = _init_neighbor_sums(
            data, np=np
        )
        A = data.get("A")
        if A is None:
            _, A = cached_nodes_and_A(G, cache_size=data.get("cache_size"))
            data["A"] = A
        epi = data.get("epi_np")
        vf = data.get("vf_np")
        cos_th = data.get("cos_theta_np")
        sin_th = data.get("sin_theta_np")
        cache = data.get("cache")
        if epi is None or vf is None or cos_th is None or sin_th is None:
            epi = np.array(data["epi"], dtype=float)
            vf = np.array(data["vf"], dtype=float)
            cos_th = np.array(data["cos_theta"], dtype=float)
            sin_th = np.array(data["sin_theta"], dtype=float)
            data["epi_np"] = epi
            data["vf_np"] = vf
            data["cos_theta_np"] = cos_th
            data["sin_theta_np"] = sin_th
            if cache is not None:
                cache.epi_np = epi
                cache.vf_np = vf
                cache.cos_theta_np = cos_th
                cache.sin_theta_np = sin_th
        x[:] = A @ cos_th
        y[:] = A @ sin_th
        epi_sum[:] = A @ epi
        vf_sum[:] = A @ vf
        count[:] = A.sum(axis=1)
        if w_topo != 0.0:
            deg_array = data.get("deg_array")
            if deg_array is None:
                deg_list = data.get("deg_list")
                if deg_list is not None:
                    deg_array = np.array(deg_list, dtype=float)
                    data["deg_array"] = deg_array
                    if cache is not None:
                        cache.deg_array = deg_array
                else:
                    deg_array = count
            deg_sum[:] = A @ deg_array
            degs = deg_array
        return x, y, epi_sum, vf_sum, count, deg_sum, degs
    else:
        x, y, epi_sum, vf_sum, count, deg_sum, degs_list = _init_neighbor_sums(
            data
        )
        idx = data["idx"]
        epi = data["epi"]
        vf = data["vf"]
        cos_th = data["cos_theta"]
        sin_th = data["sin_theta"]
        deg_list = data.get("deg_list")
        for i, node in enumerate(nodes):
            deg_i = degs_list[i] if degs_list is not None else 0.0
            for v in G.neighbors(node):
                j = idx[v]
                x[i] += cos_th[j]
                y[i] += sin_th[j]
                epi_sum[i] += epi[j]
                vf_sum[i] += vf[j]
                count[i] += 1
                if deg_sum is not None:
                    deg_sum[i] += deg_list[j] if deg_list is not None else deg_i
        return x, y, epi_sum, vf_sum, count, deg_sum, degs_list


def _compute_dnfr(G, data, *, use_numpy: bool = False) -> None:
    """Compute ΔNFR using neighbour sums.

    Parameters
    ----------
    G : nx.Graph
        Graph on which the computation is performed.
    data : dict
        Precomputed ΔNFR data as returned by :func:`_prepare_dnfr_data`.
    use_numpy : bool, optional
        When ``True`` the vectorised ``numpy`` strategy is used. Defaults to
        ``False`` to fall back to the loop-based implementation.
    """
    res = _build_neighbor_sums_common(G, data, use_numpy=use_numpy)
    if res is None:
        return
    x, y, epi_sum, vf_sum, count, deg_sum, degs = res
    _compute_dnfr_common(
        G,
        data,
        x=x,
        y=y,
        epi_sum=epi_sum,
        vf_sum=vf_sum,
        count=count,
        deg_sum=deg_sum,
        degs=degs,
    )


def default_compute_delta_nfr(G, *, cache_size: int | None = 1) -> None:
    """Compute ΔNFR by mixing phase, EPI, νf and a topological term.

    Parameters
    ----------
    G : nx.Graph
        Graph on which the computation is performed.
    cache_size : int | None, optional
        Maximum number of edge configurations cached in ``G.graph``. Values
        ``None`` or <= 0 imply unlimited cache. Defaults to ``1`` to keep the
        previous behaviour.
    """
    data = _prepare_dnfr_data(G, cache_size=cache_size)
    _write_dnfr_metadata(
        G,
        weights=data["weights"],
        hook_name="default_compute_delta_nfr",
    )
    np = get_numpy()
    use_numpy = np is not None and G.graph.get("vectorized_dnfr")
    _compute_dnfr(G, data, use_numpy=use_numpy)


def set_delta_nfr_hook(
    G, func, *, name: str | None = None, note: str | None = None
) -> None:
    """Set a stable hook to compute ΔNFR.
    Required signature: ``func(G) -> None`` and it must write ``ALIAS_DNFR``
    in each node. Basic metadata in ``G.graph`` is updated accordingly.
    """
    G.graph["compute_delta_nfr"] = func
    G.graph["_dnfr_hook_name"] = str(
        name or getattr(func, "__name__", "custom_dnfr")
    )
    if "_dnfr_weights" not in G.graph:
        _configure_dnfr_weights(G)
    if note:
        meta = G.graph.get("_DNFR_META", {})
        meta["note"] = str(note)
        G.graph["_DNFR_META"] = meta


def _apply_dnfr_hook(
    G,
    grads: dict[str, Callable[[Any, Any], float]],
    *,
    weights: dict[str, float],
    hook_name: str,
    note: str | None = None,
) -> None:
    """Generic helper to compute and store ΔNFR using ``grads``.

    ``grads`` maps component names to functions ``(G, n, nd) -> float``.
    Each gradient is multiplied by its corresponding weight from ``weights``.
    Metadata is recorded through :func:`_write_dnfr_metadata`.
    """

    for n, nd in G.nodes(data=True):
        total = 0.0
        for name, func in grads.items():
            w = weights.get(name, 0.0)
            if w:
                total += w * func(G, n, nd)
        set_dnfr(G, n, total)

    _write_dnfr_metadata(G, weights=weights, hook_name=hook_name, note=note)


# --- Hooks de ejemplo (opcionales) ---
def dnfr_phase_only(G) -> None:
    """Example: ΔNFR from phase only (Kuramoto-like)."""

    def g_phase(G, n, nd):
        th_i = get_attr(nd, ALIAS_THETA, 0.0)
        th_bar = neighbor_phase_mean(G, n)
        return -angle_diff(th_i, th_bar) / math.pi

    _apply_dnfr_hook(
        G,
        {"phase": g_phase},
        weights={"phase": 1.0},
        hook_name="dnfr_phase_only",
        note="Hook de ejemplo.",
    )


def dnfr_epi_vf_mixed(G) -> None:
    """Example: ΔNFR without phase, mixing EPI and νf."""

    def g_epi(G, n, nd):
        epi_i = get_attr(nd, ALIAS_EPI, 0.0)
        neighbors = list(G.neighbors(n))
        if neighbors:
            total = 0.0
            for v in neighbors:
                total += float(get_attr(G.nodes[v], ALIAS_EPI, epi_i))
            epi_bar = total / len(neighbors)
        else:
            epi_bar = float(epi_i)
        return epi_bar - epi_i

    def g_vf(G, n, nd):
        vf_i = get_attr(nd, ALIAS_VF, 0.0)
        neighbors = list(G.neighbors(n))
        if neighbors:
            total = 0.0
            for v in neighbors:
                total += float(get_attr(G.nodes[v], ALIAS_VF, vf_i))
            vf_bar = total / len(neighbors)
        else:
            vf_bar = float(vf_i)
        return vf_bar - vf_i

    _apply_dnfr_hook(
        G,
        {"epi": g_epi, "vf": g_vf},
        weights={"phase": 0.0, "epi": 0.5, "vf": 0.5},
        hook_name="dnfr_epi_vf_mixed",
        note="Hook de ejemplo.",
    )


def dnfr_laplacian(G) -> None:
    """Explicit topological gradient using Laplacian over EPI and νf."""
    weights_cfg = get_param(G, "DNFR_WEIGHTS")
    wE = float(weights_cfg.get("epi", DEFAULTS["DNFR_WEIGHTS"]["epi"]))
    wV = float(weights_cfg.get("vf", DEFAULTS["DNFR_WEIGHTS"]["vf"]))

    def g_epi(G, n, nd):
        epi = get_attr(nd, ALIAS_EPI, 0.0)
        neigh = list(G.neighbors(n))
        deg = len(neigh) or 1
        epi_bar = (
            sum(get_attr(G.nodes[v], ALIAS_EPI, epi) for v in neigh) / deg
        )
        return epi_bar - epi

    def g_vf(G, n, nd):
        vf = get_attr(nd, ALIAS_VF, 0.0)
        neigh = list(G.neighbors(n))
        deg = len(neigh) or 1
        vf_bar = sum(get_attr(G.nodes[v], ALIAS_VF, vf) for v in neigh) / deg
        return vf_bar - vf

    _apply_dnfr_hook(
        G,
        {"epi": g_epi, "vf": g_vf},
        weights={"epi": wE, "vf": wV},
        hook_name="dnfr_laplacian",
        note="Gradiente topológico",
    )


