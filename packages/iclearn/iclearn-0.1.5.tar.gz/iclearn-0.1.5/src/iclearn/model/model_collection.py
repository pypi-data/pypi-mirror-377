import logging

from iclearn.environment import has_pytorch

from .machine_learning_model import MachineLearningModel


logger = logging.getLogger(__name__)


def load_model(
    model: MachineLearningModel,
    loss_func_provider=None,
    metrics_provider=None,
    optimizer_provider=None,
    stopping_condition_provider=None,
):
    logger.info("Searching for model: %s", model.name)

    if has_pytorch():
        from .torch.model_collection import load_torch_model

        torch_model = load_torch_model(
            model,
            loss_func_provider,
            metrics_provider,
            optimizer_provider,
            stopping_condition_provider,
        )
        if torch_model:
            return torch_model
    return None
