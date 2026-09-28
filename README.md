# Sama lab

Working instruments behind [Sama](https://raghavkohli.xyz/work/sama/), a research project on what it
would take for a rooftop solar household in an Indian city to see, price and trade the electricity it
makes. Each instrument is labelled for what it is. None is evidence of a pilot, a user or a reading.

| | instrument | status |
|---|---|---|
| 01 | [**One feeder, two regimes**](abm/): an agent-based model of rooftop prosumers on one distribution feeder, comparing today's fixed feed-in tariff with visible peer-to-peer trading | built · synthetic data · unvalidated |
| 02 | [**Where the grid cannot see**](observability/): distribution-grid observability set against rooftop solar uptake | data survey in progress, nothing mapped |

## Layout

```
abm/              the model (Python, headless) and its page (static, reads abm/src/results.json)
observability/    survey/: what data exists, at what resolution, before anything is built
shared/           the stylesheet and iframe helper both pages use
```

Both pages are static files. There is no server and no Python in the browser. The ABM's sliders look
up a precomputed sweep.

## Build

```sh
npm install
npm run dev        # local
npm run build      # -> dist/, deployed to GitHub Pages by .github/workflows/pages.yml
```

The model and its sweep are documented in [abm/README.md](abm/README.md).

## Embedding

`npm run build` also writes the ABM essay as one script and one stylesheet with stable names, in
`dist/embed/` (published at `https://raghavk31.github.io/sama-lab/embed/`). A host page supplies its own
title and loads them:

```html
<link rel="stylesheet" href=".../embed/sama-abm.css">
<div data-sama-abm data-results=".../embed/results.json" data-sticky-under=".head"></div>
<script type="module" src=".../embed/sama-abm.js"></script>
```

The styles are scoped to `.sama-abm` and take the host's colour tokens (`--ink`, `--paper`, ...) where
it has them. `data-sticky-under` names the host's sticky header, so the settings bar docks below it.
This is how [raghavkohli.xyz/work/sama/feeder/](https://raghavkohli.xyz/work/sama/feeder/) is built: the
site copies these three files in with its `scripts/sync-sama-lab.py`.

The standalone pages also work inside an `<iframe>`. Framed, a page trims its top padding and posts its
height to the parent as `{type: "sama-lab:height", height}`.
