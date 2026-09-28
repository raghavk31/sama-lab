"""Uniform-price double auction, one call per interval.

Asks are sorted up, bids down, and the two step curves are walked to the last quantity at which
the marginal ask is still at or below the marginal bid. Everyone matched pays or receives the
midpoint of that marginal pair, clipped to [feed-in tariff, ceiling]. Where several asks (or bids)
share the marginal price, the marginal quantity is split among them pro rata, so the result does
not depend on the order households were listed in.
"""
from __future__ import annotations

import numpy as np

from .base import ClearResult, empty


def _fill(q: np.ndarray, p: np.ndarray, total: float, marginal: float, strict_better) -> np.ndarray:
    """Allocate `total` kWh: every offer strictly better than the marginal price in full, the
    remainder pro rata across offers at the marginal price."""
    out = np.zeros_like(q)
    better = strict_better(p, marginal)
    at = np.isclose(p, marginal)
    out[better] = q[better]
    rest = total - out.sum()
    if rest > 1e-12 and q[at].sum() > 0:
        out[at] = q[at] * min(1.0, rest / q[at].sum())
    return out


class UniformPrice:
    name = "uniform"

    def clear(self, ask_q, ask_p, bid_q, bid_p, fit, ceiling) -> ClearResult:
        if len(ask_q) == 0 or len(bid_q) == 0 or ask_q.sum() <= 0 or bid_q.sum() <= 0:
            return empty(len(ask_q), len(bid_q))
        ao = np.argsort(ask_p, kind="stable")
        bo = np.argsort(-bid_p, kind="stable")
        S = np.cumsum(ask_q[ao])
        D = np.cumsum(bid_q[bo])
        # Every point where either curve steps; test the segment that starts at each one.
        starts = np.unique(np.concatenate([[0.0], S[:-1], D[:-1]]))
        starts = starts[starts < min(S[-1], D[-1])]
        ia = np.searchsorted(S, starts, side="right")
        ib = np.searchsorted(D, starts, side="right")
        ok = ask_p[ao][ia] <= bid_p[bo][ib]
        if not ok[0]:
            return empty(len(ask_q), len(bid_q))
        last = np.flatnonzero(ok)[-1]          # curves are monotone, so `ok` is a prefix
        a_m, b_m = ask_p[ao][ia[last]], bid_p[bo][ib[last]]
        Q = min(S[ia[last]], D[ib[last]])
        price = float(np.clip((a_m + b_m) / 2, fit, ceiling))
        sold = _fill(ask_q, ask_p, Q, a_m, lambda p, m: p < m - 1e-12)
        bought = _fill(bid_q, bid_p, Q, b_m, lambda p, m: p > m + 1e-12)
        return ClearResult(sold, bought, np.full(len(ask_q), price), np.full(len(bid_q), price))
