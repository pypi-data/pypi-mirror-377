from torch import nn
from smz.registry import MODELS


@MODELS.register_module('Conv')
@MODELS.register_module('conv')
@MODELS.register_module('CONV')
def conv_factory(spatial_dims: int, **kwargs) -> type[nn.Conv1d | nn.Conv2d | nn.Conv3d]:
    """
    Convolutional layers in 1,2,3 dimensions.

    Args:
        dim: desired dimension of the convolutional layer

    Returns:
        Conv[dim]d
    """
    types = (nn.Conv1d, nn.Conv2d, nn.Conv3d)
    return types[spatial_dims - 1](**kwargs)