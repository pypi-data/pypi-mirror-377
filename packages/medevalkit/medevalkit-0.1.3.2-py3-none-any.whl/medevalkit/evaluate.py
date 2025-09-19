"""High-level evaluators for model predictions."""

from __future__ import annotations

import copy
from typing import Optional, Sequence

import numpy as np
from numpy.typing import ArrayLike
import pandas as pd

from .metrics import (
    BinaryClassificationMetrics,
    MulticlassClassificationMetrics,
    RegressionMetrics,
)
from .calibration import BinaryCalibration, MulticlassCalibration
from .simulation import PopulationSimulator


def _to_numpy(array: ArrayLike) -> np.ndarray:
    """Convert arbitrary array-like input to a NumPy array."""
    if isinstance(array, (pd.Series, pd.DataFrame)):
        return array.to_numpy()
    return np.asarray(array)


class Evaluate:
    """Evaluate predictions for classification or regression tasks."""

    def __init__(
        self,
        y: ArrayLike,
        y_prob: Optional[ArrayLike] = None,
        y_pred: Optional[ArrayLike] = None,
        classification: bool = True,
        threshold: float = 0.5,
    ) -> None:
        self.y_true = _to_numpy(y)
        if self.y_true.ndim != 1:
            raise ValueError("y_true must be a one-dimensional array")

        self.threshold = threshold
        self.classification = classification
        self.results: Optional[dict] = None

        if classification:
            if y_prob is None:
                raise ValueError("y_prob must be provided for classification tasks")
            prob_array = self._prepare_probabilities(y_prob)
            if prob_array.shape[0] != self.y_true.shape[0]:
                raise ValueError("y_true and y_prob must have the same number of samples")

            self.y_pred_prob = prob_array
            self.n_classes = prob_array.shape[1]

            if self.n_classes == 2:
                positive_prob = prob_array[:, 1]
                self.y_pred = (positive_prob >= threshold).astype(int)
            else:
                self.y_pred = np.argmax(prob_array, axis=1)
        else:
            if y_pred is None:
                raise ValueError("y_pred must be provided for regression tasks")
            pred_array = _to_numpy(y_pred)
            if pred_array.shape[0] != self.y_true.shape[0]:
                raise ValueError("y_true and y_pred must have the same number of samples")

            self.y_pred = pred_array
            self.y_pred_prob = None
            self.n_classes = 0

    @staticmethod
    def _prepare_probabilities(y_prob: ArrayLike) -> np.ndarray:
        """Ensure probability inputs are formatted as a 2D NumPy array."""
        prob_array = _to_numpy(y_prob)
        if prob_array.ndim == 1:
            if np.any((prob_array < 0) | (prob_array > 1)):
                raise ValueError("Probabilities must be between 0 and 1")
            prob_array = np.column_stack([1 - prob_array, prob_array])
        elif prob_array.ndim == 2:
            if np.any((prob_array < 0) | (prob_array > 1)):
                raise ValueError("Probabilities must be between 0 and 1")
        else:
            raise ValueError("y_prob must be a 1D or 2D array-like object")
        return prob_array.astype(float)

    @staticmethod
    def try_round(value, digits: int):
        try:
            return round(value, digits)
        except Exception:
            return value

    def _normalize_indices(self, indices: Optional[Sequence[int]]) -> np.ndarray:
        if indices is None:
            return np.arange(self.y_true.shape[0], dtype=int)
        return _to_numpy(indices).astype(int)

    def construct_text_report(self, metrics: dict, bootstrap: bool, n_resamples: int) -> dict:
        metrics_with_ci = copy.deepcopy(metrics)

        for metric_category, metric_dict in metrics.items():
            metric_names_with_ci = {
                key.replace("_upper", "").replace("_lower", "")
                for key in metric_dict
                if key.endswith("_upper") or key.endswith("_lower")
            }

            for metric_name in metric_names_with_ci:
                val = np.round(metric_dict[metric_name], 3)
                upper = np.round(metric_dict[f"{metric_name}_upper"], 3)
                lower = np.round(metric_dict[f"{metric_name}_lower"], 3)
                metrics_with_ci[metric_category][metric_name] = f"{val} (95% CI {lower}-{upper})"
                metrics_with_ci[metric_category].pop(f"{metric_name}_upper", None)
                metrics_with_ci[metric_category].pop(f"{metric_name}_lower", None)

        clf_metrics = metrics_with_ci.get("clf_metrics", {"Not Applicable": np.nan})
        calib_metrics = metrics_with_ci.get("calib_metrics", {"Not Applicable": np.nan})
        reg_metrics = metrics_with_ci.get("reg_metrics", {"Not Applicable": np.nan})

        report = (
            "==== Report ====\n"
            f"Bootstrap: {bootstrap}\n"
            f"Resamples: {n_resamples}\n\n"
            "-- Classification Metrics --\n"
            + "\n".join(
                f"{key}: {self.try_round(value, 3)}" for key, value in clf_metrics.items()
            )
            + "\n\n-- Calibration Metrics --\n"
            + "\n".join(
                f"{key}: {self.try_round(value, 3)}"
                for key, value in calib_metrics.items()
                if "calibration_curve" not in key
            )
            + "\n\n-- Regression Metrics --\n"
            + "\n".join(
                f"{key}: {self.try_round(value, 3)}" for key, value in reg_metrics.items()
            )
        )

        return {"text_report": report}

    def generate_report(
        self,
        indices: Optional[Sequence[int]] = None,
        multiclass_method: str = "ovr",
        calibration_bins: int = 10,
        bootstrap: bool = True,
        n_resamples: int = 1000,
        **kwargs,
    ) -> dict:
        indices_array = self._normalize_indices(indices)

        clf_metrics = {}
        calib_metrics = {}
        reg_metrics = {}

        if self.classification:
            if self.n_classes > 2:
                subset_prob = self.y_pred_prob[indices_array, :]
                subset_true = self.y_true[indices_array]
                clf_metrics = MulticlassClassificationMetrics(subset_true, subset_prob).compute(
                    bootstrap=bootstrap,
                    n_resamples=n_resamples,
                    **kwargs,
                )
                mcc = MulticlassCalibration(subset_true, subset_prob, n_bins=calibration_bins)
                if multiclass_method == "ovr":
                    ovr_calib = mcc.one_vs_rest_curves(
                        bootstrap=bootstrap,
                        n_resamples=n_resamples,
                        **kwargs,
                    )
                    for class_label, class_metrics in ovr_calib.items():
                        for key, value in class_metrics.items():
                            calib_metrics[f"{class_label}_{key}"] = value
                elif multiclass_method == "ece":
                    calib_metrics = mcc.expected_calibration_error(
                        bootstrap=bootstrap,
                        n_resamples=n_resamples,
                        **kwargs,
                    )
                else:
                    raise ValueError(
                        "Parameter `multiclass_method` must be one of ['ovr','ece']"
                    )
            else:
                positive_prob = self.y_pred_prob[indices_array, 1]
                subset_true = self.y_true[indices_array]
                clf_metrics = BinaryClassificationMetrics(
                    subset_true,
                    positive_prob,
                    threshold=self.threshold,
                ).compute(bootstrap=bootstrap, n_resamples=n_resamples, **kwargs)
                calib_metrics = BinaryCalibration(
                    subset_true,
                    positive_prob,
                    n_bins=calibration_bins,
                ).compute(bootstrap=bootstrap, n_resamples=n_resamples, **kwargs)

            output = {"clf_metrics": clf_metrics, "calib_metrics": calib_metrics}
        else:
            subset_true = self.y_true[indices_array]
            subset_pred = self.y_pred[indices_array]
            reg_metrics = RegressionMetrics(subset_true, subset_pred).compute(
                bootstrap=bootstrap,
                n_resamples=n_resamples,
                **kwargs,
            )
            output = {"reg_metrics": reg_metrics}

        report = self.construct_text_report(output, bootstrap, n_resamples)
        output.update(report)
        self.results = output
        return output


class EvaluateWithSimulation(Evaluate):
    """Evaluate predictions under varying outcome incidence via simulation."""

    def __init__(self, y: ArrayLike, y_prob: ArrayLike, threshold: float = 0.5) -> None:
        super().__init__(
            y=y,
            y_prob=y_prob,
            classification=True,
            threshold=threshold,
        )
        if self.n_classes != 2:
            raise ValueError("EvaluateWithSimulation currently supports binary classification only")
        self.results = None

    def run_simulation(
        self,
        incidence_rate_list: Optional[Sequence[float]] = None,
        calibration_bins: int = 10,
        bootstrap: bool = True,
        n_resamples: int = 1000,
        random_state: int = 1,
    ) -> dict:
        if incidence_rate_list is None:
            incidence_rate_list = [
                0.01,
                0.05,
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                0.95,
                0.99,
            ]

        simulator = PopulationSimulator(self.y_true, n_resamples, random_state)
        self.sim_dict = simulator.simulate(list(incidence_rate_list))
        self.sim_results = {}

        for incidence, indices in self.sim_dict.items():
            metrics = self.generate_report(
                indices=indices,
                calibration_bins=calibration_bins,
                bootstrap=bootstrap,
                n_resamples=n_resamples,
            )

            combined_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, dict):
                    combined_metrics.update(value)
                else:
                    combined_metrics[key] = value

            summary = {}
            for metric_name, metric_value in combined_metrics.items():
                if any(token in metric_name for token in ("upper", "lower", "text", "curve")):
                    continue
                values = [metric_value]
                mean_val = np.mean(values)
                ci_low, ci_high = np.percentile(values, [2.5, 97.5])
                summary[metric_name] = f"{mean_val:.3f} (95% CI {ci_low:.3f}-{ci_high:.3f})"

            self.sim_results[incidence] = summary

        return self.sim_results

    def generate_metrics(self) -> pd.DataFrame:
        output = pd.DataFrame.from_dict(self.sim_results, orient="index").T
        output.columns = [np.round(col, 2) for col in output.columns]
        return output
