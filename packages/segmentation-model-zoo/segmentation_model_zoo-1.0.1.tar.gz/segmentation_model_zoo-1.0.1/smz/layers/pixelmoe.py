import torch
import torch.nn as nn
from typing import List
from monai.networks.layers.factories import split_args
from collections.abc import Sequence
from monai.networks.layers.convutils import same_padding, calculate_out_shape
import numpy as np
from torch.nn.modules.utils import _pair, _triple
import torch.nn.functional as F
from smz.registry import MODELS

class Gate(nn.Module):
    def __init__(
            self, 
            spatial_dims: int,
            in_channels: int,
            n_experts: int,
            n_activated_experts: int,
            route_scale: float = 1.0,
            update_rate: float = 0.001,
        ):
        super().__init__()

        self.topk = n_activated_experts
        self.num_experts = n_experts
        self.gate = MODELS.build(
            cfg=dict(
                type='Conv', 
                spatial_dims=spatial_dims, 
                in_channels=in_channels, 
                out_channels=n_experts,
                kernel_size=3, 
                stride=1, 
                padding=1,
                bias=False)
        )

        # 负载均衡偏置项（不参与梯度计算）
        self.register_buffer('bias', torch.zeros(n_experts))
        self.route_scale = route_scale

        self.register_buffer('_history_counts', torch.zeros(n_experts))
        self.register_buffer('_current_counts', torch.zeros(n_experts))
        self._accumulative_counts = 0
        self.update_rate = update_rate

    def forward(self, x):
        if self.training:
            self.update_bias()

        # 获取空间维度信息
        spatial_dims = (1,) * (x.dim() - 2)  # 创建(1,1,...)用于广播

        scores = torch.sigmoid(self.gate(x))
        # 添加偏置并选择专家
        biased_scores = scores + self.bias.view(1, -1, *spatial_dims)
        _, indices = torch.topk(biased_scores, self.topk, dim=1)  # 直接解包索引

        weights = scores.gather(1, indices)
        weights = F.softmax(weights, dim=1) * self.route_scale  # 合并归一化和缩放

        self._current_counts = torch.bincount(
            indices.view(-1), 
            minlength=self.num_experts
        ).detach()
        
        return weights, indices

    
    def update_bias(self):
        """根据当前统计更新偏置项"""
        self._history_counts += self._current_counts

        if self.training:
            # 计算负载偏差
            load_diff = self._current_counts.mean() - self._current_counts
        
            # 使用符号函数更新偏置
            self.bias += self.update_rate * torch.sign(load_diff)


class Expert(nn.Module):
    def __init__(
            self, 
            spatial_dims: int,
            in_channels: int,
            out_channels: int,
            kwargs: dict = dict(type='Conv', kernel_size=3, stride=1, paddin=1),
            ):
        super().__init__()

        self.out_channels = out_channels
        self.stride = kwargs.get('stride', 1)
        self.stride = _pair(self.stride) if spatial_dims == 2 else _triple(self.stride)
        self.conv = MODELS.build(cfg=dict(
            spatial_dims=spatial_dims,
            in_channels=in_channels,
            out_channels=out_channels,
            **kwargs)
        )

    def forward(self, x):
        return self.conv(x)
    
    
@MODELS.register_module('PixelMoeConv')
@MODELS.register_module('pixelmoeconv')
class MoeConv(nn.Module):
    def __init__(
        self,
        spatial_dims: int,
        in_channels: int,
        out_channels: int,
        stride: Sequence[int] | int = 1,
        kernel_size: Sequence[int] | int = 3,
        padding: Sequence[int] | int  = 1,
        dilation: Sequence[int] | int = 1,
        groups: int = 1,
        bias: bool = True,
        n_experts: int = 4,
        n_activated_experts: int = 2,
        n_shared_experts: int = 1,
        route_scale: float = 1.0,
        update_rate: float = 0.001,
        expert_kwargs: List[dict] | dict = dict(type='Conv', kernel_size=3),
        
    ):
        super().__init__()
        self.spatial_dims = spatial_dims
        self.out_channels = out_channels
        self.topk = n_activated_experts
        self.stride = _pair(stride) if spatial_dims == 2 else _triple(stride)
        self.kernel_size = kernel_size
        self.padding = padding

        self.gate = Gate(
            spatial_dims=spatial_dims,
            in_channels=in_channels,
            n_experts=n_experts,
            n_activated_experts=n_activated_experts,
            route_scale=route_scale,
            update_rate=update_rate,
        )

        self.experts = nn.ModuleList()
        

        self.shared_experts = nn.ModuleList(
            [
                MODELS.build(cfg=dict(
                    type='Conv', 
                    spatial_dims=spatial_dims,
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=kernel_size,
                    stride=stride,
                    padding=padding,
                    dilation=dilation,
                    groups=groups,
                    bias=bias
            )) for _ in range(n_shared_experts)]
        )

        expert_kwargs = expert_kwargs if isinstance(expert_kwargs, list) else [expert_kwargs]
        length = len(expert_kwargs)
        assert n_experts % length == 0, f"n_experts {n_experts} must be divisible by the number of experts {length}"
        times = n_experts // length

        expert_kwargs = expert_kwargs*times
        for i in range(n_experts):
            kwargs = expert_kwargs[i]
            kwargs['kernel_size'] = kwargs.get('kernel_size', kernel_size)
            kwargs['padding'] = kwargs.get('padding', same_padding(kwargs['kernel_size'], kwargs.get('dilation', dilation)))
            kwargs['stride'] = kwargs.get('stride', stride)
            self.experts.append(
                Expert(
                    spatial_dims=spatial_dims,
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kwargs=kwargs
                )
            )
            
    def forward(self, x):
        B, _, *spatial_size = x.shape
        spatial_size = calculate_out_shape(spatial_size, self.kernel_size, self.stride, self.padding)

        weights, indices = self.gate(x)

        output = torch.zeros(B, self.out_channels, *spatial_size, device=x.device, dtype=x.dtype)
        
        # 遍历所有专家进行并行计算
        for expert_idx, expert in enumerate(self.experts):
            # 创建当前专家的掩码 [batch, top_k, d, h, w]
            mask = (indices == expert_idx)

            # 计算当前专家被选中的位置数量
            if mask.any():
                # 获取当前专家的分数 [batch, top_k, d, h, w]
                expert_score = weights * mask.float()
                
                # 在top_k维度上求和 [batch, d, h, w]
                expert_score = expert_score.sum(1, True)
                
                # 添加加权专家输出
                output += self.experts[expert_idx](x) * expert_score

        for shared_expert in self.shared_experts:
            shared_output = shared_expert(x)
            output += shared_output

        return output


if __name__ == '__main__':
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    inputs_3d = torch.randn(2, 1, 64, 64, 64).to(device)
    moe_conv_3d = MoeConv(
        spatial_dims=3,
        in_channels=1,
        out_channels=16,
        stride=2,
        n_experts=4,
        n_activated_experts=2,
        n_shared_experts=1,
        route_scale=1.0,
        expert_kwargs=[dict(type='ODConv', kernel_size=3), dict(type='ODConv', kernel_size=9)]
    ).to(device)
    print(moe_conv_3d)
    print(moe_conv_3d(inputs_3d).shape)

    inputs_2d = torch.randn(2, 1, 64, 64).to(device)
    
    moe_conv_2d = MoeConv(
        spatial_dims=2,
        in_channels=1,
        out_channels=16,
        stride=2,
        n_experts=4,
        n_activated_experts=2,
        n_shared_experts=1,
        route_scale=1.0
    ).to(device)
    print(moe_conv_2d(inputs_2d).shape)