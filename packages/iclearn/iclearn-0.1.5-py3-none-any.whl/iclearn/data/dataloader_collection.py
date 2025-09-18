from pathlib import Path

from iclearn.environment import has_pytorch

from .dataloader import DataloaderCreate, Dataloader


def load_dataloader(config: DataloaderCreate, data_dir: Path) -> Dataloader | None:
    """
    Return a suitable dataloader based on the provided
    config.

    If none is found return none - error handling is left
    to the caller in this case.
    """

    if config.dataset.name == "linear":
        if has_pytorch():
            from .utils.linear.torch.linear_data import TorchLinearDataloader

            return TorchLinearDataloader(
                config=config,
                path=data_dir,
            )
        else:
            from .utils.linear.linear_data import LinearDataloader

            return LinearDataloader(
                config=config,
                path=data_dir,
            )
    return None
