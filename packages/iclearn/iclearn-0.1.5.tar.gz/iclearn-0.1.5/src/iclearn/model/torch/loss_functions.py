import torch

_REGISTRY = {
    "torch.CrossEntropyLoss": torch.nn.CrossEntropyLoss,
    "torch.MSELoss": torch.nn.MSELoss,
}


def load_torch_loss_function(name: str):
    if name in _REGISTRY:
        return _REGISTRY[name]()
    return None
