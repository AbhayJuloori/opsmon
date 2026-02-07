from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import tomllib


@dataclass
class RangeRule:
    min: Optional[float]
    max: Optional[float]


@dataclass
class MetricConfig:
    name: str
    range: RangeRule
    baseline_days: int
    recent_days: int
    psi_bins: int
    ks_alpha: float
    missingness_threshold: float
    max_gap_minutes: int
    monotonic: bool


@dataclass
class Config:
    timestamp_col: str
    source_col: str
    metric_col: str
    value_col: str
    metrics: Dict[str, MetricConfig]


def load_config(path: str) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    data = raw.get("data", {})
    timestamp_col = data.get("timestamp_col", "timestamp")
    source_col = data.get("source_col", "source")
    metric_col = data.get("metric_col", "metric")
    value_col = data.get("value_col", "value")

    metrics_cfg = {}
    for name, cfg in raw.get("metrics", {}).items():
        range_cfg = cfg.get("range", {})
        metrics_cfg[name] = MetricConfig(
            name=name,
            range=RangeRule(min=range_cfg.get("min"), max=range_cfg.get("max")),
            baseline_days=int(cfg.get("baseline_days", 30)),
            recent_days=int(cfg.get("recent_days", 7)),
            psi_bins=int(cfg.get("psi_bins", 10)),
            ks_alpha=float(cfg.get("ks_alpha", 0.05)),
            missingness_threshold=float(cfg.get("missingness_threshold", 0.02)),
            max_gap_minutes=int(cfg.get("max_gap_minutes", 60)),
            monotonic=bool(cfg.get("monotonic", False)),
        )

    return Config(
        timestamp_col=timestamp_col,
        source_col=source_col,
        metric_col=metric_col,
        value_col=value_col,
        metrics=metrics_cfg,
    )
