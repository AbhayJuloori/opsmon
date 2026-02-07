from __future__ import annotations

import numpy as np
import pandas as pd

np.random.seed(7)

sources = ["alpha", "beta", "gamma"]
metrics = ["revenue", "clicks", "active_users"]
start = pd.Timestamp("2025-09-01")
periods = 120
freq = "D"

rows = []
for source in sources:
    for metric in metrics:
        base = np.random.uniform(100, 200)
        trend = np.random.uniform(-0.2, 0.3)
        noise = np.random.uniform(5, 25)

        dates = pd.date_range(start, periods=periods, freq=freq)
        values = base + trend * np.arange(periods) + np.random.normal(0, noise, size=periods)

        if metric == "revenue":
            values *= 40
        if metric == "clicks":
            values *= 250
        if metric == "active_users":
            values *= 600

        # Inject drift for beta revenue
        if source == "beta" and metric == "revenue":
            values[-10:] *= 1.5

        # Inject missingness for gamma clicks
        if source == "gamma" and metric == "clicks":
            values[20:25] = np.nan
            dates = dates.delete([35, 36])
            values = np.delete(values, [35, 36])

        # Inject range violations
        if source == "alpha" and metric == "active_users":
            values[-3:] = values[-3:] * 3

        for d, v in zip(dates, values):
            rows.append({"timestamp": d, "source": source, "metric": metric, "value": float(v)})


df = pd.DataFrame(rows)

df.to_csv("data/sample_timeseries.csv", index=False)
print("Wrote data/sample_timeseries.csv")
