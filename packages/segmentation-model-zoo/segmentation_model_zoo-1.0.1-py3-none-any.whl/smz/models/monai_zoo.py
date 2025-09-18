from monai.networks.nets import UNETR, SwinUNETR, UNet, VNet, SegResNet, AttentionUnet
from smz.registry import MODELS

MODELS.register_module('UNETR', module=UNETR)
MODELS.register_module('SwinUNETR', module=SwinUNETR)
MODELS.register_module('UNet', module=UNet)
MODELS.register_module('VNet', module=VNet)
MODELS.register_module('SegResNet', module=SegResNet)
MODELS.register_module('AttentionUnet', module=AttentionUnet) 