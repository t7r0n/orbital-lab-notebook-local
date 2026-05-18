# Research And Plan Review

Company: Varda Space
Project: `Orbital Lab Notebook`

## Refined Thesis

Routine orbital manufacturing needs end-to-end traceability from experiment recipe to capsule recovery and material assay.

The implementation is intentionally local and synthetic, but the test harness is shaped around the real operating question: can the proposed artifact create evidence a founder, CTO, or product leader would immediately recognize as useful?

## Fresh Sources Checked

- https://www.varda.com/
- https://www.space.com/varda-in-space-manufacturing-capsule-reentry-photos
- https://www.nasa.gov/wp-content/uploads/2026/01/flight-opportunities-newsletter-january-2026.pdf

## Plan Excerpt Used

## The Gap

Varda has spent four missions producing two distinct, *priceless* data assets that nobody is fusing: (1) the **on-orbit + reentry environment record** for each capsule — temperatures, vibration, microgravity quality, reentry shock-layer spectroscopy (cf. OSPREE on W-2), heat-shield ablation profile (cf. in-house C-PICA on W-4); and (2) the **post-recovery pharmaceutical characterization** record — XRPD diffractograms, DSC/TGA traces, particle morphology — for the API or biologic that flew. As Varda's flight cadence grows from 4 missions to N missions per year under the FAA Part 450 reusable operator license, the *causal* question becomes the entire business: *which on-orbit conditions produce which crystal-form outcomes?* Today this lives in two unconnected stacks: SRE-team flight telemetry, and pharma-team lab instrument files. There is no single, governed, queryable **Mission ↔ Material Twin** that lets a scientist ask "show me every flight where the microgravity quality dipped below 10⁻⁵ g during the polymorph soak window, and overlay the XRPD intensity at 2θ=19.4° for the recovered sample." That twin is the substrate Varda needs to make orbital pharma *boring* — and it does not exist publicly.

## The Project — `Orbital Lab Notebook` (`orbital-lab-notebook`)

> A flight-and-bench unified data plane that turns every W-series mission into a queryable, replayable Mission↔Material Twin — built on the languages Varda's flight software team already speaks.

1. **What it is.** A self-hosted OSS project: a Rust ingestion daemon that consumes CCSDS-formatted telemetry from a flight-software emulator and instrument files (XRPD `xy`/`raw`, DSC/TGA `csv`, particle-size `csv`/`xlsx`) and lands them in a **DuckDB + Parquet** lakehouse with a fixed schema (`mission`, `capsule`, `payload_slot`, `phase`, `material_lot`, `instrument`, `reading`). On top: a **JupyterLab Lite + Observable Plot** notebook surface that ships *opinionated* templates ("polymorph-form by microgravity-quality scatter," "DSC peak shift vs reentry deceleration profile," "shock-layer spectroscopy vs heat-shield ablation"). A small **diff-and-replay** CLI takes two missions and produces a 1-page PDF *Mission Pairing Report*.
2. **Why it solves the gap.** It is the join that turns four expensive-but-isolated flights into one repeatable manufacturing process. It speaks Will Bruey's native idioms — CCSDS, flight phases, ground-system pipelines — *and* the pharma scientists' native idioms — XRPD 2θ, DSC peak, particle morphology. It plugs the unowned seam between the Data Engineer (SRE) role and the pharma team Varda just hired.
3. **The "wow" moment.** A 60-second demo: pick W-2 vs W-3 (real public missions). Click "Mission Pairing Report." A PDF appears: a labelled timeline showing the polymorph-soak window on each mission, the microgravity quality envelope during that window, and the *delta* between the two missions' XRPD signatures of the recovered ritonavir lot, with a callout — *"During W-3's soak window, attitude-control thruster firings introduced 14 transient g-jitter events > 10⁻⁴ g; W-2 had 2. Polymorph Form III peak at 2θ=19.4° is +18% in W-2 sample. Hypothesis: thruster duty cycle during soak materially affects polymorph yield."* That is the screenshot Will pastes in the next investor update.

## Prototype Plan (the shippable demo)

**Surface a user invokes:**

```bash
orbital-lab-notebook ingest \
  --mission W-2 \
  --telemetry W2_ccsds.bin \
  --xrpd W2_ritonavir.xy \
  --dsc W2_ritonavir_dsc.csv

orbital-lab-notebook pair --a W-2 --b W-3 --out W2_vs_W3.pdf
orbital-lab-notebook serve              # → JupyterLab Lite at :8888
```

**Five representative inputs (the demo, all synthesised from the public mission record):**
1. W-1 ritonavir telemetry + XRPD → confirm Form III peak.
2. W-2 OSPREE shock-layer OES + heat-shield ablation → reentry environment fingerprint.
3. W-2 vs W-3 (both ritonavir) → Mission Pairing Report with DTW-aligned soak comparison.
4. W-3 → simulated mAb crystallization (forward-looking; uses public XRPD reference for a model mAb).
5. W-4 in-house heatshield ablation profile → "what new envelope did the in-house bus open?"

**Expected output / screen:** the 1-page PDF Pairing Report as the hero artifact; a JupyterLab Lite tab open to the "Polymorph Form vs Microgravity Quality" scatter; a SQL prompt showing the literal query a scientist would type.

**Metrics to prove it works:**
- Ingestion throughput: 10 MB/s of CCSDS packets sustained on a laptop (single-thread Rust + zero-copy).
- Cross-mission DTW alignment: < 5s on two soak windows ~4 hours each.
- Query latency on 4-mission aggregate (DuckDB on Parquet): p95 < 200 ms.
- Schema stability: zero breaking changes across the demo's 5 inputs.


## Build Acceptance Criteria

- Deterministic local fixtures.
- Domain-specific metrics and failure modes.
- Passing unit tests.
- Passing CLI verifier.
- Static dashboard generated locally.
- Benchmark output under the project `outputs/` folder.
- Public-safe README: no founder emails, no private outreach text, no credentials.
