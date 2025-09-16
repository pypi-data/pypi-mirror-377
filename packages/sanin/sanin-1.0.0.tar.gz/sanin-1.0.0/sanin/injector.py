from __future__ import annotations
import enum
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, Iterable

import numpy as np
import pandas as pd

from .detectors import decompose

class AnomalyType(str, enum.Enum):
    SPIKE = "spike"                 # impulse up or down at points
    DROP = "drop"                   # negative impulse(s)
    LEVEL_SHIFT = "level_shift"     # step change in mean
    VARIANCE_CHANGE = "variance_change"  # change noise scale in a window
    TREND_DRIFT = "trend_drift"     # slope change from a changepoint
    SEASON_AMP_CHANGE = "season_amp_change" # scale seasonal amplitude in window
    FLATLINE = "flatline"           # sensor stuck constant in a window
    MISSING = "missing"             # set NaNs in a window
    STUCK_HIGH = "stuck_high"       # saturate to high constant in window
    STUCK_LOW = "stuck_low"         # saturate to low constant in window
    BLACKOUT = "blackout"           # zero out (or baseline) a window

@dataclass
class InjectReport:
    indices: np.ndarray                 # indices affected
    params: Dict[str, Any]             # resolved params for reproducibility

class AnomalyInjector:
    """
    Inject synthetic anomalies into univariate time series without prior metadata.
    Minimal, dependency-light; auto-estimates baseline components internally.
    """
    def __init__(self, random_state: Optional[int] = None):
        self.rng = np.random.default_rng(random_state)

    def _as_ndarray(self, series: Iterable[float]) -> Tuple[np.ndarray, Optional[pd.Index]]:
        if isinstance(series, pd.Series):
            return series.values.astype(float), series.index
        arr = np.asarray(series, dtype=float)
        return arr, None

    def _return_like(self, base_like, values: np.ndarray) -> Any:
        if isinstance(base_like, pd.Series):
            out = pd.Series(values, index=base_like.index, name=base_like.name)
            return out
        return values

    def _pick_window(self, n: int, min_len: int, max_len: Optional[int] = None) -> Tuple[int, int]:
        if max_len is None:
            max_len = max(min_len, n // 5)
        L = int(self.rng.integers(min_len, max(max_len, min_len)+1))
        if L >= n:
            L = max(1, n//2)
        start = int(self.rng.integers(0, max(1, n - L)))
        end = start + L
        return start, end

    def inject(self,
               series: Iterable[float],
               kind: AnomalyType,
               severity: float = 1.0,
               n_points: int = 1,
               return_mask: bool = False,
               **kwargs) -> Tuple[Any, InjectReport, Optional[np.ndarray]]:
        """
        Inject an anomaly of a given kind.

        Parameters
        ----------
        series : array-like or pandas.Series
        kind : AnomalyType
        severity : float
            Generic intensity scaler (meaning varies by kind).
        n_points : int
            For point anomalies (SPIKE/DROP), how many points.
        return_mask : bool
            If True, also returns a boolean mask of affected indices.
        kwargs : dict
            Optional per-kind overrides:
             - SPIKE/DROP: {'scale': float}
             - LEVEL_SHIFT: {'offset': float, 'start': int}
             - VARIANCE_CHANGE: {'scale': float, 'start': int, 'end': int}
             - TREND_DRIFT: {'slope': float, 'start': int}
             - SEASON_AMP_CHANGE: {'mult': float, 'start': int, 'end': int}
             - FLATLINE: {'value': float, 'start': int, 'end': int}
             - MISSING: {'start': int, 'end': int}
             - STUCK_HIGH/LOW: {'value': float, 'start': int, 'end': int}
             - BLACKOUT: {'value': float, 'start': int, 'end': int}
        Returns
        -------
        (series_like, InjectReport, mask_or_none)
        """
        base_like = series
        x, idx = self._as_ndarray(series)
        n = len(x)
        if n < 2:
            raise ValueError("Series too short.")

        comps = decompose(x)
        level = comps["level"]
        trend = comps["trend"]
        season = comps["season"]
        resid = comps["resid"]
        baseline = level + trend + season

        y = x.copy()
        mask = np.zeros(n, dtype=bool)
        params = {}

        if kind in (AnomalyType.SPIKE, AnomalyType.DROP):
            # scale default: fraction of robust scale of residuals
            robust_scale = np.nanmedian(np.abs(resid - np.nanmedian(resid))) + 1e-9
            scale = kwargs.get("scale", severity * 5 * robust_scale)
            signs = 1 if kind == AnomalyType.SPIKE else -1
            positions = self.rng.choice(n, size=min(n_points, n), replace=False)
            for p in positions:
                y[p] += signs * scale
            mask[positions] = True
            params = {"scale": float(scale), "positions": positions.tolist(), "kind": kind.value}

        elif kind == AnomalyType.LEVEL_SHIFT:
            start = kwargs.get("start", int(self.rng.integers(n//4, 3*n//4)))
            # offset default ~ robust std of baseline
            robust_scale = np.nanmedian(np.abs(baseline - np.nanmedian(baseline))) + 1e-9
            offset = kwargs.get("offset", severity * 2.5 * robust_scale * (1 if self.rng.random() < 0.5 else -1))
            y[start:] += offset
            mask[start:] = True
            params = {"start": int(start), "offset": float(offset)}

        elif kind == AnomalyType.VARIANCE_CHANGE:
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(5, n//20))
            scale = kwargs.get("scale", max(1.0, 1.0 + severity * 2.0))
            noise = resid[start:end]
            if noise.std() == 0:
                noise = noise + self.rng.normal(0, 1e-6, size=noise.shape)
            mean_noise = noise.mean()
            amplified = mean_noise + (noise - mean_noise) * scale
            delta = amplified - noise
            y[start:end] += delta
            mask[start:end] = True
            params = {"start": int(start), "end": int(end), "scale": float(scale)}

        elif kind == AnomalyType.TREND_DRIFT:
            start = kwargs.get("start", int(self.rng.integers(n//5, 4*n//5)))
            # slope default relative to robust scale per 100 steps
            robust_scale = np.nanmedian(np.abs(baseline - np.nanmedian(baseline))) + 1e-9
            slope = kwargs.get("slope", severity * (2.0 * robust_scale) / max(100, n//3))
            t = np.arange(n - start)
            y[start:] += slope * t
            mask[start:] = True
            params = {"start": int(start), "slope_per_step": float(slope)}

        elif kind == AnomalyType.SEASON_AMP_CHANGE:
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(10, n//10))
            mult = kwargs.get("mult", max(0.2, 1.0 + severity))
            # scale only the seasonal component in [start:end]
            delta = (season[start:end]) * (mult - 1.0)
            y[start:end] += delta
            mask[start:end] = True
            params = {"start": int(start), "end": int(end), "mult": float(mult)}

        elif kind == AnomalyType.FLATLINE:
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(5, n//20))
            value = kwargs.get("value", float(np.nanmedian(y[start:end])))
            y[start:end] = value
            mask[start:end] = True
            params = {"start": int(start), "end": int(end), "value": float(value)}

        elif kind == AnomalyType.MISSING:
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(3, n//30))
            y[start:end] = np.nan
            mask[start:end] = True
            params = {"start": int(start), "end": int(end)}

        elif kind in (AnomalyType.STUCK_HIGH, AnomalyType.STUCK_LOW):
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(5, n//20))
            if kind == AnomalyType.STUCK_HIGH:
                default = float(np.nanpercentile(baseline, 95))
            else:
                default = float(np.nanpercentile(baseline, 5))
            value = kwargs.get("value", default)
            y[start:end] = value
            mask[start:end] = True
            params = {"start": int(start), "end": int(end), "value": float(value)}

        elif kind == AnomalyType.BLACKOUT:
            start, end = kwargs.get("start"), kwargs.get("end")
            if start is None or end is None:
                start, end = self._pick_window(n, min_len=max(5, n//20))
            value = kwargs.get("value", 0.0)
            y[start:end] = value
            mask[start:end] = True
            params = {"start": int(start), "end": int(end), "value": float(value)}

        else:
            raise ValueError(f"Unsupported kind: {kind}")

        report = InjectReport(indices=np.where(mask)[0], params=params)
        out = self._return_like(series, y)
        if return_mask:
            return out, report, mask
        return out, report, None
