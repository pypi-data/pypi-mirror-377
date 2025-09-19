import numpy as np
import pytest
from sklearn.datasets import make_classification, make_regression
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split

from medevalkit.evaluate import Evaluate


def test_evaluate_binary_classification_report_contains_metrics():
    X, y = make_classification(
        n_samples=400,
        n_features=10,
        n_informative=6,
        n_redundant=0,
        random_state=42,
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=0)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)

    evaluator = Evaluate(y_true=y_test, y_prob=y_prob, classification=True, threshold=0.5)
    report = evaluator.generate_report(bootstrap=False)

    assert "clf_metrics" in report
    assert "calib_metrics" in report
    assert "text_report" in report
    assert report["clf_metrics"]["accuracy"] > 0.6
    assert "brier_score" in report["calib_metrics"]


def test_evaluate_multiclass_classification_support():
    X, y = make_classification(
        n_samples=300,
        n_features=12,
        n_classes=3,
        n_informative=6,
        n_redundant=0,
        n_clusters_per_class=1,
        random_state=21,
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)

    model = LogisticRegression(max_iter=1000, multi_class="multinomial")
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)

    evaluator = Evaluate(y_true=y_test, y_prob=y_prob, classification=True)
    report = evaluator.generate_report(bootstrap=False)

    clf_metrics = report["clf_metrics"]
    assert "auc (macro)" in clf_metrics
    assert "precision (macro)" in clf_metrics
    assert "recall (macro)" in clf_metrics
    assert report["text_report"]


def test_evaluate_regression_report_contains_metrics():
    X, y = make_regression(n_samples=200, n_features=8, noise=0.5, random_state=123)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=12)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    evaluator = Evaluate(y_true=y_test, y_pred=y_pred, classification=False)
    report = evaluator.generate_report(bootstrap=False)

    assert "reg_metrics" in report
    assert "mse" in report["reg_metrics"]
    assert "text_report" in report


def test_evaluate_raises_when_probabilities_missing_for_classification():
    y_true = np.array([0, 1, 0, 1])
    with pytest.raises(ValueError) as excinfo:
        Evaluate(y_true=y_true, classification=True)
    assert "y_prob" in str(excinfo.value)
