import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from medevalkit.plots import (
    plot_calibration_curve,
    plot_decision_curve,
    plot_multiclass_calibration,
    plot_multiclass_roc,
    plot_roc_curve,
    plot_threshold_metrics,
)


@pytest.fixture(autouse=True)
def no_show(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)
    yield
    plt.close("all")


class _DummyCalibration:
    def __init__(self):
        grid = np.linspace(0.1, 0.9, 5)
        self._curves = {
            0: {
                "brier_score": 0.1,
                "calibration_curve": {"prob_pred": grid, "prob_true": grid},
            },
            1: {
                "brier_score": 0.2,
                "calibration_curve": {"prob_pred": grid, "prob_true": grid ** 0.9},
            },
        }

    def one_vs_rest_curves(self):
        return self._curves


def _assert_figure_created():
    assert len(plt.get_fignums()) >= 1


def test_binary_plot_functions_execute_without_error():
    y_true = np.array([0, 1, 1, 0, 1, 0])
    y_prob = np.array([0.1, 0.8, 0.6, 0.3, 0.9, 0.2])

    plot_roc_curve(y_true, y_prob)
    _assert_figure_created()
    plt.close("all")

    plot_calibration_curve(y_true, y_prob, n_bins=3)
    _assert_figure_created()
    plt.close("all")

    thresholds = {
        0.0: {"sensitivity": 1.0, "specificity": 0.0},
        0.5: {"sensitivity": 0.8, "specificity": 0.7},
        1.0: {"sensitivity": 0.0, "specificity": 1.0},
    }
    plot_threshold_metrics(thresholds)
    _assert_figure_created()
    plt.close("all")

    dca_df = pd.DataFrame({
        "threshold": np.linspace(0.1, 0.9, 5),
        "net_benefit": np.linspace(0.05, 0.15, 5),
    })
    plot_decision_curve(dca_df)
    _assert_figure_created()
    plt.close("all")


def test_multiclass_plot_functions_execute_without_error():
    y_true = np.array([0, 1, 2, 1, 0])
    y_prob = np.array(
        [
            [0.7, 0.2, 0.1],
            [0.1, 0.7, 0.2],
            [0.1, 0.2, 0.7],
            [0.2, 0.6, 0.2],
            [0.8, 0.1, 0.1],
        ]
    )

    plot_multiclass_roc(y_true, y_prob)
    _assert_figure_created()
    plt.close("all")

    dummy_calibration = _DummyCalibration()
    plot_multiclass_calibration(dummy_calibration)
    _assert_figure_created()
    plt.close("all")
