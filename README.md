# Orbital Lab Notebook Local

Routine orbital manufacturing needs end-to-end traceability from experiment recipe to capsule recovery and material assay.

The demo hook is concrete: A capsule timeline ties orbital conditions, deorbit readiness, and post-landing assay evidence into one notebook.

## Thesis

Offline capsule experiment provenance and reentry-readiness notebook for orbital manufacturing.

## Primitives

- Seeds `capsule experiment` fixtures for `Orbital Lab Notebook` with both normal operations and faulted paths.
- Computes `recipe_traceability`, `thermal_excursion_detected`, `reentry_readiness`, and `assay_linkage` from deterministic inputs so the result can be reproduced exactly.
- Stress-tests `missing_chain_of_custody`, `thermal_excursion`, `deorbit_window_conflict`, and `assay_mismatch` as named failure classes rather than vague edge cases.
- Packages `Orbital Lab Notebook Local` artifacts for code review, live demo, and regression comparison.

## Reproduce locally

```bash
uv sync --extra dev
uv run orbital-notebook init-demo --force
uv run orbital-notebook run-suite
uv run orbital-notebook verify
uv run orbital-notebook dashboard
uv run orbital-notebook benchmark --iterations 100
uv run orbital-notebook export-demo-pack
```

## Review packet

- `data/scenarios.json`
- `outputs/summary.json`
- `outputs/reports.json`
- `outputs/evidence_pack.md`
- `outputs/dashboard.html`
- `outputs/benchmark.json`
- `outputs/demo-pack.zip`

## Confidence checks

```bash
uv run ruff check .
uv run pytest -q
uv run orbital-notebook run-suite
uv run orbital-notebook verify
uv run orbital-notebook benchmark --iterations 100
```

## Data limits

Every example in `orbital-lab-notebook-local` is fabricated for repeatability. Generated outputs are rebuildable artifacts, not source material.
