from __future__ import annotations

import json
import subprocess
import sys

from orbital_lab_notebook_local.engine import (
    LocalHarness,
    benchmark,
    export_demo_pack,
    jsonl_loop,
    run_suite_and_write,
    verify_outputs,
)
from orbital_lab_notebook_local.fixtures import init_store, load_config, load_scenarios


def test_fixture_scale(tmp_path):
    config = load_config(__import__("pathlib").Path.cwd())
    counts = init_store(tmp_path, force=True)
    assert counts["scenarios"] == config.fixture_count
    assert counts["clean"] == config.clean_count


def test_suite_outputs_and_quality_gates(tmp_path):
    init_store(tmp_path, force=True)
    summary = run_suite_and_write(tmp_path)
    assert summary.recall >= 0.95
    assert summary.false_positive_rate <= 0.03
    assert summary.pass_gates
    assert all(verify_outputs(tmp_path).values())
    assert export_demo_pack(tmp_path).exists()


def test_defect_gets_evidence_backed_finding(tmp_path):
    config = load_config(__import__("pathlib").Path.cwd())
    init_store(tmp_path, force=True)
    scenarios = load_scenarios(tmp_path)
    defect = next(scenario for scenario in scenarios if not scenario.clean)
    report = LocalHarness(tmp_path).evaluate(defect)
    assert report.flagged
    assert report.findings
    assert report.findings[0].evidence
    assert report.findings[0].mode in config.failure_modes


def test_jsonl_tool_loop(tmp_path):
    init_store(tmp_path, force=True)
    defect = next(scenario for scenario in load_scenarios(tmp_path) if not scenario.clean)
    rows = jsonl_loop([json.dumps({"tool": "evaluate", "arguments": {"scenario_id": defect.id}})], tmp_path)
    payload = json.loads(rows[0])
    assert payload["flagged"]


def test_benchmark_and_cli_smoke():
    result = subprocess.run(
        [sys.executable, "-m", "orbital_lab_notebook_local.cli", "init-demo", "--force"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert '"scenarios"' in result.stdout
    assert benchmark(__import__("pathlib").Path.cwd(), iterations=5)["pass_gates"]
