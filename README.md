# Orbital Lab Notebook Local

Offline capsule experiment provenance and reentry-readiness notebook for orbital manufacturing.

This is a local-first, synthetic-data prototype inspired by a company-specific project plan for **Varda Space**. It is built to demonstrate the engineering shape of `Orbital Lab Notebook` without private data, credentials, external APIs, or hosted services.

## Why it matters

Routine orbital manufacturing needs end-to-end traceability from experiment recipe to capsule recovery and material assay.

## What it does

- Generates deterministic synthetic `capsule experiment` scenarios.
- Scores each scenario against domain-specific quality gates.
- Produces evidence-backed findings for realistic failure modes.
- Writes a static dashboard, JSON reports, benchmark output, and a portable demo pack.
- Exposes a JSONL tool loop for local agent integration.

## Metrics

- `recipe_traceability`
- `thermal_excursion_detected`
- `reentry_readiness`
- `assay_linkage`

## Failure modes

- `missing_chain_of_custody`
- `thermal_excursion`
- `deorbit_window_conflict`
- `assay_mismatch`

## Quickstart

```bash
uv sync --extra dev
uv run orbital-notebook init-demo --force
uv run orbital-notebook run-suite
uv run orbital-notebook verify
uv run orbital-notebook dashboard
uv run orbital-notebook benchmark --iterations 100
uv run orbital-notebook export-demo-pack
```

## Expected outputs

- `data/scenarios.json`
- `outputs/summary.json`
- `outputs/reports.json`
- `outputs/evidence_pack.md`
- `outputs/dashboard.html`
- `outputs/benchmark.json`
- `outputs/demo-pack.zip`

## Validation

```bash
uv run ruff check .
uv run pytest -q
uv run orbital-notebook run-suite
uv run orbital-notebook verify
uv run orbital-notebook benchmark --iterations 100
```

## Demo hook

A capsule timeline ties orbital conditions, deorbit readiness, and post-landing assay evidence into one notebook.
