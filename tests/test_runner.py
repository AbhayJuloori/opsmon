import pandas as pd

from opsmon.config import load_config
from opsmon.runner import run_monitoring


def test_run_monitoring_smoke(tmp_path):
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=10, freq="D"),
            "source": ["alpha"] * 10,
            "metric": ["revenue"] * 10,
            "value": [100.0 + i for i in range(10)],
        }
    )

    cfg_path = tmp_path / "cfg.toml"
    cfg_path.write_text(
        """
[data]

timestamp_col = "timestamp"
source_col = "source"
metric_col = "metric"
value_col = "value"

[metrics.revenue]
range.min = 0
range.max = 10000
baseline_days = 5
recent_days = 3
psi_bins = 5
ks_alpha = 0.05
missingness_threshold = 0.02
max_gap_minutes = 1440
monotonic = false
"""
    )

    cfg = load_config(str(cfg_path))
    report = run_monitoring(data, cfg)
    assert report["summary"]["cards"] == 1
    assert len(report["cards"]) == 1
