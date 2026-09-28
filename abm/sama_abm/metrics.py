"""What a run is reduced to before it reaches the page."""
from __future__ import annotations

import math

import numpy as np

from .feeder import Run


def gini(x: np.ndarray) -> float:
    """Gini coefficient of non-negative values: 0 = everyone equal, 1 = one household has it all."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    i = np.arange(1, n + 1)
    return float((2 * (i * x).sum() / (n * x.sum())) - (n + 1) / n)


def top_share(x: np.ndarray, frac: float = 0.10) -> float:
    x = np.sort(np.asarray(x, float))[::-1]
    k = max(1, int(round(frac * len(x))))
    return float(x[:k].sum() / x.sum()) if x.sum() else 0.0


def sig(v: float, n: int = 3):
    """Round to n significant figures, for a small JSON."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if v == 0:
        return 0
    r = round(v, -int(math.floor(math.log10(abs(v)))) + (n - 1))
    return int(r) if r == int(r) and abs(r) >= 10 ** (n - 1) else r


def summarise(r: Run, fit: float) -> dict:
    pro = r.hh.prosumer
    rev = r.revenue[pro]
    days = r.hours // 24
    surplus = r.to_discom.sum() + r.p2p_sold.sum() + r.curtailed.sum()
    retail_mean = float(np.average(r.hh.retail, weights=np.maximum(r.from_discom, 1e-9)))
    vol = r.p2p_volume
    return {
        "gen": float(r.gen.sum()), "self": float(r.self_consumed.sum()), "surplus": float(surplus),
        "discom": float(r.to_discom.sum()), "p2p": float(r.p2p_sold.sum()),
        "curtailed": float(r.curtailed.sum()),
        "resold_local": float(r.resold_local.sum()),
        "discom_spread": float(r.resold_local.sum() * (retail_mean - fit)),
        "seller_gain": float(r.seller_gain.sum()), "buyer_gain": float(r.buyer_gain.sum()),
        "price": float(np.nansum(r.price * vol) / vol.sum()) if vol.sum() > 0 else None,
        "rev_mean": float(rev.mean()) if len(rev) else 0.0,
        "gini": gini(rev), "top10": top_share(rev),
        "q": np.quantile(rev, np.linspace(0, 1, 21)).tolist() if len(rev) else [],
        "strip": rev.tolist(), "kw": r.hh.pv_kw[pro].tolist(),
        "day": r.net_export.reshape(days, 24).mean(axis=0).tolist(),
        "peak_export": float(r.net_export.max()),
        "bill_mean": float(r.bill.mean()),
        "n_prosumers": int(pro.sum()), "n_active": int(r.hh.active.sum()),
    }
