"""
Module to support creating and launching a training session from the CLI
"""

import os
import logging
from pathlib import Path
from typing import Callable
from functools import partial

from iccore.serialization import read_yaml

from iclearn.session import TrainConfig
from iclearn.environment import has_pytorch


logger = logging.getLogger(__name__)


def load_config(args, local_rank: int) -> TrainConfig:

    config_yaml = read_yaml(args.config.resolve())
    config = TrainConfig(**config_yaml)

    overrides = {
        "local_rank": local_rank,
        "dataset_dir": args.dataset_dir.resolve(),
        "result_dir": args.result_dir.resolve(),
    }

    if args.num_epochs >= 0:
        overrides["num_epochs"] = args.num_epochs
    if args.num_batches >= 0:
        overrides["num_batches"] = args.num_batches
    if args.node_id >= 0:
        overrides["node_id"] = args.node_id
    if args.num_nodes >= 0:
        overrides["num_nodes"] = args.num_nodes
    if args.num_gpus >= 0:
        overrides["num_gpus"] = args.num_gpus

    return config.model_copy(update=overrides)


def worker(session_func: Callable, local_rank: int, args):
    """
    This is the entry point on each parallel worker
    """

    logger.info(
        "Starting worker with rank: %s and result dir: %s",
        local_rank,
        args.result_dir.resolve(),
    )

    config = load_config(args, local_rank)
    profilers, session = session_func(config)
    if args.dry_run == 1:
        return

    logger.info("Starting training stage")
    session.train(config.num_epochs)
    logger.info("Finished training stage")

    if session.env.is_master_process:
        logger.info("Doing inference on test set")
        session.infer()

    profilers.stop()
    logger.info(
        "Finised worker task. Runtime = %.2f minutes",
        profilers.profilers["timer"].get_runtime() / 60,
    )


def cli_func(session_func: Callable, args):

    if args.num_gpus > 1:
        os.environ["MASTER_ADDR"] = "localhost"  # Address for master node
        os.environ["MASTER_PORT"] = "9956"  # Port for comms with master node

        if has_pytorch():
            import torch

            torch.multiprocessing.spawn(
                partial(worker, session_func), nprocs=args.num_gpus, args=(args,)
            )
        else:
            raise RuntimeError("Multigpu launch currently only supported with PyTorch")
    else:
        # Single GPU or CPU execution
        worker(session_func, 0, args)


def add_parser(parent):

    parser = parent.add_parser("train", help="Run in training mode")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path() / "config.yaml",
        help="Path to a config file for the session",
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        default=Path(),
        help="Path to the directory containing datasets",
    )
    parser.add_argument(
        "--result_dir",
        type=Path,
        default=Path() / "results",
        help="Path to results directory",
    )
    parser.add_argument(
        "--num_epochs", type=int, default=-1, help="Number of epochs for training"
    )
    parser.add_argument(
        "--num-nodes", type=int, default=-1, help="Number of nodes to run on"
    )
    parser.add_argument(
        "--node-id", type=int, default=-1, help="ID of the current node"
    )
    parser.add_argument(
        "--num-gpus", type=int, default=-1, help="Number of GPUs per node"
    )
    parser.add_argument(
        "--num_workers", type=int, default=-1, help="Number of dataloader workers"
    )
    parser.add_argument(
        "--num_batches",
        type=int,
        default=-1,
        help="Max number of batches for training. Mostly for troubleshooting.",
    )

    return parser
