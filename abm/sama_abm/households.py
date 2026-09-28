"""The household agents on one feeder, held as columns rather than objects.

Common random numbers: every draw depends on (seed, replicate) and nothing else. PV penetration
and active share select households by a fixed random rank, so the rooftops present at 20%
penetration are the ones present at 10% plus more, and the same holds for traders. Moving a slider
changes the parameter, not the neighbourhood.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def streams(seed: int, replicate: int) -> dict[str, np.random.Generator]:
    names = ("population", "weather", "noise")
    kids = np.random.SeedSequence([seed, replicate]).spawn(len(names))
    return {n: np.random.default_rng(k) for n, k in zip(names, kids)}


@dataclass
class Households:
    archetype: np.ndarray       # index into `archetypes`
    archetypes: list[str]
    monthly_kwh: np.ndarray
    pv_kw: np.ndarray           # 0 where the household has no rooftop PV
    active: np.ndarray          # bool: trades in regime B, sees the feeder
    aggressiveness: np.ndarray  # 0..1, PLACEHOLDER behaviour
    retail: np.ndarray          # Rs/kWh the household pays for imports

    @property
    def n(self) -> int:
        return len(self.archetype)

    @property
    def prosumer(self) -> np.ndarray:
        return self.pv_kw > 0


def _first_k(u: np.ndarray, share: float) -> np.ndarray:
    k = int(round(share * len(u)))
    mask = np.zeros(len(u), bool)
    mask[np.argsort(u, kind="stable")[:k]] = True
    return mask


def draw(cfg: dict, rng: np.random.Generator) -> Households:
    n = cfg["feeder"]["households"]
    pop, beh, tar = cfg["population"], cfg["behaviour"], cfg["tariff"]
    names = list(pop["archetypes"])
    w = np.array([pop["archetypes"][a]["weight"] for a in names], float)
    # Fixed draw order: adding a parameter at the end keeps earlier draws unchanged.
    arche = rng.choice(len(names), size=n, p=w / w.sum())
    z_kwh = rng.standard_normal(n)
    u_pv = rng.random(n)
    z_pv = rng.standard_normal(n)
    u_active = rng.random(n)
    aggr = rng.beta(beh["aggressiveness"]["a"], beh["aggressiveness"]["b"], size=n)
    u_retail = rng.random(n)

    med = np.array([pop["archetypes"][a]["monthly_kwh"] for a in names])[arche]
    sig = np.array([pop["archetypes"][a]["sigma"] for a in names])[arche]
    monthly = med * np.exp(sig * z_kwh)

    pk = pop["pv_kw"]
    kw = np.clip(pk["median"] * np.exp(pk["sigma"] * z_pv), pk["min"], pk["max"])
    kw = np.round(kw * 2) / 2                     # systems are sold in half-kW steps
    kw = np.where(_first_k(u_pv, pop["pv_penetration"]), kw, 0.0)

    return Households(
        archetype=arche, archetypes=names, monthly_kwh=monthly, pv_kw=kw,
        active=_first_k(u_active, beh["active_share"]), aggressiveness=aggr,
        retail=tar["retail_low"] + u_retail * (tar["retail_high"] - tar["retail_low"]),
    )
