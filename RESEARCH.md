# Research And Plan Review

Project: `capsule-readiness-ledger`

## Refined Thesis

Orbital manufacturing teams need traceable mission evidence that connects capsule conditions, reentry events, recovery handling, and post-flight lab characterization.

The implementation is intentionally local and synthetic, but the test harness is shaped around the real operating question: can the proposed artifact create evidence a founder, CTO, or space-systems leader would immediately recognize as useful?

## Fresh Sources Checked

- Public orbital manufacturing and reentry-capsule context.
- Local synthetic flight-and-lab fixture model.

## Plan Excerpt Used

## The Gap

Capsule missions create two high-value evidence streams: on-orbit/reentry telemetry and post-recovery material characterization. The business-critical question is causal and operational: which mission conditions correspond to which material outcomes, and can a team prove capsule readiness before the next flight?

The missing artifact is a local, governed Mission-to-Material ledger that joins flight phases, environmental windows, recovery events, and lab evidence into one replayable timeline.

## The Project - `capsule-readiness-ledger`

> A local orbital lab notebook that turns synthetic capsule telemetry and bench results into traceable readiness receipts.

**What it is.** A deterministic CLI, fixture generator, evaluator, dashboard, benchmark, and evidence-pack exporter. It models mission phases, microgravity quality, thermal windows, reentry shock, recovery delays, lab measurements, and readiness gates.

**Why it solves the gap.** Three vectors:

1. **Joined evidence.** Flight and lab records are connected by mission phase and material sample rather than reviewed as separate files.
2. **Readiness gates.** The harness reports whether evidence is sufficient for the next capsule campaign.
3. **Replayable traceability.** Every finding points back to deterministic synthetic telemetry and lab records.

**The demonstration moment.** A synthetic capsule run shows a microgravity-quality excursion during a material processing window. The dashboard traces the event to downstream lab characterization, marks the readiness impact, and exports a compact evidence pack for review.

## Prototype Plan

- **Fixture generator:** deterministic clean and degraded flight-and-lab cases.
- **Evaluator:** scores mission evidence coverage, sample traceability, reentry readiness, and lab correlation quality.
- **Dashboard:** visualizes readiness gates, metric means, top failure modes, and evidence gaps.
- **Evidence pack:** Markdown plus zipped artifacts for portable review.
- **What I measure:**
  - Mission evidence coverage.
  - Sample traceability.
  - Reentry readiness.
  - Lab correlation quality.

## Build Acceptance Criteria

- Deterministic local fixtures.
- Domain-specific metrics and failure modes.
- Passing unit tests.
- Passing CLI verifier.
- Static dashboard generated locally.
- Benchmark output under the project `outputs/` folder.
- Public-safe README: no founder emails, no private outreach text, no credentials.
