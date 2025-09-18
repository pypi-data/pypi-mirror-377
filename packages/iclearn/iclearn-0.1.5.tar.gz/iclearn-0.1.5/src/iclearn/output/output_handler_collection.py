from pathlib import Path

from .output_handler import OutputHandler
from .logging_output_handler import LoggingOutputHandler
from .mlflow_output_handler import MlFlowOutputHandler
from .plotting_output_handler import PlottingOutputHandler
from .tabular_output_handler import TabularMetricsOutputHandler

from .output_handler import OutputHandlerCreate


def load_output_handlers(
    result_dir: Path, configs: list[OutputHandlerCreate]
) -> list[OutputHandler]:

    ret: list[OutputHandler] = []
    for c in configs:
        if not c.active:
            continue
        if c.name == "mflow":
            ret.append(MlFlowOutputHandler(result_dir))
        elif c.name == "logging":
            ret.append(LoggingOutputHandler(result_dir))
        elif c.name == "plotting":
            ret.append(PlottingOutputHandler(result_dir))
        elif c.name == "tabular_metrics":
            ret.append(TabularMetricsOutputHandler(result_dir))
        if c.name == "tensorboard":
            from .torch.tensorboard_output_handler import TensorboardOutputHandler

            ret.append(TensorboardOutputHandler(result_dir))
    return ret
