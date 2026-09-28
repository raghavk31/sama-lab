// The essay's markup, from the answer to the caveats. The host page supplies the title above it:
// the standalone page (abm/index.html) and raghavkohli.xyz/work/sama/feeder/ each have their own.
export const essay = (links) => `
  <p class="meta" id="meta"></p>
  <p class="answer" id="answer">Loading the model's results…</p>

  <section class="controls" id="controls" aria-label="Model settings">
    <p class="controls__sentence" id="sentence"></p>
    <div class="controls__row">
      <label><span class="label">pv penetration</span><input type="range" id="c-pen" min="0" step="1"><output id="o-pen"></output></label>
      <label><span class="label">p2p price ceiling</span><input type="range" id="c-ceil" min="0" step="1"><output id="o-ceil"></output></label>
      <label><span class="label">households trading</span><input type="range" id="c-act" min="0" step="1"><output id="o-act"></output></label>
    </div>
  </section>

  <h2><span class="n">01</span>Where the surplus goes</h2>
  <p>A rooftop first powers its own house. What it cannot use, it exports. The first question is who
    gets paid for that export. In regime A the answer is always the DISCOM. In regime B, a household that
    trades offers its surplus each hour at a price of its choosing. Whatever finds no buyer still falls back
    to the DISCOM.</p>
  <figure>
    <div class="legend" id="leg-1"></div>
    <div class="chart" id="fig-1"></div>
    <p class="finding" id="find-1"></p>
    <figcaption><span class="n">fig. 1</span> Each exported kWh, by who absorbed it, as a share of the
      feeder's surplus over the week. Curtailed is energy the inverters were asked not to produce, because
      the transformer could not take it back upstream.</figcaption>
    <details><summary>the numbers</summary><div class="scroll-x" id="tab-1"></div></details>
  </figure>
  <p id="physics"></p>

  <h2><span class="n">02</span>Who captures it</h2>
  <p>A higher average says little on its own. What matters is which households the gain reaches.
    Each dot is one rooftop, placed by what its exports earned in the week.</p>
  <figure>
    <div class="legend" id="leg-2"></div>
    <div class="chart" id="fig-2"></div>
    <p class="finding" id="find-2"></p>
    <figcaption><span class="n">fig. 2</span> Export revenue per prosumer household, ₹ per week, one dot
      each. Ticks mark the median and the 90th percentile. The Gini coefficient runs from 0, where every
      rooftop earns the same, to 1, where one rooftop earns everything.</figcaption>
    <details><summary>the numbers</summary><div class="scroll-x" id="tab-2"></div></details>
  </figure>
  <figure>
    <div class="chart" id="fig-2b"></div>
    <p class="finding" id="find-2b"></p>
    <figcaption><span class="n">fig. 2b</span> What each rooftop gains under regime B against regime A,
      by the size of its system. The same households appear in both regimes.</figcaption>
  </figure>
  <p id="split"></p>

  <h2><span class="n">03</span>The feeder's day</h2>
  <p>Power flow at the transformer, averaged over the week's days. Above zero, the feeder is pushing
    power back up the network. Below it, the feeder is drawing power.</p>
  <figure>
    <div class="legend" id="leg-3"></div>
    <div class="chart" id="fig-3"></div>
    <p class="finding" id="find-3"></p>
    <figcaption><span class="n">fig. 3</span> Mean net export at the distribution transformer by hour of
      day, kW. The two regimes differ only because some households in B move part of their load into the
      hours they can now see the feeder exporting.</figcaption>
    <details><summary>the numbers</summary><div class="scroll-x" id="tab-3"></div></details>
  </figure>

  <h2><span class="n">04</span>How much of this is the settings</h2>
  <p>The settings above are three guesses about a feeder no one has yet measured: how many roofs
    have panels, how high the market may price a unit, and how many households would bother to trade.
    Each line below is one penetration level, at the price ceiling you chose above.</p>
  <figure>
    <div class="legend" id="leg-4"></div>
    <div class="chart sm" id="fig-4"></div>
    <p class="finding" id="find-4"></p>
    <figcaption><span class="n">fig. 4</span> Left: mean prosumer revenue under B, as a change from A.
      Right: the Gini coefficient of prosumer revenue under B. The dot is the setting you chose. Each
      point is the mean of five seeded runs.</figcaption>
    <details><summary>the numbers</summary><div class="scroll-x" id="tab-4"></div></details>
  </figure>

  <h2><span class="n">05</span>What this is not</h2>
  <div class="note">
    <p><strong>It is not data.</strong> Every consumption and generation profile here is synthetic:
      hand-drawn day shapes, a textbook solar curve and a random cloud draw. Nothing on this page was
      measured on a real feeder.</p>
    <p><strong>The behaviour is a placeholder.</strong> How eagerly a household prices, whether it
      trades at all, and how much load it moves are guesses. They are waiting on prosumer interviews that have
      not yet been done.</p>
    <p><strong>The network is one transformer.</strong> There is no voltage, no losses, no phase
      imbalance, and no wheeling, banking or cross-subsidy charges. Those charges sit between the two
      prices, and they would narrow every gain shown here.</p>
    <p><strong>It is unvalidated.</strong> The model has been tested to be internally consistent (energy
      balances every hour, seeded runs repeat exactly). It has not been checked against any real feeder.</p>
  </div>
  <p class="meta sa-links">method, assumptions and sources in the
    <a href="${links.readme}">readme</a> · part of <a href="${links.sama}">sama</a></p>
`;
