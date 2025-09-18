#!/usr/bin/env python3

from pathlib import Path

from iccore.logging_utils import setup_default_logger

import iclearn.cli
from iclearn.data import Dataloader, DataloaderCreate, load_dataloader
from iclearn.model import Model, MachineLearningModel, load_model
from iclearn.output import OutputHandler, OutputHandlerCreate, load_output_handlers


def create_dataloader(config: DataloaderCreate, data_dir: Path) -> Dataloader:
    dataloader = load_dataloader(config, data_dir)
    if not dataloader:
        raise RuntimeError(f"Dataloader with name {config.dataset.name} not found.")
    return dataloader


def create_model(config: MachineLearningModel) -> Model:
    model = load_model(config)
    if not model:
        raise RuntimeError(f"Model with name {config.name} not found.")
    return model


def create_output_handlers(
    result_dir: Path, handlers: list[OutputHandlerCreate]
) -> list[OutputHandler]:
    return load_output_handlers(result_dir, handlers)


def main_cli():

    parser = iclearn.cli.get_default_parser(
        create_dataloader, create_model, create_output_handlers
    )

    args = parser.parse_args()

    setup_default_logger()

    args.func(args)


if __name__ == "__main__":
    main_cli()
