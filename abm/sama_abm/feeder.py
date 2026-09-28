"""One feeder, one horizon, one regime.

Every hour, for every household: generation and load are drawn from the profiles; the household
consumes its own generation first; what is left is surplus or deficit. If the feeder's net export
exceeds what the distribution transformer may carry backwards, inverters are curtailed pro rata.
Then the regime decides where the remaining surplus goes.

- Regime A, opaque: the household sees only its own meter. All surplus goes to the DISCOM at the
  feed-in tariff; every deficit is bought at retail. Nobody decides anything.
- Regime B, visible: an active household sees the feeder's net demand and the interval's price.
  It moves some flexible load into hours the feeder is exporting, and it offers surplus (or bids
  for deficit) in a per-interval market. Unmatched surplus falls back to the DISCOM, unmatched
  deficit to retail. Inactive households behave as in regime A.

Physical note that shapes the results: within one feeder, a peer-to-peer trade does not move an
electron. A rooftop's export is consumed by its neighbours in both regimes. What the market
changes is who is paid for it and at what price. The only physical difference between the regimes
here comes from load shifting, which needs the household to see the feeder.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import clearing, profiles
from .households import Households, draw, streams

REGIMES = ("A", "B")


@dataclass
class Run:
    regime: str
    hh: Households
    hours: int
    # per household, summed over the horizon (kWh or Rs)
    gen: np.ndarray
    load: np.ndarray
    self_consumed: np.ndarray
    to_discom: np.ndarray
    p2p_sold: np.ndarray
    p2p_bought: np.ndarray
    curtailed: np.ndarray
    from_discom: np.ndarray
    revenue: np.ndarray          # Rs: feed-in + P2P sales
    bill: np.ndarray             # Rs: retail imports + P2P purchases
    seller_gain: np.ndarray      # Rs above what the same kWh would have fetched at the feed-in tariff
    buyer_gain: np.ndarray       # Rs below what the same kWh would have cost at retail
    # per hour, summed over the feeder
    net_export: np.ndarray       # kWh at the transformer, export positive
    resold_local: np.ndarray     # kWh bought by the DISCOM at FiT and consumed on this feeder that hour
    price: np.ndarray            # clearing price, NaN where nothing cleared
    p2p_volume: np.ndarray
    hourly: dict = field(default_factory=dict)   # household × hour arrays, only when asked for


def _weather(cfg: dict, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Hourly irradiance factor (kWh per kWp) for the horizon, and the month of each day."""
    days, _ = profiles.horizon_days(cfg["time"])
    month = profiles.month_of_day(cfg["time"])
    g = cfg["generation"]
    cloud = rng.beta(g["cloud"]["a"], g["cloud"]["b"], size=days)   # always drawn: keeps streams aligned
    p = profiles.read(cfg["profiles"]["irradiance"])
    shape = profiles.expand(p, cfg["time"])
    if p.series is not None:          # a measured series already carries season and cloud
        return g["specific_yield"] * shape, month
    per_day = g["specific_yield"] * np.asarray(g["monthly"])[month] * cloud
    return shape * np.repeat(per_day, 24), month


def _load(cfg: dict, hh: Households, rng: np.random.Generator, hours: int) -> np.ndarray:
    shapes = np.stack([profiles.expand(profiles.read(cfg["profiles"]["load"][a]), cfg["time"])
                       for a in hh.archetypes])                     # archetype × hour, days sum to 1
    daily = hh.monthly_kwh * 12 / 365
    sig = cfg["population"]["hourly_noise"]
    noise = np.exp(sig * rng.standard_normal((hours, hh.n)) - sig ** 2 / 2)
    return shapes[hh.archetype].T * daily * noise                  # hour × household


def _shift(load: np.ndarray, gen: np.ndarray, hh: Households, share: float) -> np.ndarray:
    """Active households move `share × aggressiveness` of each day's load out of hours the feeder
    imports and into hours it exports, in proportion to the export they can now see."""
    H, n = load.shape
    days = H // 24
    L = load.reshape(days, 24, n).copy()
    E = (gen - load).sum(axis=1).reshape(days, 24)                  # what the feeder shows them
    X = np.maximum(E, 0)
    frac = share * hh.aggressiveness * hh.active                    # per household
    for d in range(days):
        if X[d].sum() <= 0:
            continue
        importing = E[d] <= 0
        movable = L[d][importing].sum(axis=0)                       # load sitting in import hours
        m = np.minimum(frac * L[d].sum(axis=0), movable)
        if not m.any():
            continue
        take = np.where(movable > 0, m / np.where(movable > 0, movable, 1), 0)
        L[d][importing] *= (1 - take)
        L[d] += np.outer(X[d] / X[d].sum(), m)
    return L.reshape(H, n)


def _orders(cfg: dict, hh: Households, surplus: np.ndarray, deficit: np.ndarray, s: float):
    """Asks and bids for one hour. `s` is the feeder's surplus share this hour, which active
    households can see: plentiful surplus pushes asks and bids down. PLACEHOLDER rule."""
    fit, ceil = cfg["tariff"]["fit"], cfg["market"]["ceiling"]
    a = hh.aggressiveness
    sellers = np.flatnonzero(hh.active & (surplus > 1e-9))
    buyers = np.flatnonzero(hh.active & (deficit > 1e-9))
    ask = fit + (ceil - fit) * (1 - a[sellers]) * (1 - s / 2)
    cap = np.minimum(hh.retail[buyers], ceil)
    bid = cap - (cap - fit) * (1 - a[buyers]) * (0.5 + s / 2)
    return sellers, ask, buyers, bid


def run(cfg: dict, regime: str, replicate: int = 0, keep_hourly: bool = False) -> Run:
    if regime not in REGIMES:
        raise ValueError(f"regime is one of {REGIMES}")
    rng = streams(cfg["seed"], replicate)
    hh = draw(cfg, rng["population"])
    irr, _ = _weather(cfg, rng["weather"])
    H = len(irr)
    gen = np.outer(irr, hh.pv_kw)                                    # hour × household, kWh
    load = _load(cfg, hh, rng["noise"], H)
    if regime == "B":
        load = _shift(load, gen, hh, cfg["behaviour"]["flex_share"])

    sc = np.minimum(gen, load)
    surplus, deficit = gen - sc, load - sc

    limit = cfg["feeder"]["dt_rating_kva"] * cfg["feeder"]["reverse_flow_limit"]
    tot_s = surplus.sum(axis=1)
    excess = np.maximum(tot_s - deficit.sum(axis=1) - limit, 0)
    cut = np.where(tot_s > 0, excess / np.where(tot_s > 0, tot_s, 1), 0)
    curtailed = surplus * cut[:, None]
    surplus = surplus - curtailed

    market = clearing.get(cfg["market"]["clearing"] if regime == "B" else "discom")
    fit = cfg["tariff"]["fit"]
    sold = np.zeros_like(surplus)
    bought = np.zeros_like(deficit)
    sell_p = np.zeros_like(surplus)
    buy_p = np.zeros_like(deficit)
    price = np.full(H, np.nan)
    for h in range(H):
        S, D = surplus[h].sum(), deficit[h].sum()
        if S <= 0 or D <= 0:
            continue
        si, ask, bi, bid = _orders(cfg, hh, surplus[h], deficit[h], S / (S + D))
        r = market.clear(surplus[h, si], ask, deficit[h, bi], bid, fit, cfg["market"]["ceiling"])
        if r.volume > 0:
            sold[h, si], sell_p[h, si] = r.sold, r.price
            bought[h, bi], buy_p[h, bi] = r.bought, r.paid
            price[h] = float(np.average(r.price, weights=r.sold))

    to_discom = surplus - sold
    from_discom = deficit - bought
    exp_h, imp_h = to_discom.sum(axis=1), from_discom.sum(axis=1)
    out = Run(
        regime=regime, hh=hh, hours=H,
        gen=gen.sum(0), load=load.sum(0), self_consumed=sc.sum(0), to_discom=to_discom.sum(0),
        p2p_sold=sold.sum(0), p2p_bought=bought.sum(0), curtailed=curtailed.sum(0),
        from_discom=from_discom.sum(0),
        revenue=(fit * to_discom + sell_p * sold).sum(0),
        bill=(hh.retail * from_discom + buy_p * bought).sum(0),
        seller_gain=((sell_p - fit) * sold).sum(0),
        buyer_gain=((hh.retail - buy_p) * bought).sum(0),
        net_export=(gen - curtailed - load).sum(axis=1),
        resold_local=np.minimum(exp_h, imp_h),
        price=price, p2p_volume=sold.sum(axis=1),
    )
    if keep_hourly:
        out.hourly = dict(gen=gen, load=load, self_consumed=sc, to_discom=to_discom, p2p_sold=sold,
                          p2p_bought=bought, curtailed=curtailed, from_discom=from_discom,
                          deficit=deficit)
    return out
