from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .checks import (
    distribution_shift,
    integrity_check,
    missingness_check,
    range_check,
)
from .config import Config, MetricConfig


@dataclass
class Finding:
    code: str
    severity: str
    detail: str


def _score_findings(findings: List[Finding], metrics: Dict[str, float]) -> float:
    score = 100.0
    for f in findings:
        weight = metrics.get(f.code, 2.0)
        if f.severity == "high":
            score -= 12.0 * weight
        elif f.severity == "medium":
            score -= 6.0 * weight
        else:
            score -= 3.0 * weight
    return max(0.0, round(score, 2))


def _severity_from_rate(rate: float, high: float, medium: float) -> str:
    if rate >= high:
        return "high"
    if rate >= medium:
        return "medium"
    return "low"


def run_monitoring(df: pd.DataFrame, cfg: Config) -> Dict:
    ts_col = cfg.timestamp_col
    src_col = cfg.source_col
    metric_col = cfg.metric_col
    val_col = cfg.value_col

    df = df.copy()
    df[ts_col] = pd.to_datetime(df[ts_col])

    results = {
        "summary": {},
        "cards": [],
    }

    metric_weights = {
        "range": 1.0,
        "missing": 1.0,
        "shift": 1.2,
        "drift": 1.2,
        "integrity": 0.8,
    }

    total_cards = 0
    avg_score = []

    for (source, metric), g in df.groupby([src_col, metric_col]):
        if metric not in cfg.metrics:
            continue

        mcfg: MetricConfig = cfg.metrics[metric]
        max_ts = g[ts_col].max()
        recent_start = max_ts - pd.Timedelta(days=mcfg.recent_days)
        baseline_start = recent_start - pd.Timedelta(days=mcfg.baseline_days)

        recent = g[g[ts_col] >= recent_start]
        baseline = g[(g[ts_col] < recent_start) & (g[ts_col] >= baseline_start)]

        findings: List[Finding] = []

        rcheck = range_check(g[val_col], mcfg.range.min, mcfg.range.max)
        if rcheck["rate"] > 0:
            findings.append(
                Finding(
                    code="range",
                    severity=_severity_from_rate(rcheck["rate"], 0.05, 0.01),
                    detail=f"Range violations rate {rcheck['rate']:.2%}",
                )
            )

        mcheck = missingness_check(g, ts_col, val_col, mcfg.max_gap_minutes)
        missing_rate = max(mcheck["missing_rate"], mcheck["nan_rate"])
        if missing_rate > mcfg.missingness_threshold:
            findings.append(
                Finding(
                    code="missing",
                    severity=_severity_from_rate(missing_rate, 0.10, 0.03),
                    detail=f"Missingness rate {missing_rate:.2%}",
                )
            )

        dshift = distribution_shift(
            baseline[val_col].dropna(),
            recent[val_col].dropna(),
            mcfg.ks_alpha,
            mcfg.psi_bins,
        )
        if dshift["ks_shift"] or dshift["psi"] > 0.2:
            findings.append(
                Finding(
                    code="shift",
                    severity="medium" if dshift["psi"] < 0.4 else "high",
                    detail=f"Distribution shift (KS p={dshift['ks_pvalue']:.4f}, PSI={dshift['psi']:.3f})",
                )
            )

        drift_recent = recent[val_col].dropna()
        drift_base = baseline[val_col].dropna()
        if len(drift_recent) > 0 and len(drift_base) > 0:
            delta = float(drift_recent.mean() - drift_base.mean())
            rel = abs(delta) / (abs(drift_base.mean()) + 1e-9)
            if rel > 0.15:
                findings.append(
                    Finding(
                        code="drift",
                        severity="high" if rel > 0.3 else "medium",
                        detail=f"Mean drift {delta:.3f} ({rel:.1%})",
                    )
                )

        icheck = integrity_check(g, ts_col, val_col, mcfg.monotonic)
        if icheck["duplicates"] > 0 or icheck["monotonic_violations"] > 0:
            sev = "medium" if icheck["duplicates"] < 5 else "high"
            findings.append(
                Finding(
                    code="integrity",
                    severity=sev,
                    detail=f"Duplicates {icheck['duplicates']}, monotonic violations {icheck['monotonic_violations']}",
                )
            )

        score = _score_findings(findings, metric_weights)
        avg_score.append(score)
        total_cards += 1

        results["cards"].append(
            {
                "source": source,
                "metric": metric,
                "score": score,
                "findings": [f.__dict__ for f in findings],
                "stats": {
                    "range": rcheck,
                    "missingness": mcheck,
                    "shift": dshift,
                },
            }
        )

    results["summary"] = {
        "cards": total_cards,
        "avg_score": round(float(np.mean(avg_score)) if avg_score else 0.0, 2),
    }

    return results
