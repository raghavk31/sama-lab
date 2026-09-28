# Grid observability vs rooftop solar: data survey

Step 1 of instrument 02. Accessed 2026-09-29. Nothing has been built. Source IDs (S01…) refer to
[`sources.csv`](sources.csv); cached files are in [`raw/`](raw/).

**Status: awaiting a decision** between a national map, Bengaluru and Delhi (see Recommendation).

How to read the claims: "opened" means the page or file was fetched and the relevant part read.
**[unconfirmed]** means the claim rests on a search snippet, press coverage or inference, and was not
verified. Two claims were spot-checked against the cached files afterwards: the RDSS zeros for
Karnataka (S02), and BESCOM's 7,149 feeders and 18,181 SRTPV installations of 403.18 MW (S11).

## Summary answers

**1. Finest public resolution for smart meter penetration: DISCOM.**
- The RDSS dashboard (S02, live, read through its JSON API) gives sanctioned, installed and
  communicating counts of consumer, DT and feeder smart meters by DISCOM.
- The NSGM dashboard (S01) covers all schemes at national and state level. It could only be read from
  a printout stamped 25-08-2025, because the site refused connections. Whether it drills down to DISCOM is
  [unconfirmed].
- No public source gives consumer smart meter counts below DISCOM.
- **The exception for DT and feeder meters is BESCOM.** Its quarterly BEE energy-accounting files (S10,
  S11) give metering status for every feeder: metered and unmetered DTs, and communicable and
  non-communicable DT meters. The 2026 edition adds feeder meter communication status and the share of
  data received automatically.

**2. Feeder-level data published by a state: yes, BESCOM (Karnataka). No other was found.**
- **BESCOM:** feeder-wise T&D and AT&C loss, feeder meter type, and DT metering and DT-wise losses,
  every quarter. XLSX from Q2 FY22 to Q1 FY25, then text PDFs to Q1 FY27 (filed 7 Sep 2026).
- **Delhi:** BYPL and TPDDL state that feeder-wise AT&C is not computed on their ring networks (S13,
  S14). Both publish division-level losses.
- **Uttar Pradesh:** PVVNL's annual audit (S18) has only a feeder loss-range table and a worst-10% list.
  UPPCL's feeder portal needs a login (S19).
- **MSEDCL, Gujarat, Tamil Nadu:** not opened; [unconfirmed] either way.
- **National:** NFMS feeder data needs a login (S06). The NPP feeder data dates from 2014-15 (S07).

**3. Finest public resolution for rooftop solar: state. District exists, but only ad hoc.**
- **State:** MNRE, monthly (S21, as of 31-08-2026).
- **District and DISCOM:** PM Surya Ghar holds these, but as gated MIS reports (S22). District tables
  surface only in parliamentary answers (S23, Tamil Nadu, 22-07-2026).
- **DISCOM totals:** BESCOM 18,181 installations, 403 MW (S11); TPDDL, FY23 audit (S14).
- **Sub-DISCOM:** only BYPL, with division- and subdivision-wise embedded rooftop generation for
  FY2022-23 (S13).
- No pincode or feeder-level solar data was found.

**4. Is smart metering "state-level only"? No.**
Consumer, DT and feeder smart meter counts are public at DISCOM level (S02). But:
- consumer counts are not public below DISCOM anywhere;
- both candidate cities are outside RDSS smart metering: Karnataka, BRPL, BYPL and TPDDL show zero
  installed in S02;
- BESCOM's own filing reports 0 consumer smart meters for Apr–Jun 2026 (S11).

By the brief's rule, a national build is not ruled out. In practice, a DISCOM-level national map has
about 70 units, no DISCOM-level solar series to pair with, and both cities would be holes in it.

## Source by source

- **S01 NSGM, All India / State-wise Smart Metering Status** (Ministry of Power).
  - nsgm.gov.in refused connections (ECONNREFUSED) on repeated tries. Read from a third-party printout
    stamped 25-08-2025, with data as of 15-Aug-2025.
  - Consumer, DT and feeder smart meters: sanctioned, installed and ongoing, by scheme (RDSS,
    utility-owned, PMDP) and by agency (PFC, REC, EESL). State map. DISCOM drill-down [unconfirmed].
  - Covers IS-16444 meters only. HTML with no download. https://www.nsgm.gov.in/en/sm-stats-all
- **S02 RDSS dashboard** (Ministry of Power / REC).
  - React app over an unauthenticated JSON API (`/apiv1/getProgressDetailSm`; report types Allindia,
    DisStates, Discom). Sanctioned, awarded, installed and communicating counts for consumer, DT and
    feeder metering, at all-India, state and DISCOM level (82 utilities). Live.
  - On the access date: all-India consumer meters 195.8M sanctioned, 58.4M communicating; UP about 27.0M
    sanctioned; Karnataka, BESCOM, BRPL and BYPL zero installed.
  - District sanction data sits behind the admin login. The API is undocumented and was queried a
    handful of times, not crawled.
  - https://rdss.powermin.gov.in/discom-view-dashboard
- **S03 RDSS feeder-wise report.** Loss-reduction works per feeder (assets sanctioned, erected,
  charged). Not metering or loss data; not useful here.
- **S04/S05 CEA, Report on Status of Metering.**
  - Opened the 31-03-2025 edition (published Oct 2025, text PDF). DISCOM level with an urban/rural split.
  - Share of metered 11 kV and 33 kV feeders, DTs and consumers by category. Metered vs unmetered only,
    not smart vs conventional.
  - Self-reported. Prayas (S30) notes it has no meter type and no operational status.
- **S06 NFMS.** App shell only. Public routes: landing, about, major cities, dashboard. Feeder data
  needs an Oracle IDCS login. About 2.5 lakh 11 kV feeders (press). Whether the public views show state or
  DISCOM summaries is [unconfirmed].
- **S07 National Power Portal.** Opened. Feeder AT&C and "worst feeder" widgets dated 2014-09 to
  2015-08. Stale.
- **S08 PFC, Report on Performance of Power Utilities (2023-24, 2024-25).** Could not open:
  pfcindia.co.in serves its app shell for every document URL. From press only [unconfirmed]: DISCOM-level
  AT&C, billing, collection and finances for about 63 utilities; nothing below DISCOM expected.
- **S09 BEE Annual Energy Audit, BESCOM FY2023-24.** Opened, text PDF.
  - Division-wise AT&C; division-wise DTC metering % (March 2024).
  - States that all 6,389 feeders are metered and audited monthly; includes a 60-feeder validation
    sample.
  - SRTPV: 9,207 installations, 293 MW. Smart consumer metering "not yet commenced".
- **S10 BESCOM quarterly energy accounting, Q1 FY2024-25 (XLSX).** Opened and parsed.
  - Sheets: feeder levels (6,487 feeders), DTC metering (6,486 rows), DTC-wise losses (~60,000 rows),
    division-wise losses, infrastructure.
  - Feeder rows carry zone, circle, division, subdivision, station, feeder code and name, type, meter
    type, input, consumption, export, T&D %, AT&C % and remarks such as "communication work under
    process".
  - Every feeder meter is typed "DLMS" and no DT meter is communicable, so the observability signal
    barely varies across feeders in this vintage. Consumer smart meters: 70 (DISCOM total).
- **S11 BESCOM quarterly, Q1 FY2026-27 (PDF).** Opened, text-extractable.
  - 9 circles, 32 divisions, 148 subdivisions, 7,149 feeders, 568,472 DTs, 15.28M consumers; 216 DTs
    with communicable meters; 0 consumer smart meters.
  - 18,181 SRTPV installations, 403.18 MW (DISCOM total).
  - Feeder tables add metering status, communication status and % of data received automatically.
    Extraction to tables is feasible but needs column work.
- **S12 BESCOM quarterly index.** Twenty quarters, Q2 FY22 to Q1 FY27.
- **S13 BEE Annual Energy Audit, BYPL FY2022-23.** Opened.
  - Circle and division AT&C; a subdivision-wise embedded generation table (rooftop solar by voltage and
    subdivision).
  - Says feeder-wise loss is not feasible (ring mains) and replaces DT-wise loss with a cluster report
    to DERC. Smart meter counts blank. No later BYPL audit found.
- **S14/S15 TPDDL annual energy accounting, FY2022-23 and FY2024-25.** Opened.
  - Division-wise AT&C. Smart meters as DISCOM totals: 315,336 (FY23); 529,083 plus 10,094 prepaid
    (FY25). Feeder-wise AT&C "not available".
- **S16/S17 TPDDL quarterly.** Division-wise losses, Jul 2021 to Mar 2025. No later quarter found.
- **BRPL.** No BEE energy audit found on bsesdelhi.com or through BEE. DERC tariff petitions (S33) not
  opened.
- **S18 PVVNL (UP) audit FY2023-24.** Opened. Circle and division AT&C, feeder loss-range counts,
  worst-feeder list, DT metering 9%.
- **S19 UPPCL feeder energy portal.** Login and captcha only.
- **S20 MSEDCL audit.** Not opened.
- **S21 MNRE state-wise RE capacity as of 31-08-2026.** Opened. Rooftop solar including PM Surya Ghar:
  Karnataka 938.20 MW, Delhi 454.30 MW.
- **S22 PM Surya Ghar portal.** App code only. National, state and DISCOM application summaries are
  entitlement-gated MIS reports. A district GIS view exists in the code; public availability
  [unconfirmed]. Residential only, since Feb 2024.
- **S23 Lok Sabha SQ 59 (22-07-2026).** Opened. District-wise PMSG installations for Tamil Nadu,
  showing the ministry holds district data.
- **S24 data.gov.in PMSG state-wise.** HTTP 403.
- **S25 solarrooftop.gov.in.** Unreachable.
- **S26 OpenCity BESCOM boundary maps (source KSRSAC).** Opened and downloaded.
  - Divisions: 32 polygons covering the whole service area; names match the reports.
  - Subdivisions: 90 polygons. Sections: 237 polygons. Both look partial against the 148 subdivisions
    in S11.
  - Dataset updated 2025-11-27; underlying KSRSAC vintage unknown.
- **S27 OpenCity Delhi electricity.** Substation points only. No open Delhi DISCOM or division
  boundaries found.
- **S28 India Energy Stack strategy v0.4 (March 2026).** Opened. Draft, sandbox and pilot stage, built
  on consent-based data sharing. Its "public data" block concerns tariffs. No public grid telemetry.
- **S29/S30 Prayas.** Opened. Both confirm public metering data stops at DISCOM and is self-reported.

## What exists for Bengaluru (BESCOM)

**Observability**

| source | unit | contents | format, vintage |
|---|---|---|---|
| quarterly energy accounting (S10, S11) | feeder, aggregable to subdivision / division / circle | AT&C and T&D loss; share of DTs metered; DT meter communicability; feeder meter communication and % automatic data (2026) | XLSX to Jun 2024; text PDF to Jun 2026 |
| annual audit (S09) | division | AT&C, DT metering % | PDF, FY24 |
| RDSS, NSGM (S02, S01) | — | nothing: Karnataka is not in RDSS smart metering | — |

Consumer smart meters are public only as a BESCOM total, and it reads 0. Press reports of about 15,000
smart meters on new connections are [unconfirmed].

**Solar.** Only the BESCOM total is public: 18,181 installations, 403 MW (S11). The state total is 938 MW
(S21). No division or subdivision SRTPV table was found. Possible routes, none checked yet: KERC tariff
filings; the "Export" column in the feeder sheets, which may partly reflect embedded generation; a PM
Surya Ghar district answer for Bengaluru Urban and neighbouring districts; an RTI request.

**Boundaries.** KSRSAC division polygons via OpenCity cover the full area (32 divisions). Subdivision
polygons exist but look incomplete. There are no feeder service-area polygons, but feeder rows carry
station, subdivision and division, so they aggregate to division.

## What exists for Delhi (BRPL, BYPL, TPDDL)

**Observability**

| DISCOM | unit | contents | vintage |
|---|---|---|---|
| TPDDL | division | AT&C, quarterly | to Mar 2025 (S16) |
| TPDDL | DISCOM | smart meter totals | FY25 (S15) |
| BYPL | division | AT&C | FY23 audit only (S13) |
| BRPL | — | nothing found below DISCOM | — |

No feeder-wise AT&C: BYPL and TPDDL say ring networks prevent it. DT metering is near 100% in each
DISCOM (S04, S14), so metering share does not separate areas.

**Solar.** BYPL subdivision-wise embedded generation, FY2022-23 (S13); TPDDL DISCOM totals; news
figures by DISCOM [unconfirmed] (S31); state total 454 MW (S21).

**Boundaries.** No open DISCOM, division or subdivision polygons. They would have to be constructed,
for example from ward or assembly boundaries matched to division names. That is non-trivial and would need
checking.

## Recommendation

For Raghav to decide. The survey's reading:

- **National, by DISCOM.** Observability from RDSS installed and communicating counts (S02), CEA
  metering (S04) and PFC AT&C (S08). Solar only at state level (S21). DISCOM service areas are not openly
  available as boundaries. About 70 units, many equal to a whole state. RDSS excludes non-RDSS rollouts,
  so Karnataka and Delhi read as zero. Feasible, but the index would mostly restate state differences.
  Not recommended as the first build.
- **Bengaluru, by BESCOM division (subdivision if the boundaries hold). Recommended.**
  - Observability from the feeder-level files (S10, S11) aggregated to division: share of DTs metered,
    share communicable, feeder-meter communication rate, AT&C. A time series back to 2021 is possible.
  - Boundaries from KSRSAC division polygons (S26).
  - **The weak side is solar.** Division-level SRTPV is not public and must be obtained before any
    mismatch index is honest. First follow-up: check KERC filings, the feeder "Export" column and a PM
    Surya Ghar district answer, then decide whether to file an RTI request.
  - The 2024 observability signal is flat (no communicable DT meters). The 2026 PDFs need extracting to
    see whether it now varies.
- **Delhi, by division.** Observability from TPDDL and BYPL division AT&C (S13, S16); solar from BYPL's
  subdivision table (S13). No feeder data by design, BRPL largely missing, old vintages (BYPL FY23),
  and boundaries to construct. Better solar data for one DISCOM; weaker on everything else.

## Gaps and caveats

- **Self-reported.** Almost everything is self-reported by DISCOMs. The audits are commissioned by the
  DISCOM, and CEA and RDSS collate what DISCOMs submit. BESCOM reporting 0 smart meters against press
  figures shows the kind of inconsistency to expect.
- **Vintage mismatch.** Observability runs from Jun 2024 (XLSX) to Jun 2026 (PDF). Solar runs from Aug 2026
  (state) back to Mar 2024 or FY23 (DISCOM, subdivision). An index would mix years unless the sources are
  aligned deliberately.
- **Scheme-bound coverage.** RDSS covers only RDSS-funded meters, and PM Surya Ghar only residential systems
  since Feb 2024. Neither gives total penetration.
- **Weak proxies.** AT&C loss is a noisy proxy for metering discipline, since it includes theft and
  collection. The feeder "meter type" in BESCOM's 2024 file does not discriminate between feeders.
- **Inconsistent units.** BESCOM's feeder sheet lists 34 division and 218 subdivision names, while the summary
  gives 32 and 148. Names need reconciling against the KSRSAC codes.
- **Unreachable sources.** NSGM, PFC, solarrooftop.gov.in and data.gov.in were unreachable or blocked from
  this machine. Their contents are described from secondary material.
- **Undocumented API.** Building on the RDSS API should be a conscious choice, and its figures should be
  cross-checked against NSGM.
