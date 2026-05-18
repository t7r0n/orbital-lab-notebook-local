from __future__ import annotations

import json
import time
import zipfile
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from .dashboard import render_dashboard
from .fixtures import init_store, load_config, load_scenarios, output_dir
from .models import Finding, Scenario, ScenarioReport, SuiteSummary


class LocalHarness:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2]
        self.config = load_config(self.root)

    def evaluate(self, scenario: Scenario) -> ScenarioReport:
        values = scenario.signals
        mean_signal = sum(values.values()) / len(values)
        metric_deltas = {metric: round(max(0.0, 0.92 - value), 4) for metric, value in values.items()}
        flagged = scenario.risk >= 0.30 or any(delta > 0.12 for delta in metric_deltas.values())
        findings: list[Finding] = []
        if flagged:
            severity = "critical" if scenario.risk >= 0.45 else "review"
            weak_metrics = [metric for metric, delta in metric_deltas.items() if delta > 0.08]
            metric_phrase = ", ".join(weak_metrics[:3]) if weak_metrics else "risk model"
            findings.append(
                Finding(
                    scenario_id=scenario.id,
                    mode=scenario.mode,
                    severity=severity,
                    message=f"{self.config.project} flagged {scenario.mode} via {metric_phrase}.",
                    evidence=scenario.evidence,
                    metric_deltas=metric_deltas,
                )
            )
        score = max(0.0, min(1.0, mean_signal - (0.08 if flagged and not scenario.clean else 0.0)))
        return ScenarioReport(
            scenario_id=scenario.id,
            clean=scenario.clean,
            risk=scenario.risk,
            score=round(score, 4),
            flagged=flagged,
            finding_count=len(findings),
            findings=findings,
        )

    def evaluate_id(self, scenario_id: str) -> ScenarioReport:
        scenarios = load_scenarios(self.root)
        for scenario in scenarios:
            if scenario.id == scenario_id:
                return self.evaluate(scenario)
        raise KeyError(f"unknown scenario id: {scenario_id}")

    def run_suite(self) -> tuple[SuiteSummary, list[ScenarioReport]]:
        scenarios = load_scenarios(self.root)
        reports = [self.evaluate(scenario) for scenario in scenarios]
        defects = [report for report in reports if not report.clean]
        clean = [report for report in reports if report.clean]
        caught = sum(1 for report in defects if report.flagged)
        false_positive = sum(1 for report in clean if report.flagged)
        recall = caught / len(defects) if defects else 1.0
        fpr = false_positive / len(clean) if clean else 0.0
        metric_means: dict[str, float] = {}
        scenarios_by_id = {scenario.id: scenario for scenario in scenarios}
        for metric in self.config.metrics:
            metric_means[metric] = round(
                sum(scenarios_by_id[report.scenario_id].signals[metric] for report in reports) / len(reports),
                4,
            )
        top_modes = Counter(report.findings[0].mode for report in reports if report.findings)
        gates = {
            "recall_at_least_0_95": recall >= 0.95,
            "false_positive_rate_at_most_0_03": fpr <= 0.03,
            "all_metrics_present": set(metric_means) == set(self.config.metrics),
            "evidence_on_every_finding": all(f.evidence for report in reports for f in report.findings),
        }
        summary = SuiteSummary(
            project=self.config.project,
            company=self.config.company,
            scenario_count=len(reports),
            clean_count=len(clean),
            defect_count=len(defects),
            recall=round(recall, 4),
            false_positive_rate=round(fpr, 4),
            mean_score=round(sum(report.score for report in reports) / len(reports), 4),
            pass_gates=all(gates.values()),
            gate_details=gates,
            metric_means=metric_means,
            top_failure_modes=dict(top_modes.most_common()),
        )
        return summary, reports


def run_suite_and_write(root: Path) -> SuiteSummary:
    init_store(root)
    harness = LocalHarness(root)
    summary, reports = harness.run_suite()
    out = output_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    (out / "reports.json").write_text(
        json.dumps([report.model_dump() for report in reports], indent=2),
        encoding="utf-8",
    )
    (out / "dashboard.html").write_text(render_dashboard(harness.config, summary, reports), encoding="utf-8")
    (out / "evidence_pack.md").write_text(render_evidence_pack(harness.config, summary, reports), encoding="utf-8")
    return summary


def render_evidence_pack(config, summary: SuiteSummary, reports: list[ScenarioReport]) -> str:
    top = [report for report in reports if report.findings][:12]
    lines = [
        f"# {config.title} Evidence Pack",
        "",
        f"Company: {config.company}",
        f"Project: `{config.project}`",
        f"Pass gates: {summary.pass_gates}",
        f"Recall: {summary.recall}",
        f"False-positive rate: {summary.false_positive_rate}",
        "",
        "## Top Findings",
    ]
    for report in top:
        finding = report.findings[0]
        lines.append(f"- `{report.scenario_id}`: {finding.severity} / {finding.mode} — {finding.message}")
    lines.extend(["", "## Sources", *[f"- {source}" for source in config.sources]])
    return "\n".join(lines) + "\n"


def verify_outputs(root: Path) -> dict[str, bool]:
    out = output_dir(root)
    summary_path = out / "summary.json"
    reports_path = out / "reports.json"
    dashboard_path = out / "dashboard.html"
    evidence_path = out / "evidence_pack.md"
    if not summary_path.exists():
        run_suite_and_write(root)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    reports = json.loads(reports_path.read_text(encoding="utf-8"))
    return {
        "summary_exists": summary_path.exists(),
        "reports_exist": reports_path.exists() and len(reports) == summary["scenario_count"],
        "dashboard_exists": dashboard_path.exists() and "<html" in dashboard_path.read_text(encoding="utf-8"),
        "evidence_pack_exists": evidence_path.exists() and "Sources" in evidence_path.read_text(encoding="utf-8"),
        "quality_gates_pass": bool(summary["pass_gates"]),
    }


def benchmark(root: Path, iterations: int = 100) -> dict[str, float | bool | int]:
    harness = LocalHarness(root)
    scenarios = load_scenarios(root)
    start = time.perf_counter()
    for idx in range(iterations):
        harness.evaluate(scenarios[idx % len(scenarios)])
    elapsed_ms = (time.perf_counter() - start) * 1000
    per_case = elapsed_ms / iterations
    result = {"iterations": iterations, "p50_latency_ms": round(per_case, 4), "pass_gates": per_case < 5.0}
    out = output_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmark.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def export_demo_pack(root: Path) -> Path:
    run_suite_and_write(root)
    out = output_dir(root)
    pack = out / "demo-pack.zip"
    with zipfile.ZipFile(pack, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in ["summary.json", "reports.json", "dashboard.html", "evidence_pack.md", "benchmark.json"]:
            path = out / name
            if path.exists():
                zf.write(path, arcname=name)
    return pack


def jsonl_loop(lines: Iterable[str], root: Path) -> list[str]:
    harness = LocalHarness(root)
    responses: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        payload = json.loads(line)
        tool = payload.get("tool")
        args = payload.get("arguments", {})
        if tool in {"evaluate", "scenario.evaluate"}:
            result = harness.evaluate_id(args["scenario_id"]).model_dump()
        elif tool in {"suite", "suite.run"}:
            result = run_suite_and_write(root).model_dump()
        else:
            result = {"error": f"unknown tool: {tool}"}
        responses.append(json.dumps(result))
    return responses
