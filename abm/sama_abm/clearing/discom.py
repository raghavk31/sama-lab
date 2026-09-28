"""Regime A, and the null market: nothing clears peer to peer, all surplus goes to the DISCOM."""
from __future__ import annotations

import numpy as np

from .base import ClearResult, empty


class DiscomOnly:
    name = "discom"

    def clear(self, ask_q, ask_p, bid_q, bid_p, fit, ceiling) -> ClearResult:
        return empty(len(ask_q), len(bid_q))
