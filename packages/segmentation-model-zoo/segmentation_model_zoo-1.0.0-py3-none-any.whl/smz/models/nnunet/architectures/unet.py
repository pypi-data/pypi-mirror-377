from typing import Union, Type, List, Tuple

import torch
from dynamic_network_architectures.architectures.abstract_arch import (
    AbstractDynamicNetworkArchitectures,
    test_submodules_loadable,
)
from dynamic_network_architectures.building_blocks.helper import convert_conv_op_to_dim
from smz.models.nnunet.building_blocks.plain_conv_encoder import PlainConvEncoder
from smz.models.nnunet.building_blocks.residual import BasicBlockD, BottleneckD
from smz.models.nnunet.building_blocks.residual_encoders import ResidualEncoder
from smz.models.nnunet.building_blocks.unet_decoder import UNetDecoder
from smz.models.nnunet.building_blocks.unet_residual_decoder import UNetResDecoder
from dynamic_network_architectures.initialization.weight_init import InitWeights_He
from dynamic_network_architectures.initialization.weight_init import init_last_bn_before_add_to_0
from torch import nn
from torch.nn.modules.conv import _ConvNd
from torch.nn.modules.dropout import _DropoutNd
from smz.registry import MODELS

@MODELS.register_module()
class PlainConvUNet(AbstractDynamicNetworkArchitectures):
    def __init__(
        self,
        input_channels: int,
        n_stages: int,
        features_per_stage: Union[int, List[int], Tuple[int, ...]],
        conv_op: Type[_ConvNd],
        kernel_sizes: Union[int, List[int], Tuple[int, ...]],
        strides: Union[int, List[int], Tuple[int, ...]],
        n_conv_per_stage: Union[int, List[int], Tuple[int, ...]],
        num_classes: int,
        n_conv_per_stage_decoder: Union[int, Tuple[int, ...], List[int]],
        conv_bias: bool = False,
        norm_op: Union[None, Type[nn.Module]] = None,
        norm_op_kwargs: dict = None,
        dropout_op: Union[None, Type[_DropoutNd]] = None,
        dropout_op_kwargs: dict = None,
        nonlin: Union[None, Type[torch.nn.Module]] = None,
        nonlin_kwargs: dict = None,
        deep_supervision: bool = False,
        nonlin_first: bool = False,
        conv_kwargs_per_stage:  Union[dict, List[dict]] = {'type': 'conv'},
        conv_kwargs_per_stage_decoder:  Union[dict, List[dict]] = {'type': 'conv'},
    ):
        """
        nonlin_first: if True you get conv -> nonlin -> norm. Else it's conv -> norm -> nonlin
        """
        super().__init__()

        self.key_to_encoder = "encoder.stages"  # Contains the stem as well.
        self.key_to_stem = "encoder.stages.0"
        self.keys_to_in_proj = (
            "encoder.stages.0.0.convs.0.all_modules.0",
            "encoder.stages.0.0.convs.0.conv",  # duplicate of above
        )

        if isinstance(n_conv_per_stage, int):
            n_conv_per_stage = [n_conv_per_stage] * n_stages
        if isinstance(n_conv_per_stage_decoder, int):
            n_conv_per_stage_decoder = [n_conv_per_stage_decoder] * (n_stages - 1)
        if isinstance(conv_kwargs_per_stage, dict):
            conv_kwargs_per_stage = [conv_kwargs_per_stage] * n_stages
        if isinstance(conv_kwargs_per_stage_decoder, dict):
            conv_kwargs_per_stage_decoder = [conv_kwargs_per_stage_decoder] * (n_stages - 1)

        assert len(n_conv_per_stage) == n_stages, (
            "n_conv_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"n_conv_per_stage: {n_conv_per_stage}"
        )
        assert len(n_conv_per_stage_decoder) == (n_stages - 1), (
            "n_conv_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"n_conv_per_stage_decoder: {n_conv_per_stage_decoder}"
        )
        assert len(conv_kwargs_per_stage) == n_stages, (
            "conv_kwargs_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"conv_kwargs_per_stage: {conv_kwargs_per_stage_decoder}"
        )
        assert len(conv_kwargs_per_stage_decoder) == (n_stages - 1), (
            "conv_kwargs_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"conv_kwargs_per_stage_decoder: {conv_kwargs_per_stage_decoder}"
        )

        self.encoder = PlainConvEncoder(
            input_channels,
            n_stages,
            features_per_stage,
            conv_op,
            kernel_sizes,
            strides,
            n_conv_per_stage,
            conv_bias,
            norm_op,
            norm_op_kwargs,
            dropout_op,
            dropout_op_kwargs,
            nonlin,
            nonlin_kwargs,
            return_skips=True,
            nonlin_first=nonlin_first,
            conv_kwargs_per_stage=conv_kwargs_per_stage,
        )
        self.decoder = UNetDecoder(
            self.encoder, num_classes, n_conv_per_stage_decoder, deep_supervision, nonlin_first=nonlin_first, conv_kwargs_per_stage_decoder=conv_kwargs_per_stage_decoder
        )

    def forward(self, x):
        skips = self.encoder(x)
        return self.decoder(skips)

    def compute_conv_feature_map_size(self, input_size):
        assert len(input_size) == convert_conv_op_to_dim(self.encoder.conv_op), (
            "just give the image size without color/feature channels or "
            "batch channel. Do not give input_size=(b, c, x, y(, z)). "
            "Give input_size=(x, y(, z))!"
        )
        return self.encoder.compute_conv_feature_map_size(input_size) + self.decoder.compute_conv_feature_map_size(
            input_size
        )

    @staticmethod
    def initialize(module):
        InitWeights_He(1e-2)(module)

@MODELS.register_module()
class ResidualEncoderUNet(AbstractDynamicNetworkArchitectures):
    def __init__(
        self,
        input_channels: int,
        n_stages: int,
        features_per_stage: Union[int, List[int], Tuple[int, ...]],
        conv_op: Type[_ConvNd],
        kernel_sizes: Union[int, List[int], Tuple[int, ...]],
        strides: Union[int, List[int], Tuple[int, ...]],
        n_blocks_per_stage: Union[int, List[int], Tuple[int, ...]],
        num_classes: int,
        n_conv_per_stage_decoder: Union[int, Tuple[int, ...], List[int]],
        conv_bias: bool = False,
        norm_op: Union[None, Type[nn.Module]] = None,
        norm_op_kwargs: dict = None,
        dropout_op: Union[None, Type[_DropoutNd]] = None,
        dropout_op_kwargs: dict = None,
        nonlin: Union[None, Type[torch.nn.Module]] = None,
        nonlin_kwargs: dict = None,
        deep_supervision: bool = False,
        block: Union[Type[BasicBlockD], Type[BottleneckD]] = BasicBlockD,
        bottleneck_channels: Union[int, List[int], Tuple[int, ...]] = None,
        stem_channels: int = None,
        conv_kwargs_per_stage:  Union[dict, List[dict]] = {'type': 'conv'},
        conv_kwargs_per_stage_decoder:  Union[dict, List[dict]] = {'type': 'conv'},
    ):
        super().__init__()

        self.key_to_encoder = "encoder.stages"
        self.key_to_stem = "encoder.stem"
        self.keys_to_in_proj = ("encoder.stem.convs.0.conv", "encoder.stem.convs.0.all_modules.0")

        if isinstance(n_blocks_per_stage, int):
            n_blocks_per_stage = [n_blocks_per_stage] * n_stages
        if isinstance(n_conv_per_stage_decoder, int):
            n_conv_per_stage_decoder = [n_conv_per_stage_decoder] * (n_stages - 1)
        if isinstance(conv_kwargs_per_stage, (tuple, str)):
            conv_kwargs_per_stage = [conv_kwargs_per_stage] * n_stages
        if isinstance(conv_kwargs_per_stage_decoder, (tuple, str)):
            conv_kwargs_per_stage_decoder = [conv_kwargs_per_stage_decoder] * (n_stages - 1)
        assert len(n_blocks_per_stage) == n_stages, (
            "n_blocks_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"n_blocks_per_stage: {n_blocks_per_stage}"
        )
        assert len(n_conv_per_stage_decoder) == (n_stages - 1), (
            "n_conv_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"n_conv_per_stage_decoder: {n_conv_per_stage_decoder}"
        )
        assert len(conv_kwargs_per_stage) == n_stages, (
            "conv_kwargs_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"conv_kwargs_per_stage: {conv_kwargs_per_stage}"
        )
        assert len(conv_kwargs_per_stage_decoder) == (n_stages - 1), (
            "conv_kwargs_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"conv_kwargs_per_stage_decoder: {conv_kwargs_per_stage_decoder}"
        )

        self.encoder = ResidualEncoder(
            input_channels,
            n_stages,
            features_per_stage,
            conv_op,
            kernel_sizes,
            strides,
            n_blocks_per_stage,
            conv_bias,
            norm_op,
            norm_op_kwargs,
            dropout_op,
            dropout_op_kwargs,
            nonlin,
            nonlin_kwargs,
            block,
            bottleneck_channels,
            return_skips=True,
            disable_default_stem=False,
            stem_channels=stem_channels,
            conv_kwargs_per_stage=conv_kwargs_per_stage,
        )
        self.decoder = UNetDecoder(self.encoder, num_classes, n_conv_per_stage_decoder, deep_supervision, conv_kwargs_per_stage_decoder=conv_kwargs_per_stage_decoder)

    def forward(self, x):
        skips = self.encoder(x)
        return self.decoder(skips)

    def compute_conv_feature_map_size(self, input_size):
        assert len(input_size) == convert_conv_op_to_dim(self.encoder.conv_op), (
            "just give the image size without color/feature channels or "
            "batch channel. Do not give input_size=(b, c, x, y(, z)). "
            "Give input_size=(x, y(, z))!"
        )
        return self.encoder.compute_conv_feature_map_size(input_size) + self.decoder.compute_conv_feature_map_size(
            input_size
        )

    @staticmethod
    def initialize(module):
        InitWeights_He(1e-2)(module)
        init_last_bn_before_add_to_0(module)

@MODELS.register_module()
class ResidualUNet(nn.Module):
    def __init__(
        self,
        input_channels: int,
        n_stages: int,
        features_per_stage: Union[int, List[int], Tuple[int, ...]],
        conv_op: Type[_ConvNd],
        kernel_sizes: Union[int, List[int], Tuple[int, ...]],
        strides: Union[int, List[int], Tuple[int, ...]],
        n_blocks_per_stage: Union[int, List[int], Tuple[int, ...]],
        num_classes: int,
        n_conv_per_stage_decoder: Union[int, Tuple[int, ...], List[int]],
        conv_bias: bool = False,
        norm_op: Union[None, Type[nn.Module]] = None,
        norm_op_kwargs: dict = None,
        dropout_op: Union[None, Type[_DropoutNd]] = None,
        dropout_op_kwargs: dict = None,
        nonlin: Union[None, Type[torch.nn.Module]] = None,
        nonlin_kwargs: dict = None,
        deep_supervision: bool = False,
        block: Union[Type[BasicBlockD], Type[BottleneckD]] = BasicBlockD,
        bottleneck_channels: Union[int, List[int], Tuple[int, ...]] = None,
        stem_channels: int = None,
        conv_kwargs_per_stage:  Union[dict, List[dict]] = {'type': 'conv'},
        conv_kwargs_per_stage_decoder:  Union[dict, List[dict]] = {'type': 'conv'},
    ):
        super().__init__()
        if isinstance(n_blocks_per_stage, int):
            n_blocks_per_stage = [n_blocks_per_stage] * n_stages
        if isinstance(n_conv_per_stage_decoder, int):
            n_conv_per_stage_decoder = [n_conv_per_stage_decoder] * (n_stages - 1)
        if isinstance(conv_kwargs_per_stage, (tuple, str)):
            conv_kwargs_per_stage = [conv_kwargs_per_stage] * n_stages
        if isinstance(conv_kwargs_per_stage_decoder, (tuple, str)):
            conv_kwargs_per_stage_decoder = [conv_kwargs_per_stage_decoder] * (n_stages - 1)

        assert len(n_blocks_per_stage) == n_stages, (
            "n_blocks_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"n_blocks_per_stage: {n_blocks_per_stage}"
        )
        assert len(n_conv_per_stage_decoder) == (n_stages - 1), (
            "n_conv_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"n_conv_per_stage_decoder: {n_conv_per_stage_decoder}"
        )
        assert len(conv_kwargs_per_stage) == n_stages, (
            "conv_kwargs_per_stage must have as many entries as we have "
            f"resolution stages. here: {n_stages}. "
            f"conv_kwargs_per_stage: {conv_kwargs_per_stage}"
        )
        assert len(conv_kwargs_per_stage_decoder) == (n_stages - 1), (
            "conv_kwargs_per_stage_decoder must have one less entries "
            f"as we have resolution stages. here: {n_stages} "
            f"stages, so it should have {n_stages - 1} entries. "
            f"conv_kwargs_per_stage_decoder: {conv_kwargs_per_stage_decoder}"
        )

        self.encoder = ResidualEncoder(
            input_channels,
            n_stages,
            features_per_stage,
            conv_op,
            kernel_sizes,
            strides,
            n_blocks_per_stage,
            conv_bias,
            norm_op,
            norm_op_kwargs,
            dropout_op,
            dropout_op_kwargs,
            nonlin,
            nonlin_kwargs,
            block,
            bottleneck_channels,
            return_skips=True,
            disable_default_stem=False,
            stem_channels=stem_channels,
            conv_kwargs_per_stage=conv_kwargs_per_stage,
            conv_kwargs_per_stage_decoder=conv_kwargs_per_stage_decoder,
        )
        self.decoder = UNetResDecoder(self.encoder, num_classes, n_conv_per_stage_decoder, deep_supervision, conv_kwargs_per_stage=conv_kwargs_per_stage_decoder)

    def forward(self, x):
        skips = self.encoder(x)
        return self.decoder(skips)

    def compute_conv_feature_map_size(self, input_size):
        assert len(input_size) == convert_conv_op_to_dim(self.encoder.conv_op), (
            "just give the image size without color/feature channels or "
            "batch channel. Do not give input_size=(b, c, x, y(, z)). "
            "Give input_size=(x, y(, z))!"
        )
        return self.encoder.compute_conv_feature_map_size(input_size) + self.decoder.compute_conv_feature_map_size(
            input_size
        )

    @staticmethod
    def initialize(module):
        InitWeights_He(1e-2)(module)
        init_last_bn_before_add_to_0(module)


if __name__ == "__main__":
    # data = torch.rand((1, 4, 128, 128, 128))

    # model = PlainConvUNet(
    #     4,
    #     6,
    #     (32, 64, 125, 256, 320, 320),
    #     nn.Conv3d,
    #     3,
    #     (1, 2, 2, 2, 2, 2),
    #     (2, 2, 2, 2, 2, 2),
    #     4,
    #     (2, 2, 2, 2, 2),
    #     False,
    #     nn.BatchNorm3d,
    #     None,
    #     None,
    #     None,
    #     nn.ReLU,
    #     deep_supervision=True,
    # )

    # if False:
    #     import hiddenlayer as hl

    #     g = hl.build_graph(model, data, transforms=None)
    #     g.save("network_architecture.pdf")
    #     del g

    # test_submodules_loadable(model)

    # print(model.compute_conv_feature_map_size(data.shape[2:]))

    # data = torch.rand((1, 4, 512, 512))

    # model = PlainConvUNet(
    #     4,
    #     8,
    #     (32, 64, 125, 256, 512, 512, 512, 512),
    #     nn.Conv2d,
    #     3,
    #     (1, 2, 2, 2, 2, 2, 2, 2),
    #     (2, 2, 2, 2, 2, 2, 2, 2),
    #     4,
    #     (2, 2, 2, 2, 2, 2, 2),
    #     False,
    #     nn.BatchNorm2d,
    #     None,
    #     None,
    #     None,
    #     nn.ReLU,
    #     deep_supervision=True,
    # )

    # test_submodules_loadable(model)

    # if False:
    #     import hiddenlayer as hl

    #     g = hl.build_graph(model, data, transforms=None)
    #     g.save("network_architecture.pdf")
    #     del g

    # print(model.compute_conv_feature_map_size(data.shape[2:]))

    # network = ResidualEncoderUNet(
    #     input_channels=32,
    #     n_stages=6,
    #     features_per_stage=[32, 64, 128, 256, 320, 320],
    #     conv_op=torch.nn.Conv3d,
    #     kernel_sizes=[[3, 3, 3] for _ in range(6)],
    #     strides=[[1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
    #     n_blocks_per_stage=[1, 3, 4, 6, 6, 6],
    #     num_classes=2,
    #     n_conv_per_stage_decoder=[1, 1, 1, 1, 1],
    #     conv_bias=True,
    #     norm_op=torch.nn.InstanceNorm3d,
    #     norm_op_kwargs={"eps": 1e-5, "affine": True},
    #     nonlin=torch.nn.LeakyReLU,
    #     nonlin_kwargs={"inplace": True},
    #     deep_supervision=False,
    # )
    # network.initialize(network)
    # test_submodules_loadable(network)



    data = torch.rand((1, 4, 128, 128, 128))
    conv_kwargs = dict(
        type='moeconv',
        n_experts=4,
        n_activated_experts=2,
        n_shared_experts=1,
        route_scale=1.0,
        update_rate=0.001,
        update_bs=8,
        expert_kwargs=dict(type='Conv', kernel_size=3)
    )
    model = PlainConvUNet(
        4,
        6,
        (32, 64, 125, 256, 320, 320),
        nn.Conv3d,
        3,
        (1, 2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2, 2),
        4,
        (2, 2, 2, 2, 2),
        False,
        nn.BatchNorm3d,
        None,
        None,
        None,
        nn.ReLU,
        deep_supervision=False,
        conv_kwargs_per_stage=[conv_kwargs]*6,
        conv_kwargs_per_stage_decoder=[conv_kwargs]*5
    )

    if False:
        import hiddenlayer as hl

        g = hl.build_graph(model, data, transforms=None)
        g.save("network_architecture.pdf")
        del g
    print(model)
    print(model(data).shape)