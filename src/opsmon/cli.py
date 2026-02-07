from __future__ import annotations

import argparse
import pandas as pd

from .config import load_config
from .runner import run_monitoring
from .report import write_reports


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Operational Monitoring & Data Reliability Framework")
    sub = p.add_subparsers(dest="command", required=True)

    m = sub.add_parser("monitor", help="Run monitoring on an input dataset")
    m.add_argument("--input", required=True, help="Input CSV path")
    m.add_argument("--config", required=True, help="Config TOML path")
    m.add_argument("--outdir", required=True, help="Output directory")

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "monitor":
        cfg = load_config(args.config)
        df = pd.read_csv(args.input)
        report = run_monitoring(df, cfg)
        paths = write_reports(report, args.outdir)
        print(f"Report written: {paths['json']}")
        print(f"HTML written: {paths['html']}")


if __name__ == "__main__":
    main()
