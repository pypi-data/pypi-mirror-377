"""
Lightweight helpers for baseline decomposition without requiring heavy deps.
We estimate: level, trend, season (optional) and residual.
"""
from __future__ import annotations
import numpy as np

def _rolling_mean(x: np.ndarray, win: int) -> np.ndarray:
    win = max(1, int(win))
    if win <= 1:
        return x.copy()
    c = np.cumsum(np.insert(x, 0, 0.0))
    y = (c[win:] - c[:-win]) / float(win)
    # pad both sides to original length
    pad_left = win // 2
    pad_right = len(x) - len(y) - pad_left
    return np.pad(y, (pad_left, pad_right), mode="edge")

def _estimate_period(x: np.ndarray, max_period: int | None = None) -> int | None:
    """
    Estimate a dominant period using autocorrelation peak.
    Returns None if no strong peak is found.
    """
    n = len(x)
    if n < 8:
        return None
    if max_period is None:
        max_period = min(int(n // 2), 1000)
    x = x - np.nanmedian(x)
    # To be robust against NaNs, fill with median
    x = np.nan_to_num(x, nan=np.nanmedian(x))
    f = np.fft.rfft(x, n * 2)
    acf = np.fft.irfft(np.abs(f) ** 2)[:n]
    acf /= acf[0] if acf[0] != 0 else 1
    # Search for first strong local max beyond lag 2
    start = 2
    end = min(max_period, n - 2)
    if end <= start:
        return None
    candidate = None
    best_val = 0.0
    for lag in range(start, end):
        if acf[lag] > acf[lag - 1] and acf[lag] > acf[lag + 1]:
            if acf[lag] > best_val:
                best_val = acf[lag]
                candidate = lag
    # Require a minimum strength
    if candidate is not None and best_val >= 0.2:
        return int(candidate)
    return None

def decompose(x: np.ndarray) -> dict:
    """
    Return a dict with keys: level, trend, season, resid
    - level: median
    - trend: rolling mean over 1/10 of series (>=5)
    - season: mean seasonal pattern if a period is found; else zeros
    - resid: x - (level + trend + season)
    """
    n = len(x)
    if n == 0:
        raise ValueError("Empty series.")
    # replace NaNs for baseline estimation
    xm = np.nanmedian(x)
    x_filled = np.nan_to_num(x, nan=xm)
    level = np.full(n, xm, dtype=float)
    win = max(5, int(n / 10))
    trend = _rolling_mean(x_filled - xm, win)
    period = _estimate_period(x_filled)
    if period is None or period < 2:
        season = np.zeros(n, dtype=float)
    else:
        # seasonal mean by phase using autocorr-estimated period
        idx = np.arange(n) % period
        resid0 = x_filled - (level + trend)
        sums = np.bincount(idx, weights=resid0, minlength=period)
        counts = np.bincount(idx, minlength=period)
        counts[counts == 0] = 1
        means = sums / counts
        season = means[idx]
    baseline = level + trend + season
    resid = x_filled - baseline
    return {
        "level": level,
        "trend": trend,
        "season": season,
        "resid": resid,
        "period": period,
    }
