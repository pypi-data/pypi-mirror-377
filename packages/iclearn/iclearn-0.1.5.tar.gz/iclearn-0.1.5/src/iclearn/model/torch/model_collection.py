import logging

import torch

from iclearn.model import (
    MachineLearningModel,
    load_optimizer,
    load_stopping_conditions,
    load_metrics,
)
from iclearn.model.loss_functions import load_loss_function
from iclearn.model.torch import TorchModel


logger = logging.getLogger(__name__)


class TorchModelTemplate(TorchModel):
    """
    The model to run
    """

    def __init__(
        self,
        model: MachineLearningModel,
        impl,
        loss_func_provider=None,
        metrics_provider=None,
        optimizer_provider=None,
        stopping_condition_provider=None,
    ):

        active_metrics_provider = metrics_provider if metrics_provider else load_metrics
        active_loss_func_provider = (
            loss_func_provider if loss_func_provider else load_loss_function
        )
        active_opt_provider = (
            optimizer_provider if optimizer_provider else load_optimizer
        )
        active_stopping_provider = (
            stopping_condition_provider
            if stopping_condition_provider
            else load_stopping_conditions
        )

        super().__init__(
            metrics=active_metrics_provider(
                active_loss_func_provider(model.loss_function),
                model.metrics,
                model.num_classes,
            ),
            model=impl,
            optimizer=active_opt_provider(impl.parameters(), model.optimizer),
        )
        self.stopping = active_stopping_provider(model.stopping_conditions)


def load_torch_model(
    model: MachineLearningModel,
    loss_func_provider=None,
    metrics_provider=None,
    optimizer_provider=None,
    stopping_condition_provider=None,
):

    logger.info("Searching for model: %s", model.name.lower())

    if model.name.lower() == "torch.linear":
        impl = torch.nn.Linear(1, 1, bias=True)
        return TorchModelTemplate(
            model,
            impl,
            loss_func_provider,
            metrics_provider,
            optimizer_provider,
            stopping_condition_provider,
        )
    return None
