from pathlib import Path

import numpy as np

from iccore.data import DatasetCreate

from iclearn.data import Splits, Dataloader, DataloaderCreate

from .config import LinearDatasetConfig


class LinearDataset:
    def __init__(
        self,
        x=None,
        y=None,
        config: LinearDatasetConfig | None = None,
    ):
        if x is not None and y is not None:
            self.x, self.y = x, y
        elif config is not None:
            self.x = np.linspace(config.x_min, config.x_max, num=config.num_points)
            self.y = config.slope * self.x + config.y_intercept
            if config.noise_type == "normal":
                self.y += (
                    np.random.standard_normal(config.num_points)
                    * config.noise_amplitude
                )
        else:
            raise AttributeError("Missing x and y or a config for LinearDataset")

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


class LinearDataloader(Dataloader):
    def __init__(
        self,
        config: DataloaderCreate,
        path: Path | None = None,
    ):
        if config.dataset.fields:
            fields = config.dataset.fields
        else:
            fields = {}
        self.dataset = LinearDataset(
            config=LinearDatasetConfig.model_validate_strings(fields)
        )
        super().__init__(config, path)

    def load_dataset(self, dataset: DatasetCreate, name: str, splits: Splits):
        start_fraction = 0.0
        for split in splits.items:
            if name == split.name:
                num_samples = len(self.dataset)
                num_before = int(start_fraction * num_samples)
                end = num_before + int(split.fraction * num_samples)
                x, y = self.dataset[num_before:end]
                return LinearDataset(x, y)
            start_fraction += split.fraction

    def load_dataloader(self, dataset, batch_size, shuffle, sampler, num_workers):
        return LinearDataloaderView(dataset, batch_size)


class LinearDataloaderView:
    """
    A DataloaderIterator that deals with batched linear data.
    """

    def __init__(self, dataset, batch_size):
        self.dataset = dataset
        self.batch_size = batch_size
        if dataset is not None:
            length = int(len(dataset) / batch_size)
            if len(dataset) % batch_size:
                length += 1
            self.length = length
        else:
            self.length = 0

    def __len__(self):
        """
        Returns the number of batches
        """
        return self.length

    def __getitem__(self, batch_idx: int):
        """
        Returns the relevant batch, left over samples are in one final smaller batch.
        Not sure if this is the best implementation but I think it matches PyTorch's.
        """
        if batch_idx >= self.length:
            raise IndexError()

        dataset_id = batch_idx * self.batch_size
        if batch_idx == self.length - 1:
            return self.dataset[dataset_id:]

        return self.dataset[dataset_id : dataset_id + self.batch_size]
