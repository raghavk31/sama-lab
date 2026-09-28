// The embeddable build (dist/embed/sama-abm.js + sama-abm.css). Any element with data-sama-abm is
// rendered as the essay:
//
//   <link rel="stylesheet" href=".../sama-abm.css">
//   <div data-sama-abm data-results=".../results.json" data-sticky-under=".head"></div>
//   <script type="module" src=".../sama-abm.js"></script>
//
// data-results is required. data-sticky-under names the host's sticky header, if any, so the
// settings bar sticks below it. data-readme / data-sama override the two links at the end.
import "./abm.css";
import { mount, DEFAULT_LINKS } from "./app.js";

export { mount };

for (const el of document.querySelectorAll("[data-sama-abm]")) {
  const d = el.dataset;
  mount(el, {
    results: d.results,
    stickyUnder: d.stickyUnder,
    links: { readme: d.readme || DEFAULT_LINKS.readme, sama: d.sama || DEFAULT_LINKS.sama },
  }).catch((e) => console.error(e));
}
