"""
This module supports output handling via ml flow
"""

import logging
import pickle
import statistics
from pathlib import Path

import mlflow

from .output_handler import OutputHandler

logger = logging.getLogger(__name__)


class MlFlowOutputHandler(OutputHandler):
    def __init__(self, result_dir: Path, experiment_name: str = "mlflow_outputs"):
        super().__init__(result_dir)
        self.experiment_name = experiment_name

    def on_before_epochs(self, num_epochs, _):
        super().on_before_epochs(num_epochs, _)
        if self.experiment_name:
            mlflow.set_experiment(self.experiment_name)

    def on_epoch_end(self, metrics):
        super().on_epoch_end(metrics)
        for outer_key, values in metrics.stage_results.items():
            for metric_key, metric_values in values.items():
                value = metric_values[self.epoch_count - 1]
                self.write_metrics(outer_key, metric_key, value)

    def save_model(self, model):
        """
        Write the model to the given path
        """

        mlflow.pytorch.log_model(
            model.model, artifact_path="pytorch-model", pickle_module=pickle
        )

    def write_metrics(self, outer_key, metric_key, value):
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        if isinstance(value, list):
            mlflow.log_metric(
                f"{outer_key}_{metric_key}_total",
                sum(value),
                step=self.epoch_count,
            )
            mlflow.log_metric(
                f"{outer_key}_{metric_key}_mean",
                statistics.mean(value),
                step=self.epoch_count,
            )
            mlflow.log_metric(
                f"{outer_key}_{metric_key}_median",
                statistics.median(value),
                step=self.epoch_count,
            )
            mlflow.log_metric(
                f"{outer_key}_{metric_key}_max",
                max(value),
                step=self.epoch_count,
            )
        else:
            mlflow.log_metric(f"{outer_key}_{metric_key}", value, step=self.epoch_count)
