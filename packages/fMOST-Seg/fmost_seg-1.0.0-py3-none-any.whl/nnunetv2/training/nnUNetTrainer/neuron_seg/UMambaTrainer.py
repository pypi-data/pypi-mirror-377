from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainer
from torch import nn
from typing import List, Tuple, Union
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans


class UMambaBot3DTainer(NeuronSegBaseTrainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return get_network_from_plans(
            'smz.models.umamba.UMambaBot_3d.UMambaBot',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
    )


class UMambaBot2DTainer(NeuronSegBaseTrainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return get_network_from_plans(
            'smz.models.umamba.UMambaBot_2d.UMambaBot',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
        )