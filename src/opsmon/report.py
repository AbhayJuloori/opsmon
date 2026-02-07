from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def _score_color(score: float) -> str:
    if score >= 85:
        return "#1d9f74"
    if score >= 70:
        return "#f1b11b"
    return "#d94d4d"


def render_html(report: Dict) -> str:
    cards_html = []
    for card in report.get("cards", []):
        color = _score_color(card["score"])
        findings = card.get("findings", [])
        findings_html = "".join(
            f"<li><strong>{f['severity'].upper()}</strong> [{f['code']}] {f['detail']}</li>"
            for f in findings
        )
        if not findings_html:
            findings_html = "<li>No issues detected</li>"

        cards_html.append(
            f"""
            <div class="card">
              <div class="card-header">
                <div class="title">{card['source']} · {card['metric']}</div>
                <div class="score" style="color:{color}">{card['score']}</div>
              </div>
              <ul>{findings_html}</ul>
            </div>
            """
        )

    return f"""
    <html>
    <head>
      <style>
        body {{ font-family: 'Georgia', serif; background: #f6f1ea; margin: 0; padding: 24px; }}
        h1 {{ margin: 0 0 8px 0; }}
        .summary {{ margin-bottom: 16px; color: #444; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
        .card {{ background: white; border-radius: 12px; padding: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
        .title {{ font-weight: bold; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        ul {{ margin: 0; padding-left: 18px; }}
      </style>
    </head>
    <body>
      <h1>Reliability Cards</h1>
      <div class="summary">Cards: {report['summary'].get('cards', 0)} · Avg Score: {report['summary'].get('avg_score', 0)}</div>
      <div class="grid">
        {''.join(cards_html)}
      </div>
    </body>
    </html>
    """


def write_reports(report: Dict, outdir: str) -> Dict:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "report.json"
    html_path = out / "report.html"

    json_path.write_text(json.dumps(report, indent=2))
    html_path.write_text(render_html(report))

    return {"json": str(json_path), "html": str(html_path)}
