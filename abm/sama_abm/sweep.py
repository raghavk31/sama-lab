"""The batch runner: every cell of the sweep grid, both regimes, several seeds, into one JSON file
the page reads. Sliders on the page are lookups into this file; nothing is computed in the browser.

    python -m sama_abm.sweep [--config path] [--out path]

Regime A depends only on PV penetration, so it is run once per penetration level. Scalars are the
mean over replicates, with [min, max] where the spread is worth showing; distributions (quantiles,
the per-household strip) come from replicate 0, where every cell shares the same households.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from datetime import date
from pathlib import Path

import numpy as np

from . import config as cfgmod
from . import feeder
from .metrics import sig, summarise

ROOT = Path(__file__).resolve().parent.parent
SCALARS = ("gen", "self", "surplus", "discom", "p2p", "curtailed", "resold_local", "discom_spread",
           "seller_gain", "buyer_gain", "price", "rev_mean", "gini", "top10", "peak_export",
           "bill_mean")
RANGED = ("p2p", "gini", "rev_mean", "top10", "price")
MAX_BYTES = 2_000_000


def _cell(cfg: dict, regime: str, reps: int, keep_kw: bool) -> dict:
    fit = cfg["tariff"]["fit"]
    runs = [summarise(feeder.run(cfg, regime, k), fit) for k in range(reps)]
    out = {}
    for k in SCALARS:
        vals = [r[k] for r in runs if r[k] is not None]
        out[k] = sig(float(np.mean(vals))) if vals else None
        if k in RANGED and vals:
            out[k + "_rng"] = [sig(min(vals)), sig(max(vals))]
    out["day"] = [round(v, 1) for v in np.mean([r["day"] for r in runs], axis=0)]
    out["q"] = [round(v) for v in runs[0]["q"]]
    out["strip"] = [round(v) for v in runs[0]["strip"]]
    if keep_kw:
        out["kw"] = runs[0]["kw"]
    out["n_prosumers"], out["n_active"] = runs[0]["n_prosumers"], runs[0]["n_active"]
    return out


def sweep(cfg: dict, log=print) -> dict:
    g = cfg["sweep"]
    reps = g["replicates"]
    A, B = [], []
    t0 = time.time()
    for i, pen in enumerate(g["pv_penetration"]):
        base = cfgmod.override(cfg, **{"population.pv_penetration": pen, "behaviour.active_share": 0.0})
        A.append(_cell(base, "A", reps, keep_kw=True))
        plane = []
        for ceil in g["ceiling"]:
            row = []
            for act in g["active_share"]:
                c = cfgmod.override(cfg, **{"population.pv_penetration": pen, "market.ceiling": ceil,
                                            "behaviour.active_share": act})
                row.append(_cell(c, "B", reps, keep_kw=False))
            plane.append(row)
        B.append(plane)
        log(f"  penetration {pen:.0%} done, {time.time() - t0:.0f}s")
    f = cfg["feeder"]
    return {
        "meta": {
            "title": "Sama feeder ABM: sweep results",
            "generated": date.today().isoformat(),
            "seed": cfg["seed"], "replicates": reps,
            "households": f["households"], "horizon": cfg["time"]["horizon"],
            "week_month": cfg["time"]["week_month"],
            "limit_kw": f["dt_rating_kva"] * f["reverse_flow_limit"],
            "tariff": cfg["tariff"], "clearing": cfg["market"]["clearing"],
            "flex_share": cfg["behaviour"]["flex_share"],
            "grid": {k: g[k] for k in ("pv_penetration", "ceiling", "active_share")},
            "default": g["default"],
            "index": "A[pen]; B[pen][ceiling][active]. kWh and Rs are feeder totals over the "
                     "horizon unless named _mean. strip/q: prosumer revenue (Rs), replicate 0; "
                     "A[pen].kw gives each strip entry's PV kW, same order in A and B.",
            "synthetic": True,
        },
        "A": A, "B": B,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(cfgmod.DEFAULT))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cfg = cfgmod.load(a.config)
    out = Path(a.out) if a.out else ROOT / cfg["sweep"]["out"]
    n = len(cfg["sweep"]["pv_penetration"]) * len(cfg["sweep"]["ceiling"]) * len(cfg["sweep"]["active_share"])
    print(f"sweep: {n} cells x {cfg['sweep']['replicates']} replicates")
    t = time.time()
    res = sweep(cfg)
    text = json.dumps(res, separators=(",", ":"), ensure_ascii=False)
    size = len(text.encode())
    if size > MAX_BYTES:
        raise SystemExit(f"results are {size / 1e6:.2f} MB, over the 2 MB budget: coarsen the grid")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({size / 1e3:.0f} KB) in {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
