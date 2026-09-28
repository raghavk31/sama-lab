"""Consumption and irradiance profiles, read from CSV so a measured profile replaces a synthetic one
without touching model code.

A name like ``load_daytime_absent`` resolves to ``data/measured/<name>.csv`` if that file exists,
otherwise ``data/profiles/<name>.csv``. Two CSV forms are accepted:

- a day shape, 24 rows: ``hour,weekday,weekend`` (load) or ``hour,ghi_norm`` (irradiance);
- a series, 168 or 8760 rows: ``hour,value``, one row per hour of a week or a year.

Profiles carry *shape* only. Each day is normalised to sum to 1 and magnitudes come from the
config (a household's monthly kWh, a feeder's specific yield), so a measured profile in any unit
drops in. A series keeps its day-to-day variation: it is normalised by its mean day, not per day.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DAYS_BEFORE_MONTH = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


@dataclass
class Profile:
    name: str
    source: Path
    weekday: np.ndarray | None = None   # 24 values, day shape
    weekend: np.ndarray | None = None
    series: np.ndarray | None = None    # 168 or 8760 values

    @property
    def measured(self) -> bool:
        return self.source.parent.name == "measured"


def resolve(name: str, data_dir: Path | None = None) -> Path:
    data_dir = data_dir or DATA
    for sub in ("measured", "profiles"):
        p = data_dir / sub / f"{name}.csv"
        if p.exists():
            return p
    raise FileNotFoundError(f"profile '{name}' not found in {data_dir}/measured or {data_dir}/profiles")


def read(name: str, data_dir: Path | None = None) -> Profile:
    path = resolve(name, data_dir)
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    cols = set(rows[0]) if rows else set()
    if "value" in cols:
        s = np.array([float(r["value"]) for r in rows])
        if len(s) not in (168, 8760):
            raise ValueError(f"{path}: a series needs 168 or 8760 rows, got {len(s)}")
        return Profile(name, path, series=s)
    if len(rows) != 24:
        raise ValueError(f"{path}: a day shape needs 24 rows, got {len(rows)}")
    if "weekday" in cols:
        return Profile(name, path, weekday=np.array([float(r["weekday"]) for r in rows]),
                       weekend=np.array([float(r["weekend"]) for r in rows]))
    if "ghi_norm" in cols:
        g = np.array([float(r["ghi_norm"]) for r in rows])
        return Profile(name, path, weekday=g, weekend=g)
    raise ValueError(f"{path}: expected columns weekday,weekend or ghi_norm or value")


def _norm(day: np.ndarray) -> np.ndarray:
    s = day.sum()
    return day / s if s > 0 else day


def horizon_days(time_cfg: dict) -> tuple[int, int]:
    """(number of days, first day-of-year) for the configured horizon."""
    if time_cfg["horizon"] == "year":
        return 365, 0
    return 7, DAYS_BEFORE_MONTH[time_cfg["week_month"] - 1]


def expand(p: Profile, time_cfg: dict) -> np.ndarray:
    """Hourly shape across the horizon, each day summing to ~1 (a series: its mean day sums to 1)."""
    days, doy0 = horizon_days(time_cfg)
    if p.series is not None:
        s = p.series
        if len(s) == 168:
            s = np.tile(s, math.ceil(days / 7) + 1)[: days * 24] if days != 7 else s
        else:
            s = s[doy0 * 24: (doy0 + days) * 24]
        return s / (s.sum() / days)
    wd, we = _norm(p.weekday), _norm(p.weekend)
    dow0 = time_cfg.get("start_weekday", 0)
    return np.concatenate([we if (dow0 + d) % 7 >= 5 else wd for d in range(days)])


def month_of_day(time_cfg: dict) -> np.ndarray:
    """Month index 0–11 for each day of the horizon."""
    days, doy0 = horizon_days(time_cfg)
    doy = (doy0 + np.arange(days)) % 365
    return np.searchsorted(DAYS_BEFORE_MONTH, doy, side="right") - 1


# --- the synthetic set -------------------------------------------------------------------------
# Hand-drawn shapes, not fitted to any dataset. They exist so the model runs before fieldwork
# profiles arrive; `python -m sama_abm.profiles` rewrites them.

def _bumps(spec: list[tuple[float, float, float]], base: float) -> np.ndarray:
    h = np.arange(24) + 0.5
    return base + sum(a * np.exp(-0.5 * ((h - c) / w) ** 2) for c, w, a in spec)


SYNTHETIC_LOAD = {
    # out 9–18 on weekdays: a morning peak, an empty house, a long evening with cooling
    "load_daytime_absent": (
        _bumps([(7.0, 1.2, 1.0), (20.5, 2.2, 1.8), (13.0, 2.0, 0.05)], 0.25),
        _bumps([(8.5, 1.5, 0.9), (13.5, 2.5, 0.8), (20.5, 2.2, 1.6)], 0.30)),
    # someone home all day: cooking peaks, fans and cooling through the afternoon
    "load_daytime_present": (
        _bumps([(7.5, 1.3, 0.9), (13.0, 2.5, 0.9), (20.5, 2.0, 1.5)], 0.30),
        _bumps([(8.5, 1.5, 0.9), (13.5, 2.5, 1.0), (20.5, 2.0, 1.5)], 0.30)),
    # a shop, tailoring unit or clinic on the ground floor: a working day, then the household
    "load_home_business": (
        _bumps([(7.5, 1.2, 0.6), (14.0, 3.5, 1.4), (20.5, 1.8, 1.1)], 0.30),
        _bumps([(8.5, 1.5, 0.8), (13.5, 3.0, 0.8), (20.5, 2.0, 1.3)], 0.30)),
}


def synthetic_irradiance(sunrise: float = 6.0, sunset: float = 18.5) -> np.ndarray:
    """Clear-sky shape: a half-sine between sunrise and sunset, integrated over each hour."""
    fine = np.linspace(0, 24, 24 * 60, endpoint=False) + 0.5 / 60
    x = np.clip((fine - sunrise) / (sunset - sunrise), 0, 1)
    g = np.sin(np.pi * x) ** 1.3
    return g.reshape(24, 60).mean(axis=1) / g.reshape(24, 60).mean(axis=1).max()


def write_synthetic(data_dir: Path | None = None) -> None:
    out = (data_dir or DATA) / "profiles"
    out.mkdir(parents=True, exist_ok=True)
    for name, (wd, we) in SYNTHETIC_LOAD.items():
        with (out / f"{name}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["hour", "weekday", "weekend"])
            for h in range(24):
                w.writerow([h, f"{wd[h]:.4f}", f"{we[h]:.4f}"])
    g = synthetic_irradiance()
    with (out / "irradiance.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hour", "ghi_norm"])
        for h in range(24):
            w.writerow([h, f"{g[h]:.4f}"])


if __name__ == "__main__":
    write_synthetic()
    print(f"wrote synthetic profiles to {DATA / 'profiles'}")
