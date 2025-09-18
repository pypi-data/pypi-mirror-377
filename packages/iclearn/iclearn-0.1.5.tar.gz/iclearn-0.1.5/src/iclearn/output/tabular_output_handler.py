"""
This module supports the generation of tabular output
"""

import logging
from pathlib import Path
import csv

from iclearn.model import MetricsCache
from .output_handler import OutputHandler

logger = logging.getLogger(__name__)


class TabularMetricsOutputHandler(OutputHandler):
    """
    Outputs loss/time results in a CSV format.
    """

    def __init__(self, result_dir: Path, filename: str = "tabular_metrics.csv"):
        """
        Create the lists that store the CSV information.
        """
        super().__init__(result_dir)

        # Path to the .csv
        self.path_to_file = result_dir / filename

    def on_before_epochs(self, num_epochs, _):
        """
        This method runs before any epochs begin.

        The CSV is created and opened here as
        training is just about to begin.
        """
        super().on_before_epochs(num_epochs, _)

        self.f = open(self.path_to_file.__str__(), "w", newline="")

        header = ["Epoch", "Stage", "Batch", "Batch Loss", "Time Taken (s)"]

        writer = csv.writer(self.f)
        writer.writerow(header)
        self.f.flush()

    def on_batch_end(self, metrics: MetricsCache):
        """
        This method is called at the end of a batch.

        Records each batch's loss and outputs relevant
        information to the CSV.
        """
        super().on_batch_end(metrics)

        if self.current_stage != "inference":
            loss = metrics.batch_last_results["loss"]
            writer = csv.writer(self.f)
            writer.writerow(
                [
                    self.epoch_count,
                    self.current_stage,
                    self.batch_count,
                    loss,
                    metrics.batch_time,
                ]
            )
            self.f.flush()

    def on_after_epochs(self):
        """
        This method runs after all epochs have finished.

        This method closes the open CSV file.
        """
        super().on_after_epochs()

        self.f.close()
