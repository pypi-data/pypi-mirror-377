"""
Module to support creating and launching a training session from the CLI
"""

import logging
from typing import Callable

from iccore.time_utils import get_timestamp_for_paths

import iclearn.session
from iclearn.environment import has_pytorch
from iclearn.utils.profiler import TimerProfiler, ProfilerCollection
from iclearn.output import LoggingOutputHandler

from iclearn.session import TrainConfig

logger = logging.getLogger(__name__)


def setup_profilers(config: TrainConfig):
    profilers = ProfilerCollection()
    profilers.add_profiler("timer", TimerProfiler(config.result_dir))
    if config.with_profiling:
        if config.model.framework == "pytorch" and has_pytorch():
            from iclearn.utils.torch.profiler import TorchProfiler

            profilers.add_profiler("torch", TorchProfiler(config.result_dir))
    return profilers


def load_environment(config: TrainConfig):
    if config.model.framework == "pytorch" and has_pytorch():
        from iclearn.environment.torch import environment

        return environment.load(
            config.node_id, config.num_nodes, config.num_gpus, config.local_rank
        )
    else:
        from iclearn.environment import environment  # type: ignore

        return environment.load(config.local_rank)


def write_environment(env, config: TrainConfig):
    if config.model.framework == "pytorch" and has_pytorch():
        from iclearn.environment.torch import environment

        return environment.write(env, config.result_dir)
    else:
        from iclearn.environment import environment  # type: ignore

        return environment.write(env, config.result_dir)


def setup_session(
    dataloader_func: Callable,
    model_func: Callable,
    output_handler_func: Callable | None,
    input_config: TrainConfig,
):

    result_dir = input_config.result_dir / input_config.name / get_timestamp_for_paths()
    result_dir.mkdir(parents=True, exist_ok=True)

    config = input_config.model_copy(update={"result_dir": result_dir})

    logger.info("Starting session in: %s", config.result_dir)
    iclearn.session.train_config.write_config(config, config.result_dir)

    logger.info("Setting up profilers")
    profilers = setup_profilers(config)
    profilers.start()

    logger.info("Loading environment")
    env = load_environment(config)
    write_environment(env, config)

    logger.info(
        "Loading dataset '%s' with cache in: %s",
        config.dataloader.dataset.name,
        config.dataset_dir,
    )
    dataloader = dataloader_func(config.dataloader, config.dataset_dir)
    dataloader.load(env)

    logger.info("Creating model: '%s'", config.model.name)
    model_config = config.model.model_copy(
        update={"num_classes": dataloader.num_classes}
    )
    model = model_func(model_config)

    logger.info("Creating Session")
    session = iclearn.session.Session(model, env, config.result_dir, dataloader)

    handlers: list = []
    if output_handler_func:
        handlers = output_handler_func(config.result_dir, config.outputs)

    if not handlers:
        handlers = [LoggingOutputHandler(config.result_dir)]
    session.output_handlers.extend(handlers)

    return profilers, session
