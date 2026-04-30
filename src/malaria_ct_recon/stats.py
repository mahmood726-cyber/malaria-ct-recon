"""Statistical helpers — Wilson CI for proportions, bootstrap CI for any statistic."""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import norm


def wilson_ci(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (Wilson 1927)."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if not (0 <= successes <= n):
        raise ValueError(f"successes must be in [0, {n}], got {successes}")
    z = norm.ppf(1 - alpha / 2)
    phat = successes / n
    denom = 1 + z**2 / n
    centre = (phat + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_ci(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_resamples: int = 2000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> tuple[float, float]:
    """Percentile bootstrap CI for an arbitrary statistic."""
    rng = np.random.default_rng(seed)
    n = len(data)
    if n == 0:
        raise ValueError("data must be non-empty")
    samples = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        samples[i] = statistic(data[idx])
    return float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2))
