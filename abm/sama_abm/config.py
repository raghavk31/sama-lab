"""Load and check the YAML config. The model reads a plain nested dict; this module is the only
place that knows where the file lives and what must be in it."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parent.parent / "config" / "default.yaml"


def load(path: Path | str = DEFAULT) -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    validate(cfg)
    return cfg


def override(cfg: dict, **dotted) -> dict:
    """A copy of cfg with dotted keys replaced: override(cfg, **{"market.ceiling": 5.0})."""
    out = copy.deepcopy(cfg)
    for key, val in dotted.items():
        node = out
        *path, leaf = key.split(".")
        for p in path:
            node = node[p]
        if leaf not in node:
            raise KeyError(f"unknown config key {key}")
        node[leaf] = val
    validate(out)
    return out


def validate(cfg: dict) -> None:
    n = cfg["feeder"]["households"]
    if not 50 <= n <= 5000:
        raise ValueError(f"feeder.households={n} is outside a sensible range")
    t = cfg["tariff"]
    if not t["fit"] < t["retail_low"] <= t["retail_high"]:
        raise ValueError("tariff must satisfy fit < retail_low <= retail_high")
    if not t["fit"] <= cfg["market"]["ceiling"] <= t["retail_high"]:
        raise ValueError("market.ceiling must sit between the feed-in tariff and the retail rate")
    for k in ("pv_penetration",):
        if not 0 <= cfg["population"][k] <= 1:
            raise ValueError(f"population.{k} must be a share")
    if not 0 <= cfg["behaviour"]["active_share"] <= 1:
        raise ValueError("behaviour.active_share must be a share")
    if cfg["time"]["horizon"] not in ("week", "year"):
        raise ValueError("time.horizon is week or year")
    if len(cfg["generation"]["monthly"]) != 12:
        raise ValueError("generation.monthly needs 12 values")
    arch = cfg["population"]["archetypes"]
    if set(arch) != set(cfg["profiles"]["load"]):
        raise ValueError("every archetype needs a load profile, and vice versa")
