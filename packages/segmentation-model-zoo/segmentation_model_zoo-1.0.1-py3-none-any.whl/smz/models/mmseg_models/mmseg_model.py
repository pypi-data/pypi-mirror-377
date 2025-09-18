from mmseg.registry import MODELS
from torch import nn
from mmseg.utils import ConfigType

class MMSegModel(nn.Module):
    def __init__(self, 
                 input_channels:int, 
                 num_classes:int, 
                 cfg:ConfigType = None, 
                 final_up:int =0, 
                 deep_supervision:bool = True):
        super().__init__()
        model = cfg.model
        model.data_preprocessor = None
        model.backbone.in_channels = input_channels
        model.decode_head.num_classes = num_classes
        model.auxiliary_head.num_classes = num_classes
        self.model = MODELS.build(model)
        self.final_up = nn.UpsamplingBilinear2d(scale_factor=final_up) if final_up > 0 else nn.Identity()
        self.deep_supervision = deep_supervision

    def forward(self, inputs):
        x = self.model.extract_feat(inputs)
        main_out = self.final_up(self.model.decode_head.forward(x))
        if self.deep_supervision:
            out = [main_out]
            if isinstance(self.model.auxiliary_head, nn.ModuleList):
                for idx, aux_head in enumerate(self.auxiliary_head):
                    out.append(aux_head.forward(x))
            else:
                out.append(self.model.auxiliary_head.forward(x))  
            return out
        return main_out


if __name__ == "__main__":
    import torch
    from mmengine import Config
    cfg = Config.fromfile('/home/yjiang/workspace/code/segmentation-model-zoo/smz/models/mmseg_models/configs/CCNet/ccnet_r50-d8.py')
    model = MMSegModel(input_channels=4, num_classes=3, cfg=cfg, final_up=4, deep_supervision=False)
    model.eval()
    x = torch.randn(2, 4, 256, 256)
    with torch.no_grad():
        y = model(x)
    print(y.shape)