import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from medevalkit.evaluate import EvaluateWithSimulation


def test_simulation_generates_summary_for_requested_incidence_rates():
    X, y = make_classification(
        n_samples=500,
        n_features=10,
        n_informative=6,
        weights=[0.6, 0.4],
        random_state=123,
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=7)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    y_prob = clf.predict_proba(X_test)

    simulator = EvaluateWithSimulation(y_true=y_test, y_prob=y_prob, threshold=0.5)
    incidence_rates = [0.2, 0.5]
    results = simulator.run_simulation(
        incidence_rate_list=incidence_rates,
        calibration_bins=5,
        bootstrap=False,
        n_resamples=3,
        random_state=5,
    )

    for rate in incidence_rates:
        assert rate in results

    for summary in results.values():
        assert "auc" in summary or "accuracy" in summary

    metrics_df = simulator.generate_metrics()
    assert not metrics_df.empty
    assert any("auc" in idx for idx in metrics_df.index)
