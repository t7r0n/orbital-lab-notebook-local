from __future__ import annotations

import json
import random
from pathlib import Path

from .models import ProjectConfig, Scenario


def load_config(root: Path) -> ProjectConfig:
    config_path = root / "project_config.json"
    if not config_path.exists():
        config_path = Path.cwd() / "project_config.json"
    return ProjectConfig.model_validate_json(config_path.read_text(encoding="utf-8"))


def data_dir(root: Path) -> Path:
    return root / "data"


def output_dir(root: Path) -> Path:
    return root / "outputs"


def _metric_value(index: int, metric_index: int, clean: bool, rng: random.Random) -> float:
    base = 0.82 + ((index + metric_index * 7) % 13) / 100
    if clean:
        return min(0.99, base + rng.uniform(0.02, 0.07))
    penalty = 0.18 + ((index + metric_index * 3) % 9) / 100
    return max(0.05, base - penalty + rng.uniform(-0.03, 0.02))


def generate_scenarios(config: ProjectConfig) -> list[Scenario]:
    rng = random.Random(config.repo)
    scenarios: list[Scenario] = []
    for idx in range(config.fixture_count):
        clean = idx < config.clean_count
        mode = "nominal" if clean else config.failure_modes[(idx - config.clean_count) % len(config.failure_modes)]
        signals = {metric: round(_metric_value(idx, m_idx, clean, rng), 4) for m_idx, metric in enumerate(config.metrics)}
        risk = 1.0 - (sum(signals.values()) / len(signals))
        if not clean:
            risk = min(0.99, risk + 0.18 + ((idx % 5) * 0.025))
        expected = [] if clean else [mode]
        evidence = [
            f"{config.scenario}:{idx:04d}:source-manifest",
            f"{config.project}:{mode}:metric-snapshot",
            f"{config.company}:local-synthetic-fixture",
        ]
        scenarios.append(
            Scenario(
                id=f"{config.scenario.replace(' ', '-')}-{idx:04d}",
                kind=config.scenario,
                clean=clean,
                risk=round(risk, 4),
                mode=mode,
                signals=signals,
                expected_flags=expected,
                evidence=evidence,
            )
        )
    return scenarios


def init_store(root: Path, force: bool = False) -> dict[str, int]:
    config = load_config(root)
    ddir = data_dir(root)
    scenarios_path = ddir / "scenarios.json"
    if scenarios_path.exists() and not force:
        payload = json.loads(scenarios_path.read_text(encoding="utf-8"))
        return {
            "scenarios": len(payload),
            "clean": sum(1 for row in payload if row["clean"]),
            "defects": sum(1 for row in payload if not row["clean"]),
        }
    ddir.mkdir(parents=True, exist_ok=True)
    scenarios = generate_scenarios(config)
    scenarios_path.write_text(
        json.dumps([scenario.model_dump() for scenario in scenarios], indent=2),
        encoding="utf-8",
    )
    return {"scenarios": len(scenarios), "clean": config.clean_count, "defects": len(scenarios) - config.clean_count}


def load_scenarios(root: Path) -> list[Scenario]:
    init_store(root)
    return [
        Scenario.model_validate(row)
        for row in json.loads((data_dir(root) / "scenarios.json").read_text(encoding="utf-8"))
    ]
