"""Market designs, by name. A new design is one file with a class that has `name` and `clear()`
(see base.ClearingMechanism), added to REGISTRY; config `market.clearing` picks it."""
from .base import ClearingMechanism, ClearResult
from .discom import DiscomOnly
from .uniform import UniformPrice

REGISTRY: dict[str, type] = {c.name: c for c in (DiscomOnly, UniformPrice)}


def get(name: str) -> ClearingMechanism:
    try:
        return REGISTRY[name]()
    except KeyError:
        raise KeyError(f"no clearing mechanism '{name}'; have {sorted(REGISTRY)}") from None
