from __future__ import annotations

from jinja2 import Template

from .models import ProjectConfig, ScenarioReport, SuiteSummary

TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ config.title }}</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f7f9fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5e6a76;
      --line: #d9e2ea;
      --accent: #227c8f;
      --good: #1b7f54;
      --warn: #a35d00;
      --bad: #a12836;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    @media (prefers-color-scheme: dark) {
      :root { --bg:#101418; --panel:#161d24; --ink:#edf2f7; --muted:#a6b1bd; --line:#2a3642; --accent:#63b3c4; }
    }
    body { margin:0; background:var(--bg); color:var(--ink); }
    main { width:min(1180px, calc(100vw - 40px)); margin:0 auto; padding:34px 0 48px; }
    header { display:flex; justify-content:space-between; align-items:end; gap:24px; margin-bottom:24px; }
    h1 { margin:0 0 8px; font-size:30px; line-height:1.1; letter-spacing:0; }
    p { margin:0; color:var(--muted); }
    .grid { display:grid; gap:14px; }
    .metrics { grid-template-columns:repeat(4,minmax(0,1fr)); margin-bottom:18px; }
    .metric, section { background:var(--panel); border:1px solid var(--line); border-radius:8px; }
    .metric { padding:18px; min-height:92px; }
    .metric span { color:var(--muted); font-size:13px; }
    .metric strong { display:block; font-size:28px; margin-top:8px; }
    section { padding:18px; margin-top:16px; }
    h2 { font-size:17px; margin:0 0 14px; }
    table { width:100%; border-collapse:collapse; font-size:14px; }
    th,td { padding:11px 9px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); font-weight:600; }
    .chip { display:inline-flex; align-items:center; min-height:24px; padding:0 9px; border-radius:999px; font-size:12px; font-weight:700; }
    .good { background:color-mix(in srgb, var(--good) 14%, transparent); color:var(--good); }
    .warn { background:color-mix(in srgb, var(--warn) 14%, transparent); color:var(--warn); }
    .bad { background:color-mix(in srgb, var(--bad) 14%, transparent); color:var(--bad); }
    .bars { display:grid; gap:12px; }
    .barrow { display:grid; grid-template-columns:210px 1fr 56px; gap:12px; align-items:center; }
    .bar { height:10px; border-radius:999px; background:var(--line); overflow:hidden; }
    .bar > i { display:block; height:100%; background:var(--accent); }
    .two { grid-template-columns:1.1fr .9fr; }
    code { overflow-wrap:anywhere; color:var(--accent); }
    @media (max-width:860px) { header,.two{display:block}.metrics{grid-template-columns:repeat(2,minmax(0,1fr));}.barrow{grid-template-columns:1fr;} }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>{{ config.title }}</h1>
        <p>{{ config.tagline }}</p>
      </div>
      <span class="chip {{ 'good' if summary.pass_gates else 'bad' }}">{{ 'PASS' if summary.pass_gates else 'FAIL' }}</span>
    </header>
    <div class="grid metrics">
      <div class="metric"><span>Scenarios</span><strong>{{ summary.scenario_count }}</strong></div>
      <div class="metric"><span>Recall</span><strong>{{ (summary.recall * 100) | round(1) }}%</strong></div>
      <div class="metric"><span>False Positive Rate</span><strong>{{ (summary.false_positive_rate * 100) | round(1) }}%</strong></div>
      <div class="metric"><span>Mean Score</span><strong>{{ (summary.mean_score * 100) | round(1) }}</strong></div>
    </div>
    <div class="grid two">
      <section>
        <h2>Metric Health</h2>
        <div class="bars">
        {% for metric, value in summary.metric_means.items() %}
          <div class="barrow">
            <code>{{ metric }}</code>
            <div class="bar"><i style="width: {{ (value * 100) | round(1) }}%"></i></div>
            <span>{{ (value * 100) | round(1) }}%</span>
          </div>
        {% endfor %}
        </div>
      </section>
      <section>
        <h2>Why This Exists</h2>
        <p>{{ config.problem }}</p>
        <p style="margin-top:14px">{{ config.wow }}</p>
      </section>
    </div>
    <section>
      <h2>Representative Findings</h2>
      <table>
        <tr><th>Scenario</th><th>Severity</th><th>Mode</th><th>Evidence</th></tr>
        {% for report in reports %}
          {% if report.findings %}
          {% set finding = report.findings[0] %}
          <tr>
            <td><code>{{ report.scenario_id }}</code></td>
            <td><span class="chip {{ 'bad' if finding.severity == 'critical' else 'warn' }}">{{ finding.severity }}</span></td>
            <td>{{ finding.mode }}</td>
            <td><code>{{ finding.evidence[0] }}</code></td>
          </tr>
          {% endif %}
        {% endfor %}
      </table>
    </section>
  </main>
</body>
</html>"""
)


def render_dashboard(config: ProjectConfig, summary: SuiteSummary, reports: list[ScenarioReport]) -> str:
    return TEMPLATE.render(config=config, summary=summary, reports=[report for report in reports if report.findings][:16])
