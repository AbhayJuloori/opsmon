# Operational Monitoring & Data Reliability Framework (opsmon)

A pragmatic, extensible monitoring framework for multi-source time-series data. It detects anomalies, drift, and integrity issues that impact downstream analytics. The framework produces a **Reliability Card** per source/metric and a consolidated report for fast root-cause analysis.

## Explanation 
Think of this project as a **health check system for data**.

Imagine a school keeps track of daily attendance, cafeteria sales, and sports sign-ups from different systems. Sometimes the data is wrong: a day is missing, numbers jump too high, or a system quietly starts reporting different values. This project is a **watchdog** that looks at those numbers every day and says:

- "Something is missing."
- "This looks very different than usual."
- "These numbers are too big/small to be real."
- "A system is repeating the same timestamp."

It then gives each data source a **reliability score** (0–100) and a short list of **what went wrong**.

### Why it’s useful
People make decisions based on data—budgets, forecasts, performance reports. If the data is broken, those decisions are wrong. This project helps:
- Catch problems early (before bad data is used)
- Build trust in reports
- Find the root cause faster (it tells you *why* a score is low)

In one sentence: It’s a report card for data quality.

## Key Features
- **Range checks** and business-rule thresholds
- **Missingness diagnostics** (rate, streaks, and gaps)
- **Distribution shift** detection via KS test and PSI
- **Drift checks** between baseline and recent windows
- **Integrity checks** (duplicates, monotonicity, timestamp gaps)
- **Reliability Card** scoring with root-cause breadcrumbs
- **JSON + HTML reports** for quick review or downstream automation

## Project Layout
```
operational-monitoring-framework/
  src/opsmon/              # Framework core
  configs/                 # Example configs
  data/                    # Sample data
  scripts/                 # Helpers (generate data)
  tests/                   # Placeholder for unit tests
```

## Quickstart
1. Install locally:
```
pip install -e .
```

2. Generate sample data:
```
python scripts/generate_sample_data.py
```

3. Run monitoring:
```
opsmon monitor --input data/sample_timeseries.csv --config configs/example.toml --outdir out
```

## Configuration (TOML)
See `configs/example.toml` for a full example.

## Output
- `out/report.json` — Machine-readable report
- `out/report.html` — Human-friendly Reliability Card

## Example Output
You can preview a real run here:
- `examples/report.json`
- `examples/report.html`

## Notes
- The framework expects a **long-form** dataset with columns:
  `timestamp, source, metric, value`.
- You can add new checks by extending `opsmon/checks.py` and wiring them into `opsmon/runner.py`.

## License
MIT
