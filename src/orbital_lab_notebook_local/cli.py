from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from .engine import LocalHarness, export_demo_pack, jsonl_loop, run_suite_and_write, verify_outputs
from .engine import benchmark as run_benchmark
from .fixtures import init_store, output_dir
from .models import project_root

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def init_demo(force: bool = False) -> None:
    console.print_json(json.dumps(init_store(project_root(), force=force)))


@app.command()
def evaluate(scenario_id: str, output: Path | None = None) -> None:
    report = LocalHarness(project_root()).evaluate_id(scenario_id)
    payload = report.model_dump()
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print_json(json.dumps(payload))


@app.command(name="run-suite")
def run_suite() -> None:
    console.print_json(run_suite_and_write(project_root()).model_dump_json())


@app.command()
def dashboard() -> None:
    summary = run_suite_and_write(project_root())
    console.print_json(json.dumps({"dashboard": str(output_dir(project_root()) / "dashboard.html"), "pass_gates": summary.pass_gates}))


@app.command()
def verify() -> None:
    checks = verify_outputs(project_root())
    console.print_json(json.dumps(checks))
    if not all(checks.values()):
        raise typer.Exit(1)


@app.command()
def benchmark(iterations: int = 100) -> None:
    console.print_json(json.dumps(run_benchmark(project_root(), iterations=iterations)))


@app.command(name="export-demo-pack")
def export_demo_pack_command() -> None:
    console.print_json(json.dumps({"demo_pack": str(export_demo_pack(project_root()))}))


@app.command(name="tool-loop")
def tool_loop() -> None:
    for line in jsonl_loop(sys.stdin, project_root()):
        print(line)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
