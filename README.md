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

The build uses relative paths, so `dist/` works at any path. To embed a page in another static
site:

```html
<iframe src="https://raghavk31.github.io/sama-lab/abm/" style="width:100%;border:0" id="sama-abm" title="One feeder, two regimes"></iframe>
<script>
  addEventListener("message", (e) => {
    if (e.data && e.data.type === "sama-lab:height") document.getElementById("sama-abm").style.height = e.data.height + "px";
  });
</script>
```

Inside a frame, a page trims its top padding and reports its height to the parent.
