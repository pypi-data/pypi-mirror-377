import numpy as np

from medevalkit.metrics import (
    BinaryClassificationMetrics,
    MulticlassClassificationMetrics,
    RegressionMetrics,
)


def test_binary_classification_metrics_basic_values():
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array([0.2, 0.9, 0.7, 0.1, 0.85])
    bcm = BinaryClassificationMetrics(y_true, y_prob, threshold=0.5)
    results = bcm.compute(bootstrap=False)

    expected_keys = {"auc", "auprc", "f1", "sensitivity", "specificity", "accuracy"}
    assert expected_keys.issubset(results.keys())
    assert 0.0 <= results["auc"] <= 1.0
    assert results["accuracy"] > 0.5


def test_multiclass_classification_metrics_structure():
    y_true = np.array([0, 1, 2, 1, 0, 2])
    y_prob = np.array(
        [
            [0.8, 0.1, 0.1],
            [0.2, 0.6, 0.2],
            [0.2, 0.1, 0.7],
            [0.2, 0.5, 0.3],
            [0.7, 0.2, 0.1],
            [0.1, 0.2, 0.7],
        ]
    )
    mcm = MulticlassClassificationMetrics(y_true, y_prob)
    results = mcm.compute(bootstrap=False)

    assert set(results.keys()) == {"auc (macro)", "precision (macro)", "recall (macro)"}
    assert all(0.0 <= value <= 1.0 for value in results.values())


def test_regression_metrics_basic_values():
    y_true = np.array([3.0, 4.0, 5.0, 6.0])
    y_pred = np.array([2.9, 4.1, 5.2, 5.8])
    rm = RegressionMetrics(y_true, y_pred)
    results = rm.compute(bootstrap=False)

    assert set(results.keys()) == {"mse", "mae"}
    assert results["mse"] >= 0.0
    assert results["mae"] >= 0.0
