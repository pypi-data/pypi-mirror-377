import numpy as np

from medevalkit.bootstrap import Bootstrapper


def _squared_error(yt, yp):
    return np.mean((yt - yp) ** 2)


def test_bootstrap_generates_expected_number_of_samples():
    y_true = np.array([0, 1, 1, 0, 1, 0], dtype=float)
    y_pred = np.array([0.1, 0.8, 0.7, 0.2, 0.9, 0.3], dtype=float)

    bs = Bootstrapper(n_resamples=50, random_state=7)
    scores = bs.bootstrap(_squared_error, y_true=y_true, y_pred=y_pred)

    assert len(scores) == 50
    assert all(np.isfinite(scores))


def test_bootstrap_ci_bounds_are_ordered_and_reproducible():
    y_true = np.linspace(0, 1, 20)
    noise = np.random.RandomState(0).normal(scale=0.05, size=20)
    y_pred = y_true + noise

    bs1 = Bootstrapper(n_resamples=100, random_state=42)
    bs2 = Bootstrapper(n_resamples=100, random_state=42)

    mean1, lower1, upper1 = bs1.bootstrap_ci(_squared_error, y_true=y_true, y_pred=y_pred)
    mean2, lower2, upper2 = bs2.bootstrap_ci(_squared_error, y_true=y_true, y_pred=y_pred)

    assert np.isclose(mean1, mean2)
    assert np.isclose(lower1, lower2)
    assert np.isclose(upper1, upper2)
    assert lower1 <= mean1 <= upper1
