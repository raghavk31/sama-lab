"""The contract a market design meets. A clearing mechanism takes one interval's offers and bids
and says who sold what to whom at what price. Anything it leaves unmatched falls back to the
DISCOM: surplus at the feed-in tariff, deficit at each household's retail rate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass
class ClearResult:
    sold: np.ndarray      # kWh each seller sold peer to peer (same order as the asks passed in)
    bought: np.ndarray    # kWh each buyer bought peer to peer
    price: np.ndarray     # Rs/kWh each seller received (uniform designs: one value repeated)
    paid: np.ndarray      # Rs/kWh each buyer paid

    @property
    def volume(self) -> float:
        return float(self.sold.sum())


class ClearingMechanism(Protocol):
    name: str

    def clear(self, ask_q: np.ndarray, ask_p: np.ndarray, bid_q: np.ndarray, bid_p: np.ndarray,
              fit: float, ceiling: float) -> ClearResult: ...


def empty(n_ask: int, n_bid: int) -> ClearResult:
    return ClearResult(np.zeros(n_ask), np.zeros(n_bid), np.zeros(n_ask), np.zeros(n_bid))
