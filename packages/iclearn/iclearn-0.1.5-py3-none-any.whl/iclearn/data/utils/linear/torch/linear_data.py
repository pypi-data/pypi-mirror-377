from pathlib import Path

import torch
from torch.utils.data import Dataset as TorchDataset, DataLoader as TorchDataLoader

from iccore.data import DatasetCreate

from iclearn.data import Splits, Dataloader, DataloaderCreate

from ..config import LinearDatasetConfig


class TorchLinearDataset(TorchDataset):
    def __init__(
        self,
        x: torch.Tensor | None = None,
        y: torch.Tensor | None = None,
        config: LinearDatasetConfig | None = None,
    ):
        if x is not None and y is not None:
            self.x, self.y = x, y
        elif config is not None:
            self.x = torch.linspace(
                start=config.x_min, end=config.x_max, steps=config.num_points
            )
            self.y = config.slope * self.x + config.y_intercept
            if config.noise_type == "normal":
                self.y += torch.randn(config.num_points) * config.noise_amplitude
            # Reshape
            self.x = self.x.view(config.num_points, 1)
            self.y = self.y.view(config.num_points, 1)
        else:
            raise AttributeError("Missing x and y or a config for LinearDataset")

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


class TorchLinearDataloader(Dataloader):
    def __init__(
        self,
        config: DataloaderCreate,
        path: Path | None = None,
    ):
        if config.dataset.fields:
            fields = config.dataset.fields
        else:
            fields = {}
        self.dataset = TorchLinearDataset(
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
                return TorchLinearDataset(x, y)
            start_fraction += split.fraction

    def load_dataloader(self, dataset, batch_size, shuffle, sampler, num_workers):
        return TorchDataLoader(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=num_workers,
        )
