from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision
from typing import List, Tuple, Union
from torch import nn
from dynamic_network_architectures.building_blocks.helper import convert_conv_op_to_dim
from smz.models.swin_smt.swin_smt import SwinSMT
import pydoc

class SwinSMTTrainer(NeuronSegBaseTrainerNoDeepSupervision):
    def build_network_architecture(
        self,
        architecture_class_name: str,
        arch_init_kwargs: dict,
        arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
        num_input_channels: int,
        num_output_channels: int,
        enable_deep_supervision: bool = True,
    ) -> nn.Module:

        return SwinSMT(
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            img_size = self.configuration_manager.patch_size,
            spatial_dims = convert_conv_op_to_dim(pydoc.locate(arch_init_kwargs['conv_op'])),
            use_v2 = False,
            feature_size=48,
            use_moe=True,
            num_experts=4,
            num_layers_with_moe=3
        )