from torch import nn
from collections.abc import Sequence
from torch.nn.modules.utils import _triple, _pair
import numpy as np
from torchvision.ops import DeformConv2d
try:
    from dconv_native.modules import DeformConv3d
except ImportError:
    DeformConv3d = None
from functools import partial
from monai.networks.layers.utils import get_act_layer, get_norm_layer
from monai.networks.layers.convutils import same_padding
import torch
from smz.registry import MODELS

class _DeformConvBase(nn.Module):
    def __init__(
        self,
        spatial_dims: int,
        in_channels: int,
        out_channels: int,
        stride: Sequence[int] | int = 1,
        kernel_size: Sequence[int] | int = 3,
        padding: Sequence[int] | int | None = None,
        dilation: Sequence[int] | int = 1,
        groups: int = 1,
        offset_groups: int = 1,
        bias: bool = True,
        modulated_act: tuple | str | None = "SIGMOID",
        deform_param_op: str = "Conv"
    ):
        super(_DeformConvBase, self).__init__()
        assert spatial_dims in [2, 3], "spatial_dims should be 2 or 3"
    
        kernel_size = _pair(kernel_size) if spatial_dims == 2 else _triple(kernel_size)

        self.num_kernel_points = np.prod(kernel_size)
        self.offset_groups = offset_groups
        self.groups = groups
        self.spatial_dims = spatial_dims
        self.stride = _pair(stride) if spatial_dims == 2 else _triple(stride)
        self.modulated_act = get_act_layer(modulated_act) if modulated_act is not None else nn.Identity()

        if padding is None:
            padding = same_padding(kernel_size, dilation)

        print('deform_param_op', deform_param_op)
        self.deform_params = MODELS.build(
            cfg=dict(
                type=deform_param_op,
                spatial_dims=spatial_dims,
                in_channels=in_channels,
                out_channels=self._deform_channels(),
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                dilation=dilation,
                groups=1,
                bias=bias
            )
        )
        
        self.deform_conv_op = DeformConv2d if spatial_dims == 2 else partial(DeformConv3d, offset_groups=offset_groups)
        self.deform_conv = self.deform_conv_op(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            dilation,
            groups,
            bias=bias
        )
        

    def _deform_channels(self):
        return self.spatial_dims * self.offset_groups * self.num_kernel_points

    def _get_deformation(self, input):
        return self.deform_params(input), None

    def forward(self, input):
        deformation = self._get_deformation(input)
        return self.deform_conv(input, *deformation)
    

@MODELS.register_module()
class DeformConv(_DeformConvBase):
    pass

@MODELS.register_module()
class ModulatedDeformConv(_DeformConvBase):
    def _deform_channels(self):
        self.offset_channels = self.spatial_dims * self.offset_groups * self.num_kernel_points
        self.alpha_channels = self.offset_groups * self.num_kernel_points
        return self.offset_channels + self.alpha_channels

    def _get_deformation(self, input):
        deformation = self.deform_params(input)
        offset, alpha = torch.split(
            deformation,
            [self.offset_channels, self.alpha_channels],
            dim=1
        )
        return offset, self.modulated_act(alpha)

# y(𝑝_0)=∑𝑤(𝑝_𝑛 )⋅𝑥(𝑝_0+𝑝_𝑛+Δ𝑝_𝑛 )Δ𝑚_𝑛 
# 𝑝_𝑛+Δ𝑝_𝑛是最终的形状
# generate_cross_shape_grid和generate_x_shape_grid产生的Δ𝑝_𝑛已经是最终形状，因此需要减去𝑝_𝑛
# convert_dsc_offsets产生的Δ𝑝_𝑛需要加上𝑝_𝑛才是想要的形状
def convert_dsc_offsets_3d(offsets, morph, num_kernel_points):
    offsets = offsets.float()
    center = num_kernel_points // 2

    x = offsets[:, ::3]
    y = offsets[:, 1::3]
    z = offsets[:, 2::3]
    
    # Determine axes to zero and process based on morph
    if morph == 0:
        x = 0
        process_axes = [y, z]
    elif morph == 1:
        y = 0
        process_axes = [x, z]
    elif morph == 2:
        z = 0
        process_axes = [x, y]
    else:
        raise ValueError("Invalid morph value. Must be 0, 1, 2.")

    # Process each axis
    for axis in process_axes:
        # Process front half (from start to center, inclusive)
        axis[:, :center+1] = axis[:, :center+1].flip(1).cumsum(1).flip(1)
        
        # Process back half (from center to end)
        axis[:, center:] = axis[:, center:].cumsum(1)
    
    offsets[:, ::3] = x
    offsets[:, 1::3] = y 
    offsets[:, 2::3]= z
    
    return offsets


def convert_dsc_offsets_2d(offsets, morph, num_kernel_points):
    offsets = offsets.float()
    center = num_kernel_points // 2

    x = offsets[:, ::2]
    y = offsets[:, 1::2]
    
    # Determine axes to zero and process based on morph
    if morph == 0:
        x = 0
        axis = y
    elif morph == 1:
        y = 0
        axis = x
    else:
        raise ValueError("Invalid morph value. Must be 0, 1, 2.")

    # Process each axis
    axis[:, :center+1] = axis[:, :center+1].flip(1).cumsum(1).flip(1)
    # Process back half (from center to end)
    axis[:, center:] = axis[:, center:].cumsum(1)
    
    offsets[:, ::2] = x
    offsets[:, 1::2] = y 
    
    return offsets

class _DynamicSnakeConvBase(DeformConv):
    def __init__(
        self,
        spatial_dims: int,
        in_channels: int,
        out_channels: int,
        stride: Sequence[int] | int = 1,
        kernel_size: Sequence[int] | int = 3,
        padding: Sequence[int] | int | None = None,
        dilation: Sequence[int] | int = 1,
        groups: int = 1,
        offset_groups: int = 1,
        bias: bool = True,
        modulated_act: tuple | str | None = "SIGMOID",
        deform_param_op: nn.Module | None = None,
        offset_norm: tuple | str | None = "batch",
        offset_act: tuple | str | None = "tanh",
        morph = None,
    ):
        self.spatial_dims = spatial_dims
        self.morph = morph
        assert self.morph is not None, "morph should be set before replacing deform conv"
        assert self.morph <= 2 and spatial_dims == 3 or self.morph < 2 and spatial_dims == 2, "morph should be 0 or 1 for 2D and 2 for 3D"

        if spatial_dims == 3:
            self.convert_offsets = convert_dsc_offsets_3d
        else:
            self.convert_offsets = convert_dsc_offsets_2d
        
        kernel_size = max(kernel_size) if isinstance(kernel_size, Sequence) else kernel_size
        if self.morph == 0:
            kernel_size = (kernel_size, 1) if spatial_dims == 2 else (kernel_size, 1, 1)
        elif self.morph == 1:
            kernel_size = (1, kernel_size) if spatial_dims == 2 else (1, kernel_size, 1)
        else:
            kernel_size = (1, 1, kernel_size)
        padding = same_padding(kernel_size, dilation)
        self.num_kernel_points = np.prod(kernel_size)
        self.offset_groups = offset_groups

        super(_DynamicSnakeConvBase, self).__init__(spatial_dims, in_channels, out_channels, stride, kernel_size, padding, dilation, groups, offset_groups, bias, modulated_act, deform_param_op)
        
        self.offset_norm = get_norm_layer(offset_norm, spatial_dims, self.spatial_dims * self.offset_groups * self.num_kernel_points)
        self.offset_act = get_act_layer(offset_act)

    def _get_deformation(self, input):
        offsets, alpha = super()._get_deformation(input)
        offsets = offsets.clone()
        return self.convert_offsets(self.offset_act(self.offset_norm(offsets)), self.morph, self.num_kernel_points), alpha   

@MODELS.register_module()    
class XDSConv(_DynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 0
        super(XDSConv, self).__init__(*args, **kwargs)

@MODELS.register_module()    
class YDSConv(_DynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 1
        super(YDSConv, self).__init__(*args, **kwargs)

@MODELS.register_module()
class ZDSConv(_DynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 2
        super(ZDSConv, self).__init__(*args, **kwargs)

class _ModulatedDynamicSnakeConvBase(_DynamicSnakeConvBase):
    def _deform_channels(self):
        self.offset_channels = self.spatial_dims * self.offset_groups * self.num_kernel_points
        self.alpha_channels = self.offset_groups * self.num_kernel_points
        return self.offset_channels + self.alpha_channels

    def _get_deformation(self, input):
        deformation = self.deform_params(input)
        offset, alpha = torch.split(
            deformation,
            [self.offset_channels, self.alpha_channels],
            dim=1
        )
        offset = offset.clone()
        return self.convert_offsets(self.offset_act(self.offset_norm(offset)), self.morph, self.num_kernel_points), self.modulated_act(alpha)

@MODELS.register_module()
class XMDSConv(_ModulatedDynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 0
        super(XMDSConv, self).__init__(*args, **kwargs)

@MODELS.register_module()
class YMDSConv(_ModulatedDynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 1
        super(YMDSConv, self).__init__(*args, **kwargs)

@MODELS.register_module()
class ZMDSConv(_ModulatedDynamicSnakeConvBase):
    def __init__(self, *args, **kwargs):
        kwargs["morph"] = 2
        super(ZMDSConv, self).__init__(*args, **kwargs)

@MODELS.register_module()
class DynamicSnakeConv(nn.Module):
    def __init__(
        self,
        spatial_dims: int,
        in_channels: int,
        out_channels: int,
        stride: Sequence[int] | int = 1,
        kernel_size: Sequence[int] | int = 3,
        padding: Sequence[int] | int | None = None,
        dilation: Sequence[int] | int = 1,
        groups: int = 1,
        offset_groups: int = 1,
        bias: bool = True,
        modulated_act: tuple | str | None = "SIGMOID",
        deform_param_op: nn.Module | None = 'conv',
        offset_norm: tuple | str | None = "batch",
        offset_act: tuple | str | None = "tanh",
        modulated: bool = False,
    ):
        super(DynamicSnakeConv, self).__init__()
        assert spatial_dims in [2, 3], "spatial_dims should be 2 or 3"

        self.out_channels = out_channels
        self.spatial_dims = spatial_dims
        self.stride = _pair(stride) if spatial_dims == 2 else _triple(stride)
        self.conv = MODELS.build(
            cfg=dict(
                type='Conv',
                spatial_dims=spatial_dims,
                in_channels=spatial_dims*out_channels,
                out_channels=out_channels,
                kernel_size=3,
                stride=1,
                padding=1,
                dilation=1,
                groups=1,
                bias=bias
            )
        )


        xdsc_type = XMDSConv if modulated else XDSConv
        self.xdsc = nn.Sequential(
            xdsc_type(
                spatial_dims,
                in_channels,
                out_channels,
                stride,
                kernel_size,
                padding,
                dilation,
                groups,
                offset_groups,
                bias,
                modulated_act,
                deform_param_op,
                offset_norm,
                offset_act
            ),
            get_norm_layer('batch', spatial_dims, out_channels),
            get_act_layer('relu')
        )

        ydsc_type = YMDSConv if modulated else YDSConv
        self.ydsc = nn.Sequential(
            ydsc_type(
                spatial_dims,
                in_channels,
                out_channels,
                stride,
                kernel_size,
                padding,
                dilation,
                groups,
                offset_groups,
                bias,
                modulated_act,
                deform_param_op,
                offset_norm,
                offset_act
            ),
            get_norm_layer('batch', spatial_dims, out_channels),
            get_act_layer('relu')
        )

        if spatial_dims == 3:
            zdsc_type = ZMDSConv if modulated else ZDSConv
            self.zdsc = nn.Sequential(
                zdsc_type(
                    spatial_dims,
                    in_channels,
                    out_channels,
                    stride,
                    kernel_size,
                    padding,
                    dilation,
                    groups,
                    offset_groups,
                    bias,
                    modulated_act,
                    deform_param_op,
                    offset_norm,
                    offset_act
                ),
                get_norm_layer('batch', spatial_dims, out_channels),
                get_act_layer('relu')
            )
        
        self.forward_func = self.forward_3d if spatial_dims == 3 else self.forward_2d

    def forward_3d(self, input):
        return self.conv(torch.cat([
            self.xdsc(input),
            self.ydsc(input),
            self.zdsc(input)
        ], dim=1))
    
    def forward_2d(self, input):
        return self.conv(torch.cat([
            self.xdsc(input),
            self.ydsc(input)
        ], dim=1))
    
    def forward(self, input):
        return self.forward_func(input)
            

if __name__ == "__main__":
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inputs = torch.randn(2, 3, 64, 64).to(device)

    conv_type = DynamicSnakeConv
    conv = conv_type(
        spatial_dims=2,
        in_channels=3,
        out_channels=16,
        stride=1,
        kernel_size=3,
        padding=1,
        dilation=1,
        groups=1,
        offset_groups=1,
        bias=True,
        modulated=True
    ).to(device)
    outputs = conv(inputs)
    print(outputs.shape)  # should be (2, 16, 64, 64)

    inputs = torch.randn(2, 3, 64, 64, 64).to(device)
    conv = conv_type(
        spatial_dims=3,
        in_channels=3,
        out_channels=16,
        stride=1,
        kernel_size=3,
        padding=1,
        dilation=1,
        groups=1,
        offset_groups=1,
        bias=True,
        modulated=True
    ).to(device)
    outputs = conv(inputs)
    print(outputs.shape)  # should be (2, 16, 64, 64, 64)


