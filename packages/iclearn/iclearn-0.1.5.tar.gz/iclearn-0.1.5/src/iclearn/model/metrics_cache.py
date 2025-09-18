"""
This module is for a metrics cache
"""

from typing import Callable
import time


class MetricsCache:
    """
    A cache of previously calculated metrics
    """

    def __init__(self, sync_func: Callable | None = None) -> None:
        """
        :param dict stage_results: Results generated at each stage
        :param dict batch_cuml_results: Results accumulated over a batch
        :param dict batch_last_results: Results at the end of a batch

        :param str active_stage: The current training stage
        :param int count: A batch counter
        :param Callable | None sync_func: A function to sync
        the cache in a distributed setting

        :param float batch_time: Records batch start and end time

        """
        self.stage_results: dict = {}
        self.batch_cuml_results: dict = {}
        self.batch_last_results: dict = {}

        self.active_stage: str = ""

        self.batch_count: int = 0

        self.sync_func = sync_func

        self.batch_time: float = 0.0

    def on_before_epochs(self):
        """
        This method is run before any epochs
        """
        self.stage_results = {}

    def on_epoch_start(self):
        """
        This method is run when an epoch starts
        """
        self._reset_for_stage("train")

    def on_epoch_end(self):
        """
        This method is run when an epoch finishes
        """
        self.update_stage_averages()
        if self.sync_func:
            self.stage_results = self.sync_func(self.stage_results)

    def on_validation_start(self):
        self.update_stage_averages()
        self._reset_for_stage("validation")

    def on_before_infer(self):
        self.stage_results = {}
        self._reset_for_stage("infer")

    def _reset_for_stage(self, stage: str):
        self.active_stage = stage
        self.batch_count = 0
        self.batch_cuml_results = {}
        self.batch_last_results = {}

        """
    def sync_results(self, env: Environment):
        if env.is_multigpu:
            self.stage_results = env.sync_dict(self.stage_results)
        """

    def on_batch_start(self):
        """
        This method is run at the start of a batch
        """
        self.batch_time = self._get_timing()

    def on_batch_item(self, key: str, value):
        if key not in self.batch_cuml_results:
            self.batch_cuml_results[key] = value
        else:
            current_value = self.batch_cuml_results[key]
            self.batch_cuml_results[key] = current_value + value
        self.batch_last_results[key] = value

    def update_stage_averages(self):
        if self.active_stage not in self.stage_results:
            self.stage_results[self.active_stage] = {}

        for metric_type, value in self.batch_cuml_results.items():
            batch_average = value / self.batch_count
            if metric_type in self.stage_results[self.active_stage]:
                self.stage_results[self.active_stage][metric_type].append(batch_average)
            else:
                self.stage_results[self.active_stage][metric_type] = [batch_average]
        if "time" in self.batch_last_results:
            if "time" in self.stage_results[self.active_stage]:
                self.stage_results[self.active_stage]["time"].append(
                    self.batch_last_results["time"]
                )
            else:
                self.stage_results[self.active_stage]["time"] = [
                    self.batch_last_results["time"]
                ]

    def on_batch_end(self):
        """
        This method is called at the end of a batch, when metrics
        have been calculated.
        """
        self.batch_time = self._get_timing(self.batch_time)

        if "time" in self.batch_last_results:
            self.batch_last_results["time"].append(self.batch_time)
        else:
            self.batch_last_results["time"] = [self.batch_time]

        self.batch_count += 1

    def _get_timing(self, start_time=None):
        """
        Function to measure elapsed time
        """

        if start_time:
            return time.time() - start_time
        return time.time()
