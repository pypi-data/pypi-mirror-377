import numpy as np
import pandas as pd
from sanin import AnomalyInjector, AnomalyType

def make_series(n=500, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    season = 10*np.sin(2*np.pi*t/50)
    trend = 0.02*t
    y = 100 + trend + season + rng.normal(0, 1, n)
    return pd.Series(y)

def test_spike():
    s = make_series()
    inj = AnomalyInjector(random_state=42)
    y2, rep, mask = inj.inject(s, AnomalyType.SPIKE, n_points=3, return_mask=True)
    assert mask.sum() == 3

def test_level_shift():
    s = make_series()
    inj = AnomalyInjector(random_state=42)
    y2, rep, mask = inj.inject(s, AnomalyType.LEVEL_SHIFT, severity=1.5, return_mask=True)
    assert mask.sum() > 0
