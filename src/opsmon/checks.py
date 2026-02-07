from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


def range_check(series: pd.Series, min_val: float | None, max_val: float | None) -> Dict:
    if series.empty:
        return {"violations": 0, "rate": 0.0}

    mask = pd.Series(False, index=series.index)
    if min_val is not None:
        mask |= series < min_val
    if max_val is not None:
        mask |= series > max_val

    violations = int(mask.sum())
    rate = float(violations / len(series))
    return {"violations": violations, "rate": rate}


def missingness_check(df: pd.DataFrame, ts_col: str, val_col: str, max_gap_minutes: int) -> Dict:
    if df.empty:
        return {"missing_rate": 0.0, "max_gap_minutes": 0, "nan_rate": 0.0}

    df_sorted = df.sort_values(ts_col)
    ts = pd.to_datetime(df_sorted[ts_col])
    gaps = ts.diff().dt.total_seconds().div(60).fillna(0)
    gap_violations = gaps > max_gap_minutes

    missing_rate = float(gap_violations.mean())
    max_gap = float(gaps.max())

    nan_rate = float(df_sorted[val_col].isna().mean())
    return {
        "missing_rate": missing_rate,
        "max_gap_minutes": max_gap,
        "nan_rate": nan_rate,
    }


def psi(a: np.ndarray, b: np.ndarray, bins: int = 10) -> float:
    if len(a) == 0 or len(b) == 0:
        return 0.0

    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(a, quantiles))
    if len(edges) < 3:
        edges = np.linspace(min(a.min(), b.min()), max(a.max(), b.max()), bins + 1)

    a_counts, _ = np.histogram(a, bins=edges)
    b_counts, _ = np.histogram(b, bins=edges)

    a_ratio = a_counts / max(a_counts.sum(), 1)
    b_ratio = b_counts / max(b_counts.sum(), 1)

    a_ratio = np.where(a_ratio == 0, 1e-6, a_ratio)
    b_ratio = np.where(b_ratio == 0, 1e-6, b_ratio)

    return float(np.sum((a_ratio - b_ratio) * np.log(a_ratio / b_ratio)))


def distribution_shift(baseline: pd.Series, recent: pd.Series, ks_alpha: float, psi_bins: int) -> Dict:
    if baseline.empty or recent.empty:
        return {"ks_pvalue": 1.0, "ks_shift": False, "psi": 0.0}

    ks_stat = ks_2samp(baseline, recent)
    ks_pvalue = float(ks_stat.pvalue)
    ks_shift = ks_pvalue < ks_alpha

    psi_score = psi(baseline.to_numpy(), recent.to_numpy(), bins=psi_bins)
    return {"ks_pvalue": ks_pvalue, "ks_shift": ks_shift, "psi": psi_score}


def integrity_check(df: pd.DataFrame, ts_col: str, val_col: str, monotonic: bool) -> Dict:
    if df.empty:
        return {"duplicates": 0, "monotonic_violations": 0}

    duplicates = int(df.duplicated(subset=[ts_col]).sum())

    monotonic_violations = 0
    if monotonic:
        s = df.sort_values(ts_col)[val_col]
        monotonic_violations = int((s.diff().fillna(0) < 0).sum())

    return {
        "duplicates": duplicates,
        "monotonic_violations": monotonic_violations,
    }
