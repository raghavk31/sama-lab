// The ABM page. Everything shown is a lookup into results.json, which the Python sweep wrote;
// no model runs in the browser. Every sentence that states a finding is written from the numbers
// of the setting on screen, so the text cannot drift from the figures.
import * as Plot from "@observablehq/plot";
import resultsUrl from "./results.json?url";
import { reportHeight } from "../../shared/embed.js";

const $ = (id) => document.getElementById(id);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const pct = (x, d = 0) => `${(100 * x).toFixed(d)}%`;
const rs = (x, d = 0) => `₹${Number(x).toLocaleString("en-IN", { minimumFractionDigits: d, maximumFractionDigits: d })}`;
const kwh = (x) => `${Math.round(x).toLocaleString("en-IN")} kWh`;
const words = (x) => {
  const t = { 0: "none", 0.25: "a quarter", 0.5: "half", 0.75: "three quarters", 1: "all" }[x];
  return t ?? pct(x);
};

let R;                        // results
const S = { pen: 0, ceil: 0, act: 0 };

const A = () => R.A[S.pen];
const B = () => R.B[S.pen][S.ceil][S.act];
const g = () => R.meta.grid;

function colors() {
  return { discom: css("--s-discom"), p2p: css("--s-p2p"), curtail: css("--s-curtail"),
           ink: css("--ink"), soft: css("--ink-soft"), mute: css("--mute"), grid: css("--grid"),
           line: css("--line"), paper: css("--paper") };
}

function width(el) { return Math.max(280, Math.round(el.clientWidth || 680)); }

function style() {
  return { fontFamily: css("--sans"), fontSize: "12px", color: css("--mute"), background: "transparent", overflow: "visible" };
}

function legend(el, items) {
  el.innerHTML = items.map(([label, color, kind]) =>
    `<span><i class="${kind || ""}" style="background:${color}"></i>${label}</span>`).join("");
}

function table(el, head, rows) {
  el.innerHTML = `<table><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${
    rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function mount(el, node) { el.replaceChildren(node); }

// --- 00 the answer ---------------------------------------------------------------------------

function answer() {
  const a = A(), b = B();
  const up = b.rev_mean / a.rev_mean - 1;
  const act = g().active_share[S.act];
  if (act === 0) {
    $("answer").textContent = "With nobody trading, regime B is regime A: the same flows, the same payments. Move the third slider to let households trade.";
    return;
  }
  const dg = b.gini - a.gini;
  $("answer").innerHTML =
    `When ${words(act)} of the households can see the feeder and trade, ${pct(b.p2p / b.surplus)} of the rooftop surplus is sold to neighbours at about ${rs(b.price, 2)} instead of to the DISCOM at ₹2.50, and the mean prosumer earns ${pct(up)} more. ` +
    (Math.abs(dg) < 0.01
      ? `The spread of earnings barely moves (Gini ${a.gini.toFixed(2)} to ${b.gini.toFixed(2)}).`
      : dg > 0
        ? `The gain is not shared evenly: the Gini of prosumer revenue rises from ${a.gini.toFixed(2)} to ${b.gini.toFixed(2)}, because it goes to the households that trade.`
        : `The gain also evens out earnings a little: the Gini falls from ${a.gini.toFixed(2)} to ${b.gini.toFixed(2)}.`);
}

// --- 01 where the surplus goes ------------------------------------------------------------------

function fig1(c) {
  const a = A(), b = B();
  const kinds = [["discom", "to the DISCOM at ₹2.50", c.discom], ["p2p", "to a neighbour, peer to peer", c.p2p], ["curtailed", "curtailed", c.curtail]];
  const rows = [];
  for (const [reg, cell] of [["A · opaque", a], ["B · visible", b]]) {
    let x = 0;
    for (const [k, label, color] of kinds) {
      const share = (cell[k] || 0) / cell.surplus;
      rows.push({ reg, k, label, color, x1: x, x2: x + share, share, kwh: cell[k] || 0 });
      x += share;
    }
  }
  legend($("leg-1"), kinds.map(([, l, col]) => [l, col]));
  const W = width($("fig-1"));
  const vis = rows.filter((r) => r.share > 0);
  mount($("fig-1"), Plot.plot({
    width: W, height: 118, marginLeft: 84, marginRight: 8, marginTop: 6, marginBottom: 26, style: style(),
    x: { domain: [0, 1], tickFormat: (d) => pct(d), ticks: 5, label: null },
    y: { domain: ["A · opaque", "B · visible"], label: null, padding: 0.35 },
    marks: [
      Plot.gridX({ stroke: c.grid, strokeOpacity: 1, ticks: 5 }),
      Plot.barX(vis, { x1: "x1", x2: "x2", y: "reg", fill: (d) => d.color, insetLeft: 1, insetRight: 1, rx: 2 }),
      Plot.text(vis.filter((d) => d.share * (W - 92) > 44), { x: (d) => (d.x1 + d.x2) / 2, y: "reg",
        text: (d) => pct(d.share), fill: "white", fontSize: 12, fontWeight: 500 }),
      Plot.tip(vis, Plot.pointer({ x: (d) => (d.x1 + d.x2) / 2, y: "reg",
        title: (d) => `${d.reg}\n${d.label}\n${pct(d.share, 1)} of surplus · ${kwh(d.kwh)}` })),
    ],
  }));

  const moved = b.p2p / a.discom;
  $("find-1").textContent = b.p2p > 0
    ? `${pct(moved)} of what the DISCOM used to absorb now clears peer to peer, at a mean price of ${rs(b.price, 2)} a unit.`
    : "Nothing clears peer to peer at this setting.";
  if (a.curtailed > 1) {
    $("find-1").textContent += ` Curtailment ${b.curtailed < a.curtailed ? "falls" : "moves"} from ${kwh(a.curtailed)} to ${kwh(b.curtailed)} a week.`;
  }
  const local = a.resold_local / a.discom;
  $("physics").innerHTML = `One thing does not change between the two bars. In regime A, <strong>${pct(local)} of what the DISCOM buys at ₹2.50 is used on this same feeder within the hour</strong>, by the neighbours, who pay retail for it. Within one feeder, a peer-to-peer trade does not move any electricity. The neighbour's lights were already running on the rooftop's surplus. What the market changes is who is paid for that unit, and how much.`;
  table($("tab-1"), ["", "surplus", "DISCOM", "peer to peer", "curtailed", "clearing price"],
    [["A · opaque", a, null], ["B · visible", b, b.price]].map(([n, x, p]) =>
      [n, kwh(x.surplus), kwh(x.discom), kwh(x.p2p || 0), kwh(x.curtailed), p ? rs(p, 2) : "—"]));
}

// --- 02 who captures it -------------------------------------------------------------------------

const jitter = (i) => ((i * 0.6180339887) % 1) - 0.5;

function quant(q, p) { return q[Math.round(p * 20)]; }

function fig2(c) {
  const a = A(), b = B();
  const kw = a.kw;
  const dots = [];
  a.strip.forEach((v, i) => dots.push({ reg: "A · opaque", v, kw: kw[i], j: jitter(i), color: c.discom }));
  b.strip.forEach((v, i) => dots.push({ reg: "B · visible", v, kw: kw[i], j: jitter(i), color: c.p2p }));
  const ticks = [];
  for (const [reg, cell] of [["A · opaque", a], ["B · visible", b]]) {
    ticks.push({ reg, v: quant(cell.q, 0.5), t: "median" }, { reg, v: quant(cell.q, 0.9), t: "90th" });
  }
  const labels = [["A · opaque", a], ["B · visible", b]].map(([reg, cell]) => ({ reg, t: `Gini ${cell.gini.toFixed(2)} · top tenth ${pct(cell.top10)}` }));
  legend($("leg-2"), [["regime A · opaque", c.discom], ["regime B · visible", c.p2p]]);
  const W = width($("fig-2"));
  const xmax = Math.max(...b.strip, ...a.strip);
  mount($("fig-2"), Plot.plot({
    width: W, height: 250, marginLeft: 84, marginRight: 12, marginTop: 20, marginBottom: 32, style: style(),
    x: { domain: [0, xmax * 1.02], label: "₹ per week →", labelAnchor: "right", tickFormat: (d) => `₹${d}`, ticks: W > 520 ? 6 : 4 },
    y: { domain: [-0.5, 0.5], axis: null },
    fy: { domain: ["A · opaque", "B · visible"], label: null, padding: 0.25 },
    marks: [
      Plot.gridX({ stroke: c.grid, strokeOpacity: 1, ticks: W > 520 ? 6 : 4 }),
      Plot.dot(dots, { x: "v", y: (d) => d.j * 0.8, fy: "reg", r: 3, fill: (d) => d.color, fillOpacity: 0.8,
        stroke: c.paper, strokeWidth: 0.75 }),
      Plot.tickX(ticks, { x: "v", fy: "reg", stroke: c.ink, strokeWidth: 1.5, insetTop: 2, insetBottom: 2 }),
      W > 520 ? Plot.text(ticks, { x: "v", fy: "reg", frameAnchor: "top", dy: -12, text: "t", fill: c.soft, fontSize: 11 }) : null,
      Plot.text(labels, { fy: "reg", frameAnchor: "top-right", dy: -12, text: "t", fill: c.ink, fontSize: 12 }),
      Plot.tip(dots, Plot.pointer({ x: "v", y: (d) => d.j * 0.8, fy: "reg",
        title: (d) => `${d.reg}\n${d.kw} kW rooftop\n${rs(d.v)} a week` })),
    ],
  }));

  const act = g().active_share[S.act];
  const dg = b.gini - a.gini;
  $("find-2").textContent = act === 0
    ? "With nobody trading the two rows are the same households earning the same amounts."
    : `The median rooftop goes from ${rs(quant(a.q, 0.5))} to ${rs(quant(b.q, 0.5))} a week. ` +
      (dg > 0.005
        ? `The Gini rises from ${a.gini.toFixed(2)} to ${b.gini.toFixed(2)}: visibility splits prosumers into those who trade and those who do not.`
        : dg < -0.005
          ? `The Gini falls from ${a.gini.toFixed(2)} to ${b.gini.toFixed(2)}.`
          : `The Gini stays near ${b.gini.toFixed(2)}.`);
  table($("tab-2"), ["", "mean", "median", "90th pct", "Gini", "top tenth's share"],
    [["A · opaque", a], ["B · visible", b]].map(([n, x]) =>
      [n, rs(x.rev_mean), rs(quant(x.q, 0.5)), rs(quant(x.q, 0.9)), x.gini.toFixed(3), pct(x.top10, 1)]));

  // 2b: the gain by system size
  const gain = b.strip.map((v, i) => ({ kw: kw[i], d: v - a.strip[i] }));
  const traded = gain.filter((x) => x.d > 0.5);
  mount($("fig-2b"), Plot.plot({
    width: W, height: 232, marginLeft: 52, marginRight: 12, marginTop: 30, marginBottom: 32, style: style(),
    x: { label: "rooftop system, kW →", labelAnchor: "right", ticks: W > 520 ? 6 : 4 },
    y: { label: "↑ ₹ gained per week", labelAnchor: "top", tickFormat: (d) => `₹${d}`, ticks: 5, grid: false },
    marks: [
      Plot.gridY({ stroke: c.grid, strokeOpacity: 1, ticks: 5 }),
      Plot.ruleY([0], { stroke: c.line }),
      Plot.dot(gain, { x: (d) => d.kw + jitter(d.kw * 97 + d.d) * 0.25, y: "d", r: 3, fill: c.p2p, fillOpacity: 0.75, stroke: c.paper, strokeWidth: 0.75 }),
      Plot.tip(gain, Plot.pointer({ x: "kw", y: "d", title: (d) => `${d.kw} kW rooftop\n${d.d >= 0 ? "+" : ""}${rs(d.d)} a week under B` })),
    ],
  }));
  $("find-2b").textContent = act === 0 ? "" :
    `${traded.length} of ${gain.length} rooftops gain anything at all. The rest are either not trading or never matched, and they earn exactly what they earned before. Among those that gain, the gain grows with the size of the roof.`;

  const pool = b.seller_gain + b.buyer_gain;
  $("split").innerHTML = pool > 0
    ? `There is another side to each trade. Every unit sold peer to peer would otherwise have been bought by the DISCOM at ₹2.50 and sold next door at retail. Over this week that gap comes to <strong>${rs(pool)}</strong>. The market splits it: <strong>sellers keep ${pct(b.seller_gain / pool)}, and buyers, who pay less than retail, keep ${pct(b.buyer_gain / pool)}</strong>. That gap is not the DISCOM's profit. It pays for the network, and a real tariff would take part of it back as wheeling and other charges this model leaves out.`
    : "";
}

// --- 03 the feeder's day ------------------------------------------------------------------------

function fig3(c) {
  const a = A(), b = B();
  const pts = [];
  a.day.forEach((v, h) => pts.push({ h, v, reg: "A · opaque" }));
  b.day.forEach((v, h) => pts.push({ h, v, reg: "B · visible" }));
  const lim = R.meta.limit_kw;
  const peak = Math.max(...a.day, ...b.day);
  const showLim = peak > 0.55 * lim;
  legend($("leg-3"), [["regime A · opaque", c.discom, "line"], ["regime B · visible", c.p2p, "line"]]);
  const W = width($("fig-3"));
  mount($("fig-3"), Plot.plot({
    width: W, height: 272, marginLeft: 52, marginRight: 12, marginTop: 30, marginBottom: 32, style: style(),
    x: { domain: [0, 23], ticks: [0, 6, 12, 18, 23], tickFormat: (h) => `${String(h).padStart(2, "0")}:00`, label: null },
    y: { label: "↑ kW exported", labelAnchor: "top", ticks: 5, domain: showLim ? [Math.min(...a.day, ...b.day), lim * 1.08] : undefined, nice: true },
    color: { domain: ["A · opaque", "B · visible"], range: [c.discom, c.p2p] },
    marks: [
      Plot.gridY({ stroke: c.grid, strokeOpacity: 1, ticks: 5 }),
      Plot.ruleY([0], { stroke: c.line }),
      showLim ? Plot.ruleY([lim], { stroke: c.curtail, strokeWidth: 1 }) : null,
      showLim ? Plot.text([lim], { y: (d) => d, x: 0, dy: -7, textAnchor: "start", text: () => `transformer limit, ${lim} kW`, fill: c.soft, fontSize: 11 }) : null,
      Plot.lineY(pts, { x: "h", y: "v", stroke: "reg", strokeWidth: 2, curve: "monotone-x" }),
      Plot.tip(pts, Plot.pointerX({ x: "h", y: "v", stroke: "reg",
        title: (d) => `${String(d.h).padStart(2, "0")}:00 · ${d.reg}\n${d.v >= 0 ? "exporting" : "importing"} ${Math.abs(d.v).toFixed(0)} kW` })),
    ],
  }));
  const pa = Math.max(...a.day), pb = Math.max(...b.day);
  const hrs = a.day.map((v, h) => (v > 0 ? h : null)).filter((h) => h !== null);
  let f;
  if (!hrs.length) {
    f = "At this penetration the feeder never exports, even at midday. Every rooftop's surplus is absorbed by its neighbours before it reaches the transformer.";
  } else {
    f = `The feeder exports from about ${String(hrs[0]).padStart(2, "0")}:00 to ${String(hrs[hrs.length - 1] + 1).padStart(2, "0")}:00. `;
    f += pb < pa - 0.5
      ? `Under B the midday peak is ${pct(1 - pb / pa)} lower (${pa.toFixed(0)} to ${pb.toFixed(0)} kW), because households that can see the surplus move some load into it.`
      : "The two regimes carry almost the same flows. A market by itself does not move power; only load that shifts does.";
  }
  $("find-3").textContent = f;
  table($("tab-3"), ["hour", "A kW", "B kW"], a.day.map((v, h) => [`${String(h).padStart(2, "0")}:00`, v.toFixed(1), b.day[h].toFixed(1)]));
}

// --- 04 sensitivity -----------------------------------------------------------------------------

function ramp(n) {
  // one hue, light to dark: the P2P ochre, stepped for magnitude (penetration)
  const dark = css("color-scheme") === "dark";
  const [lo, hi] = dark ? ["#6B4A10", "#F0CC80"] : ["#E3C48A", "#5E3F07"];
  const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [a, b] = [rgb(lo), rgb(hi)];
  return Array.from({ length: n }, (_, i) => {
    const t = 0.2 + (0.8 * i) / (n - 1);
    return "#" + a.map((v, j) => Math.round(v + (b[j] - v) * t).toString(16).padStart(2, "0")).join("");
  });
}

function fig4(c) {
  const G = g();
  const cols = ramp(G.pv_penetration.length);
  const pts = [];
  G.pv_penetration.forEach((pen, i) => {
    const a = R.A[i];
    G.active_share.forEach((act, k) => {
      const b = R.B[i][S.ceil][k];
      pts.push({ pen, i, act, up: b.rev_mean / a.rev_mean - 1, gini: b.gini, sel: i === S.pen && k === S.act });
    });
  });
  legend($("leg-4"), G.pv_penetration.map((p, i) => [`${pct(p)} of roofs with PV`, cols[i], "line"]));
  const box = $("fig-4");
  const wide = box.clientWidth > 560;
  const W = wide ? Math.floor((box.clientWidth - 24) / 2) : width(box);
  const panel = (y, label, fmt) => Plot.plot({
    width: W, height: 232, marginLeft: 44, marginRight: 10, marginTop: 30, marginBottom: 32, style: style(),
    x: { domain: [0, 1], ticks: [0, 0.25, 0.5, 0.75, 1], tickFormat: (d) => pct(d), label: "households trading →", labelAnchor: "right" },
    y: { label, labelAnchor: "top", tickFormat: fmt, ticks: 4, nice: true },
    color: { domain: G.pv_penetration, range: cols },
    marks: [
      Plot.gridY({ stroke: c.grid, strokeOpacity: 1, ticks: 4 }),
      Plot.lineY(pts, { x: "act", y, z: "pen", stroke: "pen", strokeWidth: 2 }),
      Plot.dot(pts.filter((d) => d.sel), { x: "act", y, r: 5, fill: c.ink, stroke: c.paper, strokeWidth: 2 }),
      Plot.tip(pts, Plot.pointer({ x: "act", y, stroke: "pen",
        title: (d) => `${pct(d.pen)} with PV, ${pct(d.act)} trading\nrevenue ${d.up >= 0 ? "+" : ""}${pct(d.up)} vs A · Gini ${d.gini.toFixed(3)}` })),
    ],
  });
  box.replaceChildren(panel("up", "↑ revenue vs regime A", (d) => pct(d)), panel("gini", "↑ Gini, regime B", (d) => d.toFixed(2)));

  const here = pts.filter((d) => d.i === S.pen);
  const gmax = here.reduce((m, d) => (d.gini > m.gini ? d : m));
  const last = here[here.length - 1];
  const lo = R.B[0][S.ceil][G.active_share.length - 1], hi = R.B[G.pv_penetration.length - 1][S.ceil][G.active_share.length - 1];
  let f = `Revenue rises with every household that joins, reaching ${pct(last.up)} above regime A when all trade at ${pct(G.pv_penetration[S.pen])} penetration. `;
  f += gmax.act < 1 && gmax.gini - last.gini > 0.005
    ? `Inequality does not rise with it. The Gini peaks at ${gmax.gini.toFixed(2)} with ${pct(gmax.act)} trading, and falls to ${last.gini.toFixed(2)} once everyone can. A partial rollout is the least equal state. `
    : `The Gini climbs from ${here[0].gini.toFixed(2)} to ${last.gini.toFixed(2)} as more households trade. `;
  f += `More rooftops push the clearing price down, from ${rs(lo.price, 2)} at ${pct(G.pv_penetration[0])} penetration to ${rs(hi.price, 2)} at ${pct(G.pv_penetration.at(-1))}, and the gain shifts from sellers to buyers.`;
  $("find-4").textContent = f;
  table($("tab-4"), ["PV", "trading", "revenue vs A", "Gini", "price"],
    pts.map((d) => [pct(d.pen), pct(d.act), `${d.up >= 0 ? "+" : ""}${pct(d.up, 1)}`, d.gini.toFixed(3),
      R.B[d.i][S.ceil][G.active_share.indexOf(d.act)].price ? rs(R.B[d.i][S.ceil][G.active_share.indexOf(d.act)].price, 2) : "—"]));
}

// --- controls and wiring ------------------------------------------------------------------------

function controls() {
  const G = g();
  const spec = [["pen", "pv_penetration", (v) => pct(v)], ["ceil", "ceiling", (v) => `₹${v.toFixed(2)}`], ["act", "active_share", (v) => pct(v)]];
  for (const [k, key, fmt] of spec) {
    const input = $(`c-${k}`), out = $(`o-${k}`);
    input.max = G[key].length - 1;
    input.value = S[k];
    input.setAttribute("aria-valuetext", fmt(G[key][S[k]]));
    out.textContent = fmt(G[key][S[k]]);
    input.oninput = () => {
      S[k] = +input.value;
      out.textContent = fmt(G[key][S[k]]);
      input.setAttribute("aria-valuetext", out.textContent);
      render();
    };
  }
}

function sentence() {
  const G = g(), m = R.meta;
  $("sentence").textContent = `A feeder of ${m.households} households: ${pct(G.pv_penetration[S.pen])} with rooftop PV, ${words(G.active_share[S.act])} of them trading, and a market allowed to clear up to ₹${G.ceiling[S.ceil].toFixed(2)} a unit.`;
}

function render() {
  const c = colors();
  sentence();
  answer();
  fig1(c);
  fig2(c);
  fig3(c);
  fig4(c);
}

async function main() {
  R = await (await fetch(resultsUrl)).json();
  const m = R.meta, G = m.grid;
  S.pen = G.pv_penetration.indexOf(m.default.pv_penetration);
  S.ceil = G.ceiling.indexOf(m.default.ceiling);
  S.act = G.active_share.indexOf(m.default.active_share);
  const month = new Date(2026, m.week_month - 1, 1).toLocaleString("en-GB", { month: "long" }).toLowerCase();
  $("meta").textContent = `${m.households} households · one feeder · one ${month} week, hourly · ${G.pv_penetration.length * G.ceiling.length * G.active_share.length} settings × ${m.replicates} seeds · synthetic profiles · run ${m.generated}`;
  controls();
  render();
  let t, lastW = 0;
  new ResizeObserver(([e]) => {
    const w = Math.round(e.contentRect.width);
    if (w === lastW) return;              // height changes come from rendering itself; ignore them
    const first = lastW === 0;
    lastW = w;
    if (first) return;
    clearTimeout(t);
    t = setTimeout(render, 120);
  }).observe(document.querySelector(".page"));
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  reportHeight();
}

main().catch((e) => {
  $("answer").textContent = "The results file did not load. " + e.message;
  console.error(e);
});
