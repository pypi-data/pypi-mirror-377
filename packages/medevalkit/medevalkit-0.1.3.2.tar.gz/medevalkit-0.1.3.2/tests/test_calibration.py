import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from medevalkit.calibration import BinaryCalibration, MulticlassCalibration


def test_binary_calibration_returns_curve_and_brier_score():
    rng = np.random.RandomState(0)
    y_true = rng.randint(0, 2, size=200)
    logits = rng.normal(size=200)
    y_prob = 1 / (1 + np.exp(-logits))

    calib = BinaryCalibration(y_true, y_prob, n_bins=5)
    metrics = calib.compute(bootstrap=False)

    assert "brier_score" in metrics
    prob_pred, prob_true = metrics["calibration_curve"]
    assert prob_pred.shape == prob_true.shape


def test_multiclass_calibration_outputs_expected_structures():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)

    mc = MulticlassCalibration(y_test, y_prob)
    ece = mc.expected_calibration_error(bootstrap=False)
    curves = mc.one_vs_rest_curves(bootstrap=False)

    assert "expected_calibration_error" in ece
    assert isinstance(curves, dict)
    for result in curves.values():
        assert "brier_score" in result
        curve = result["calibration_curve"]
        assert set(curve.keys()) == {"prob_pred", "prob_true"}
