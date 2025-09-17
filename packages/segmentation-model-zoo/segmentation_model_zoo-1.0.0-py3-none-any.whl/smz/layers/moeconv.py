import torch
import torch.nn as nn
from typing import List
from monai.networks.layers.factories import split_args
from collections.abc import Sequence
from monai.networks.layers.convutils import same_padding, calculate_out_shape
import numpy as np
from torch.nn.modules.utils import _pair, _triple
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
            update_bs: int = 32,
        ):
        super().__init__()
        
        self.topk = n_activated_experts
        self.num_experts = n_experts
        self.gate = nn.Sequential(
            nn.AdaptiveAvgPool3d(1) if spatial_dims == 3 else nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(in_channels, n_experts)
        )   

        # 负载均衡偏置项（不参与梯度计算）
        self.register_buffer('bias', torch.zeros(n_experts))
        self.route_scale = route_scale

        self._current_batch_size = 0
        self.register_buffer('_current_counts', torch.zeros(n_experts))
        self.register_buffer('_history_counts', torch.zeros(n_experts))
        self.update_rate = update_rate
        self.update_bs = update_bs
        self.acc_bs = 0
        self.register_buffer('_accumulative_counts', torch.zeros(n_experts))

    def forward(self, x):
        self._current_batch_size = x.size(0)

        if self.training:
            self.update_bias()

        scores = self.gate(x).sigmoid()
        original_scores = scores
        scores = scores + self.bias
        indices = torch.topk(scores, self.topk, dim=-1)[1]
        weights = original_scores.gather(-1, indices)
        weights /= weights.sum(dim=-1, keepdim=True)
        weights *= self.route_scale

        self._current_counts = torch.bincount(
            indices.view(-1), 
            minlength=self.num_experts
        ).detach()
        
        return weights.type_as(x).reshape(self._current_batch_size, -1), indices.reshape(self._current_batch_size, -1)

    @torch.no_grad()
    def update_bias(self):
        """根据当前统计更新偏置项"""
        self._history_counts += self._current_counts
        self._accumulative_counts += self._current_counts
        self.acc_bs += self._current_batch_size

        if self.acc_bs >= self.update_bs:
            self.acc_bs = 0
            # 计算负载偏差
            load_diff = self._accumulative_counts.mean() - self._accumulative_counts
            
            self._accumulative_counts.zero_()
            # 使用符号函数更新偏置
            self.bias += self.update_rate * torch.sign(load_diff)

class Expert(nn.Module):
    def __init__(
            self, 
            spatial_dims: int,
            in_channels: int,
            out_channels: int,
            kwargs: dict = dict(type='Conv', kernel_size=3, stride=1, padding=1)
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

    
@MODELS.register_module('MoeConv')
@MODELS.register_module('moeconv')
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
        update_bs: int = 32,
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
            update_bs=update_bs,
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

        counts = torch.bincount(indices.flatten(), minlength=len(self.experts)).tolist()
        
        # 遍历所有专家进行并行计算
        for expert_idx, expert in enumerate(self.experts):
            if counts[expert_idx] == 0:
                continue

            expert = self.experts[expert_idx]
            idx, top = torch.where(indices == expert_idx)
            output[idx] += expert(x[idx]) * weights[idx, top].view(-1, *[1]*(len(x.shape)-1))

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
        stride=1,
        n_experts=4,
        n_activated_experts=2,
        n_shared_experts=1,
        route_scale=1.0,
        # expert_kwargs=[dict(type='ODConv', kernel_size=3), dict(type='ODConv', kernel_size=9)]
        expert_kwargs=[dict(type='Conv', kernel_size=3), dict(type='Conv', kernel_size=9)],
        update_bs=8,
    ).to(device) 
    # print(moe_conv_3d)
    # print(moe_conv_3d.gate._history_counts, moe_conv_3d.gate._current_counts)
    # print(moe_conv_3d(inputs_3d).shape)
    # print(moe_conv_3d.gate._history_counts, moe_conv_3d.gate._current_counts)
    for i in range(10000):
        x = torch.randn(2, 1, 64, 64, 64).to(device)
        y = moe_conv_3d(x)
        if i % 32 == 0:
            print(i, moe_conv_3d.gate.bias, moe_conv_3d.gate._history_counts, moe_conv_3d.gate._current_counts)

    # inputs_2d = torch.randn(2, 1, 64, 64).to(device)
    
    # moe_conv_2d = MoeConv(
    #     spatial_dims=2,
    #     in_channels=1,
    #     out_channels=16,
    #     stride=1,
    #     n_experts=4,
    #     n_activated_experts=2,
    #     n_shared_experts=1,
    #     route_scale=1.0,
    # ).to(device)
    # print(moe_conv_2d(inputs_2d).shape)