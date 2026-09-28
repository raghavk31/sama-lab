# One feeder, two regimes

An agent-based model of rooftop solar prosumers on one electricity distribution feeder in an Indian
city. It runs the same week twice. In **regime A** (opaque), every exported unit goes to the DISCOM at a
fixed feed-in tariff. In **regime B** (visible), households can see the feeder and trade surplus with
their neighbours. The page at [`index.html`](index.html) reads the precomputed results.

**Status: a synthetic model, unvalidated.** Nothing in it is measured, and it has not been checked
against any real feeder. Read the sections on what is assumed, synthetic and unvalidated before quoting
a number from it.

## The question

What changes in surplus allocation and household revenue when a prosumer can see where its exported
electricity goes and choose a counterparty, compared with the current regime, where the DISCOM absorbs all
surplus at a fixed rate?

## What the model does

- **One feeder, 300 households** (200–500 in config), one representative April week at hourly
  resolution. `time.horizon: year` runs 8,760 hours.
- **Each household** has an archetype: daytime-absent working household, daytime-present household, or
  mixed use with a home business. It also has a monthly consumption and, with probability set by *PV
  penetration*, a rooftop system (lognormal, median 3 kW, clipped to 1–10 kW, sold in half-kW steps). It
  has an *active* flag, which decides whether it trades in regime B, and an *aggressiveness* between 0 and 1.
- **Every hour**, a household consumes its own generation first. What is left is surplus or deficit.
  If the feeder's net export exceeds the transformer's reverse-flow limit, inverters are curtailed pro rata.
- **Regime A:** surplus goes to the DISCOM at the feed-in tariff, and deficit is bought at retail. No household
  decides anything, and each sees only its own meter.
- **Regime B:** an active household sees the feeder's net position that hour. It moves a share of its
  load into hours the feeder is exporting. It offers its surplus, or bids for its deficit, in a per-hour
  **uniform-price double auction**, clearing between the feed-in tariff and a price ceiling. Unmatched surplus
  falls back to the DISCOM, and unmatched deficit to retail. Inactive households behave as in A.
- **Outputs** per setting: the split of surplus between DISCOM, peer to peer and curtailed; each
  prosumer's revenue, with the Gini coefficient, quantiles and the top decile's share; the hourly net
  export at the transformer; how the gap between the feed-in tariff and retail on traded units divides between sellers and buyers.

### A physical point the results turn on

Within one feeder, a peer-to-peer trade does not move any electricity. A rooftop's export is consumed by
its neighbours in both regimes. At the default setting, about three quarters of what the DISCOM buys
at the feed-in tariff is used on the same feeder within the hour. The market changes who is paid for
those units and at what price. The only physical difference between the regimes here comes from load
shifting, which needs the household to see the feeder.

## Run it

```sh
cd abm
python -m venv .venv && .venv/Scripts/activate      # or source .venv/bin/activate
pip install -e ".[test]"
python -m sama_abm.profiles     # (re)write the synthetic profiles
pytest                          # 18 tests: energy balance, clearing, determinism, CSV override
python -m sama_abm.sweep        # 125 settings x 5 seeds -> src/results.json (~130 KB, ~1 min)
```

Then, from the repo root, `npm install && npm run dev` serves the page.

One run from Python:

```python
from sama_abm import config, feeder
cfg = config.load()
b = feeder.run(config.override(cfg, **{"behaviour.active_share": 0.75}), "B", replicate=0)
b.revenue[b.hh.prosumer].mean()
```

## Code layout

| file | what it holds |
|---|---|
| `config/default.yaml` | every parameter. Nothing numeric is hardcoded in `sama_abm/`. |
| `sama_abm/profiles.py` | profile CSVs: measured over synthetic, shapes and series |
| `sama_abm/households.py` | the population, drawn with common random numbers |
| `sama_abm/clearing/` | market designs: `base.py` (the contract), `discom.py` (A), `uniform.py` (B) |
| `sama_abm/feeder.py` | one run: one regime, one replicate |
| `sama_abm/metrics.py` | Gini, shares, the per-run summary |
| `sama_abm/sweep.py` | the batch runner, which writes `src/results.json` |

**A new market design** is one file in `sama_abm/clearing/`. It is a class with a `name` and
`clear(ask_q, ask_p, bid_q, bid_p, fit, ceiling) -> ClearResult`, added to `REGISTRY`, and selected with
`market.clearing` in config. Pay-as-bid, a bilateral matcher or a DISCOM-run pool would each fit.

**Reproducibility.** One master seed (`seed`). Each replicate derives its own streams from
`SeedSequence([seed, replicate])`. Penetration and trader share select households by a fixed rank, so
the rooftops present at 20% are the ones present at 10% plus more, and a slider changes the parameter,
not the neighbourhood. The same config always writes the same `results.json`, apart from the date
stamp in `meta.generated`.

## Replacing a synthetic profile with a measured one

Profiles are looked up by name: `data/measured/<name>.csv` first, then `data/profiles/<name>.csv`.
To use a measured profile, **drop a CSV into `data/measured/` with the same name**. No code changes.

| profile | 24-row day shape | 168- or 8,760-row series |
|---|---|---|
| `load_daytime_absent`, `load_daytime_present`, `load_home_business` | `hour,weekday,weekend` | `hour,value` |
| `irradiance` | `hour,ghi_norm` | `hour,value` |

Profiles carry **shape**, not magnitude. Each day is normalised to sum to 1, and a series is normalised by
its mean day, so any unit works. Magnitudes come from config: `population.archetypes.*.monthly_kwh` for
load, and `generation.specific_yield` for PV. A measured irradiance *series* already carries season and
cloud, so the monthly multiplier and the cloud draw are skipped for it. A new archetype is a new entry in
`population.archetypes` and in `profiles.load`.

## What is assumed

Every item has a config key. Those marked **placeholder** are behavioural and wait on fieldwork.

| assumption | value | key |
|---|---|---|
| households on the feeder | 300 | `feeder.households` |
| transformer reverse-flow limit | 400 kVA × 0.60 = 240 kW | `feeder.dt_rating_kva`, `feeder.reverse_flow_limit` |
| PV size distribution | lognormal, median 3 kW, σ 0.55, clipped 1–10 kW | `population.pv_kw` |
| archetype mix | 45% daytime-absent, 40% daytime-present, 15% home business | `population.archetypes` |
| monthly consumption (median) | 240 / 300 / 420 kWh | `population.archetypes.*.monthly_kwh` |
| specific yield, clear day | 4.6 kWh per kWp per day | `generation.specific_yield` |
| month multipliers | generic Indian curve, April 1.10, July 0.70 | `generation.monthly` |
| daily cloud factor | Beta(9, 1.5), mean 0.86 | `generation.cloud` |
| **aggressiveness** (placeholder) | Beta(2, 2) | `behaviour.aggressiveness` |
| **load moved into export hours** (placeholder) | 10% of daily load × aggressiveness | `behaviour.flex_share` |
| **ask and bid rule** (placeholder) | see below | `sama_abm/feeder.py::_orders` |
| retail rate per household | uniform in ₹6.40–6.80 | `tariff.retail_low`, `tariff.retail_high` |

The order rule (placeholder). With `a` a household's aggressiveness and `s` the feeder's surplus
share that hour (surplus ÷ (surplus + deficit)):

- ask = FiT + (ceiling − FiT) × (1 − a) × (1 − s/2)
- bid = cap − (cap − FiT) × (1 − a) × (1/2 + s/2), where cap = min(own retail rate, ceiling)

So a timid household asks near the ceiling, bids near the feed-in tariff, and rarely trades. When the
feeder is flush with surplus, everyone prices lower. Nobody has asked a household how it would
actually price a unit. This rule stands in until someone does.

## What is synthetic

- **All load profiles.** Hand-drawn day shapes (`profiles.py::SYNTHETIC_LOAD`), not fitted to any
  dataset, with lognormal household-hour noise.
- **The irradiance curve.** A half-sine clear-sky shape between 06:00 and 18:30, scaled by a generic
  monthly curve and a random daily cloud factor. No measured irradiance for any city.
- **The PV size distribution and the archetype mix.** Plausible for urban Indian rooftops, but not taken
  from installation data.

## What is unvalidated

All of it. The tests check that the model is internally consistent: energy balances every
hour for every household, every kWh sold peer to peer is bought on the feeder, prices stay in the band,
regime B with nobody trading equals regime A, and seeded runs repeat exactly. None of that says the
model is *right*. It has not been calibrated against metered data from any feeder, and the behaviour
it assumes has not been observed. Treat it as a way of asking which questions matter, not as evidence.

## What is left out

Voltage and thermal limits below the transformer, line losses, phase imbalance, reactive power;
batteries; time-of-day retail tariffs; fixed charges; and every charge that sits between a seller and a
buyer in a real peer-to-peer framework: wheeling, banking, cross-subsidy surcharge, platform fee. Those
charges would narrow every gain the model shows. Establishing what survives them, under each state's
framework, is the next piece of work (see the Sama page, chapter 00).

## Tariffs and sources

**The ₹2.50 feed-in tariff is stylised.** It is the export rate used across the Sama project to state the
gap. It is **not** a figure from a specific regulator's order, and it is lower than the Karnataka figures
found so far:

- KERC, *Determination of Tariff and norms in respect of Solar Power Projects (including Solar Rooftop
  Photovoltaic Projects) for FY24*, order dated 01.06.2023. For grid-connected rooftop PV of 1–10 kW for
  domestic consumers: **₹4.50/unit without capital subsidy, ₹2.97/unit with capital subsidy**. This applies
  to PPAs entered into on or after 01.04.2023, for 25 years. For 1–2000 kW excluding domestic 1–10 kW: ₹3.74/unit.
  [PDF, hosted by BESCOM](https://srtpv.bescom.org/SRTPV/document/KERCSRTPVtariff2024.pdf), accessed 2026-09-29.
- A later FY25 figure of ₹3.79/unit (domestic 1–10 kW, without subsidy) and an LT export rate of
  ₹3.27/kWh appear in secondary sources. **[unverified]**: not yet read in a primary order.

Because the feed-in tariff is a config value (`tariff.fit`), the whole sweep can be rerun at ₹2.97 or ₹4.50
with one edit. A regime-B gain measured against ₹2.50 will overstate the gain against either.

**The ₹6.40–6.80 retail band** is also the project's stated range. **[unverified]** against a current
BESCOM, BSES or UPPCL domestic tariff schedule. Domestic retail tariffs in India are slabbed, and the
marginal rate a household avoids depends on its slab.

**Peer-to-peer trading** in Karnataka is governed by the KERC (Implementation of Peer to Peer Solar Energy
Transaction) Regulations, 2024, effective 06.08.2024 as reported by
[Mercom](https://www.mercomindia.com/karnataka-frames-regulations-for-peer-to-peer-solar-energy-transactions).
The [notification PDF](https://kerc.karnataka.gov.in/uploads/media_to_upload1724310950.pdf) is a scanned image and has not
been read clause by clause here. The model's rule that unsold surplus falls back to the licensee matches the
reported summary. Its price band and its lack of charges are the model's own simplifications, not the regulation's.
