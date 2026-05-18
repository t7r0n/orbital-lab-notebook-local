from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class ProjectConfig(BaseModel):
    repo: str
    package: str
    cli: str
    company: str
    title: str
    tagline: str
    problem: str
    project: str
    plan_slug: str
    scenario: str
    fixture_count: int
    clean_count: int
    metrics: list[str]
    failure_modes: list[str]
    wow: str
    sources: list[str]


class Scenario(BaseModel):
    id: str
    kind: str
    clean: bool
    risk: float = Field(ge=0, le=1)
    mode: str
    signals: dict[str, float]
    expected_flags: list[str]
    evidence: list[str]


class Finding(BaseModel):
    scenario_id: str
    mode: str
    severity: str
    message: str
    evidence: list[str]
    metric_deltas: dict[str, float]


class ScenarioReport(BaseModel):
    scenario_id: str
    clean: bool
    risk: float
    score: float
    flagged: bool
    finding_count: int
    findings: list[Finding]


class SuiteSummary(BaseModel):
    project: str
    company: str
    scenario_count: int
    clean_count: int
    defect_count: int
    recall: float
    false_positive_rate: float
    mean_score: float
    pass_gates: bool
    gate_details: dict[str, bool]
    metric_means: dict[str, float]
    top_failure_modes: dict[str, int]
