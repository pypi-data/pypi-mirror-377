from iclearn.environment import has_pytorch


def load_loss_function(name: str):

    if has_pytorch():
        from .torch import load_torch_loss_function  # NOQA

        return load_torch_loss_function(name)
    return None
