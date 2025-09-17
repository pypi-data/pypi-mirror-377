from smz.models.monai_zoo import SwinUNETR
from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision
from torch import nn
from typing import List, Tuple, Union
from dynamic_network_architectures.building_blocks.helper import convert_conv_op_to_dim

class SwinUNETRTrainer(NeuronSegBaseTrainerNoDeepSupervision):
    
    @staticmethod
    def build_network_architecture(
        architecture_class_name: str,
        arch_init_kwargs: dict,
        arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
        num_input_channels: int,
        num_output_channels: int,
        enable_deep_supervision: bool = True,
    ) -> nn.Module:

        return SwinUNETR(
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            patch_size = 2,
            depths = (2, 2, 2, 2),
            num_heads = (3, 6, 12, 24),
            window_size = 7,
            spatial_dims = convert_conv_op_to_dim(arch_init_kwargs['conv_op']),
            use_v2 = False
        )
    
class SwinUNETRV2Trainer(NeuronSegBaseTrainerNoDeepSupervision):
    
    def build_network_architecture(
        architecture_class_name: str,
        arch_init_kwargs: dict,
        arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
        num_input_channels: int,
        num_output_channels: int,
        enable_deep_supervision: bool = True,
    ) -> nn.Module:

        return SwinUNETR(
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            patch_size = 2,
            depths = (2, 2, 2, 2),
            num_heads = (3, 6, 12, 24),
            window_size = 7,
            spatial_dims = convert_conv_op_to_dim(arch_init_kwargs['conv_op']),
            use_v2 = True
        )
    

