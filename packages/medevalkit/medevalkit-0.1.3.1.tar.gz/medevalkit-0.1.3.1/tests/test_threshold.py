import numpy as np

from medevalkit.threshold import (
    DecisionCurveAnalysis,
    MulticlassThresholdOptimizer,
    ThresholdAnalysis,
    ThresholdOptimizer,
)


def test_threshold_analysis_returns_metrics_for_requested_steps():
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_prob = np.array([0.1, 0.4, 0.75, 0.8, 0.2, 0.85, 0.3, 0.7])

    analysis = ThresholdAnalysis(y_true, y_prob)
    summary = analysis.compute(step=0.5)

    assert set(summary.keys()) == {1.0, 0.5, 0.0}
    for metrics in summary.values():
        assert {"sensitivity", "specificity", "accuracy"}.issubset(metrics.keys())


def test_decision_curve_analysis_dataframe_structure():
    y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 0, 1])
    y_prob = np.array([0.2, 0.8, 0.65, 0.3, 0.7, 0.1, 0.9, 0.4, 0.25, 0.6])

    dca = DecisionCurveAnalysis(y_true, y_prob)
    df = dca.compute()

    assert {"threshold", "net_benefit"}.issubset(df.columns)
    assert (df["threshold"] >= 0).all() and (df["threshold"] <= 1).all()


def test_threshold_optimizers_return_valid_thresholds():
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_prob = np.array([0.05, 0.35, 0.81, 0.76, 0.22, 0.88, 0.4, 0.7])

    optimizer = ThresholdOptimizer(y_true, y_prob)
    youden = optimizer.optimize_youden()
    f1 = optimizer.optimize_f1()

    assert 0 <= youden <= 1
    assert 0 <= f1 <= 1


def test_multiclass_threshold_optimizer_predicts_labels():
    y_true = np.array([0, 1, 2, 1, 0, 2])
    y_prob = np.array(
        [
            [0.7, 0.2, 0.1],
            [0.1, 0.8, 0.1],
            [0.1, 0.2, 0.7],
            [0.2, 0.6, 0.2],
            [0.8, 0.1, 0.1],
            [0.2, 0.2, 0.6],
        ]
    )

    mto = MulticlassThresholdOptimizer(y_true, y_prob)
    thresholds = mto.optimize_per_class(method="youden")
    predictions = mto.predict()

    assert thresholds.keys() == {0, 1, 2}
    assert predictions.shape == y_true.shape
    assert set(predictions).issubset({0, 1, 2})
