from mmengine.registry import Registry
from mmengine.registry import MODELS as MMENGINE_MODELS

MODELS = Registry('model', parent=MMENGINE_MODELS, locations=['smz.models', 'smz.layers'])