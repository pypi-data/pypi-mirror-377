"""
This module supports output handling via tensorboard
"""

import logging
from pathlib import Path
import statistics

import torch
from torch.utils.tensorboard import SummaryWriter

from ..output_handler import OutputHandler

logger = logging.getLogger(__name__)


class TensorboardOutputHandler(OutputHandler):
    def __init__(self, result_dir: Path, tensorboard_dir: str = "tensorboard"):
        super().__init__(result_dir)
        # Path to the tensorboard output
        self.tensorboard_path = result_dir / tensorboard_dir
        self.writer = None

    def on_before_epochs(self, num_epochs, _):
        super().on_before_epochs(num_epochs, _)
        self.writer = SummaryWriter(self.tensorboard_path)

    def on_epoch_end(self, metrics):
        super().on_epoch_end(metrics)
        for outer_key, values in metrics.stage_results.items():
            for metric_key, metric_values in values.items():
                value = metric_values[self.epoch_count - 1]
                self.write_scalars(outer_key, metric_key, value)
        self.writer.flush()

    def on_after_epochs(self):
        super().on_after_epochs()
        self.writer.close()

    def save_model(self, model):
        torch.save(
            model.model,
            self.result_dir / "best_model.pt",
        )

    def write_scalars(self, outer_key, metric_key, value):
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        if isinstance(value, list):
            self.writer.add_scalar(
                f"{outer_key}_{metric_key}_total",
                sum(value),
                global_step=self.epoch_count,
            )
            self.writer.add_scalar(
                f"{outer_key}_{metric_key}_mean",
                statistics.mean(value),
                global_step=self.epoch_count,
            )
            self.writer.add_scalar(
                f"{outer_key}_{metric_key}_median",
                statistics.median(value),
                global_step=self.epoch_count,
            )
            self.writer.add_scalar(
                f"{outer_key}_{metric_key}_max",
                max(value),
                global_step=self.epoch_count,
            )
        else:
            self.writer.add_scalar(
                f"{outer_key}_{metric_key}", value, global_step=self.epoch_count
            )
