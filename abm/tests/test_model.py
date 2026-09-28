import hashlib
import json
import shutil

import numpy as np
import pytest

from sama_abm import clearing, config, feeder, profiles
from sama_abm.metrics import gini

CFG = config.load()


def over(**kw):
    return config.override(CFG, **kw)


@pytest.mark.parametrize("regime", ["A", "B"])
@pytest.mark.parametrize("pen", [0.1, 0.6])
def test_energy_balance_every_hour(regime, pen):
    r = feeder.run(over(**{"population.pv_penetration": pen}), regime, keep_hourly=True)
    h = r.hourly
    parts = h["self_consumed"] + h["to_discom"] + h["p2p_sold"] + h["curtailed"]
    np.testing.assert_allclose(parts, h["gen"], atol=1e-9)
    np.testing.assert_allclose(h["self_consumed"] + h["p2p_bought"] + h["from_discom"], h["load"], atol=1e-9)
    # every kWh sold peer to peer is bought by someone on the feeder, hour by hour
    np.testing.assert_allclose(h["p2p_sold"].sum(1), h["p2p_bought"].sum(1), atol=1e-9)


def test_no_active_traders_is_regime_a():
    c = over(**{"behaviour.active_share": 0.0})
    a, b = feeder.run(c, "A"), feeder.run(c, "B")
    for k in ("to_discom", "p2p_sold", "curtailed", "revenue", "bill"):
        np.testing.assert_allclose(getattr(a, k), getattr(b, k))


def test_prices_stay_in_band():
    c = over(**{"behaviour.active_share": 1.0, "market.ceiling": 5.0})
    r = feeder.run(c, "B")
    p = r.price[~np.isnan(r.price)]
    assert len(p) and p.min() >= CFG["tariff"]["fit"] and p.max() <= 5.0


def test_seeded_runs_are_identical():
    def digest():
        r = feeder.run(CFG, "B", replicate=3)
        return hashlib.sha256(np.concatenate([r.revenue, r.net_export]).tobytes()).hexdigest()
    assert digest() == digest()


def test_replicates_differ():
    assert not np.allclose(feeder.run(CFG, "A", 0).revenue, feeder.run(CFG, "A", 1).revenue)


def test_penetration_is_nested():
    lo = feeder.run(over(**{"population.pv_penetration": 0.1}), "A").hh.prosumer
    hi = feeder.run(over(**{"population.pv_penetration": 0.3}), "A").hh.prosumer
    assert (hi[lo]).all() and hi.sum() > lo.sum()


# --- clearing -----------------------------------------------------------------------------

U = clearing.get("uniform")


def test_no_crossing_clears_nothing():
    r = U.clear(np.array([1.0]), np.array([6.0]), np.array([1.0]), np.array([3.0]), 2.5, 6.4)
    assert r.volume == 0


def test_everything_crosses():
    r = U.clear(np.array([1.0, 2.0]), np.array([3.0, 3.2]), np.array([3.0]), np.array([6.0]), 2.5, 6.4)
    assert r.volume == pytest.approx(3.0)
    assert r.price[0] == pytest.approx((3.2 + 6.0) / 2)


def test_short_side_limits_volume():
    r = U.clear(np.array([5.0]), np.array([3.0]), np.array([1.0, 1.0]), np.array([6.0, 5.0]), 2.5, 6.4)
    assert r.volume == pytest.approx(2.0)
    np.testing.assert_allclose(r.bought, [1.0, 1.0])


def test_tie_at_margin_is_pro_rata():
    r = U.clear(np.array([2.0, 6.0]), np.array([3.0, 3.0]), np.array([4.0]), np.array([6.0]), 2.5, 6.4)
    np.testing.assert_allclose(r.sold, [1.0, 3.0])


def test_price_clipped_to_ceiling():
    r = U.clear(np.array([1.0]), np.array([6.3]), np.array([1.0]), np.array([6.8]), 2.5, 6.4)
    assert r.price[0] == pytest.approx(6.4)


def test_registry_rejects_unknown():
    with pytest.raises(KeyError):
        clearing.get("nope")


# --- profiles -----------------------------------------------------------------------------

def test_measured_csv_overrides_synthetic(tmp_path, monkeypatch):
    data = tmp_path / "data"
    shutil.copytree(profiles.DATA / "profiles", data / "profiles")
    (data / "measured").mkdir()
    base = feeder.run(CFG, "A")
    monkeypatch.setattr(profiles, "DATA", data)
    # a flat measured shape for one archetype, in arbitrary units
    rows = "hour,weekday,weekend\n" + "".join(f"{h},7,7\n" for h in range(24))
    (data / "measured" / "load_daytime_absent.csv").write_text(rows)
    assert profiles.read("load_daytime_absent").measured
    r = feeder.run(CFG, "A")
    assert r.load.sum() == pytest.approx(base.load.sum(), rel=0.02)   # magnitudes come from config
    assert not np.allclose(r.net_export, base.net_export)            # the shape came from the CSV


def test_series_profile_accepted(tmp_path):
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "x.csv").write_text("hour,value\n" + "".join(f"{h},{h % 24}\n" for h in range(168)))
    p = profiles.read("x", tmp_path)
    s = profiles.expand(p, CFG["time"])
    assert len(s) == 168 and s.sum() == pytest.approx(7)


def test_gini():
    assert gini(np.ones(10)) == pytest.approx(0)
    assert gini(np.r_[np.zeros(99), 1.0]) == pytest.approx(0.99)
