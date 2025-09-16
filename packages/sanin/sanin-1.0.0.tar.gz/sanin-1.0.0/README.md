# sanin
<img width="102" height="102" alt="image" src="https://github.com/user-attachments/assets/127a9f7e-0d4a-4583-a3a9-ba601e747c28" />

A lightweight package for **injecting synthetic anomalies** into time series **without** requiring prior metadata.  
It internally estimates level, trend, and seasonality, then applies user-selected anomalies.

## Local Installation

```bash
pip install -e .
```

## Uso rápido

```python
import numpy as np, pandas as pd
from sanin import AnomalyInjector, AnomalyType

# Example series
t = np.arange(1000)
y = 100 + 0.01*t + 5*np.sin(2*np.pi*t/50) + np.random.normal(0, 1, size=len(t))
s = pd.Series(y, index=pd.date_range("2024-01-01", periods=len(t), freq="min"))

inj = AnomalyInjector(random_state=123)

# 1) Positive spikes in 5 points
y1, rep1, mask1 = inj.inject(s, AnomalyType.SPIKE, severity=1.0, n_points=5, return_mask=True)

# 2) Level shift starting at a point
y2, rep2, mask2 = inj.inject(s, AnomalyType.LEVEL_SHIFT, severity=2.0, return_mask=True)

# 3) Variance change within a window
y3, rep3, mask3 = inj.inject(s, AnomalyType.VARIANCE_CHANGE, severity=1.5, return_mask=True)
```

## Anomaly Types

- `SPIKE` (point anomaly, +)
- `DROP` (point anomaly, −)
- `LEVEL_SHIFT` (step change in level)
- `VARIANCE_CHANGE` (increased noise in a window)
- `TREND_DRIFT` (slope change)
- `SEASON_AMP_CHANGE` (seasonal amplitude change in a window)
- `FLATLINE` (sensor stuck at constant value)
- `MISSING` (segment with NaNs)
- `STUCK_HIGH`, `STUCK_LOW` (saturation at high/low value)
- `BLACKOUT` (zeroing or fixed value in a window)

Each injection also returns a **report** with affected indices and resolved parameters.

## Design
- No heavy dependencies: uses `numpy`/`pandas`.
- Internal decomposition:
  - level = robust median;
  - trend = moving average over ~10% of the length;
  - seasonality = mean by phase with period estimated via autocorrelation;
  - residual = observed - (level + trend + seasonality).
- Parameters have **robust** defaults derived from the series itself.

## Tests

```bash
pytest -q
```

## License

MIT
