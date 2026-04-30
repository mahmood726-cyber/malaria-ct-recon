"""Tests for statistical helpers."""
import math

import numpy as np
import pytest

from malaria_ct_recon import stats


def test_wilson_ci_known_values() -> None:
    low, high = stats.wilson_ci(50, 100)
    assert math.isclose(low, 0.4038, abs_tol=0.001)
    assert math.isclose(high, 0.5962, abs_tol=0.001)


def test_wilson_ci_zero_successes_floor_at_zero() -> None:
    low, high = stats.wilson_ci(0, 100)
    assert math.isclose(low, 0.0, abs_tol=1e-10) and high > 0.0


def test_wilson_ci_all_successes_ceil_at_one() -> None:
    low, high = stats.wilson_ci(100, 100)
    assert low < 1.0 and high == 1.0


def test_wilson_ci_zero_n_raises() -> None:
    with pytest.raises(ValueError):
        stats.wilson_ci(0, 0)


def test_bootstrap_ci_mean_returns_plausible_interval() -> None:
    rng = np.random.default_rng(42)
    data = rng.normal(loc=10.0, scale=2.0, size=500)
    low, high = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=1000, seed=123)
    assert low < 10.0 < high


def test_bootstrap_ci_deterministic_with_seed() -> None:
    data = np.arange(100, dtype=float)
    a = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=200, seed=1)
    b = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=200, seed=1)
    assert a == b
