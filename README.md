# opsmon: Operational Monitoring & Data Reliability

`opsmon` is a lightweight monitoring framework for multi-source time-series data. It focuses on the kinds of failures that quietly break downstream analytics: missing values, range violations, drift, duplicate timestamps, abnormal jumps, and other integrity issues.

Instead of returning only a raw list of failed checks, the framework produces a **Reliability Card** per source and metric plus machine-readable JSON output for automation.

## Why this project exists

Most teams monitor infrastructure before they monitor the data itself. A pipeline can stay green while a source starts dropping rows, drifting away from historical behavior, or violating business rules. `opsmon` is designed to catch those data-quality failures early and make the root cause visible.

## What it checks

- **Range and business-rule checks** for impossible or out-of-bounds values
- **Missingness diagnostics** including rates, streaks, and timestamp gaps
- **Distribution shift** detection using KS tests and PSI
- **Drift checks** between baseline and recent windows
- **Integrity checks** for duplicates, monotonicity failures, and repeated timestamps
- **Reliability scoring** with short explanations of what drove the score down

## What you get

- `out/report.json` for machine-readable monitoring output
- `out/report.html` for a human-friendly Reliability Card
- Per-source and per-metric summaries that make it easier to triage problems quickly

## Quickstart

### 1. Install

```bash
pip install -e .
```

### 2. Generate sample data

```bash
python scripts/generate_sample_data.py
```

### 3. Run monitoring

```bash
opsmon monitor --input data/sample_timeseries.csv --config configs/example.toml --outdir out
```

## Configuration

`opsmon` expects a long-form dataset with columns like:

```text
timestamp, source, metric, value
```

See `configs/example.toml` for a complete configuration example, including thresholds, drift settings, and enabled checks.

## Project layout

```text
opsmon/
├── src/opsmon/    # Framework core
├── configs/       # Example configurations
├── data/          # Sample data
├── scripts/       # Sample-data generator and helpers
└── tests/         # Test suite
```

## Extending the framework

You can add new checks by extending the core monitoring logic in `src/opsmon/` and wiring those checks into the runner pipeline. The reporting layer is designed to keep both the machine-readable output and the Reliability Card aligned.

## Why it is useful in practice

This project is aimed at the layer between raw ingestion and downstream reporting or modeling. It helps teams:

- catch silent data failures before they affect dashboards or forecasts
- build trust in downstream analytics
- give operators a short explanation of what failed instead of a wall of raw metrics

## License

MIT
