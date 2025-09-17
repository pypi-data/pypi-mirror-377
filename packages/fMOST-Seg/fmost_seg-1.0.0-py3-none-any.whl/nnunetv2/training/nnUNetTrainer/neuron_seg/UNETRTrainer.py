from smz.models.monai_zoo import UNETR
from torch import nn
from typing import List, Tuple, Union
from dynamic_network_architectures.building_blocks.helper import convert_conv_op_to_dim
from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision

class UNETRTrainer(NeuronSegBaseTrainerNoDeepSupervision):
    
    def build_network_architecture(
        self,
        architecture_class_name: str,
        arch_init_kwargs: dict,
        arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
        num_input_channels: int,
        num_output_channels: int,
        enable_deep_supervision: bool = True,
    ) -> nn.Module:

        return UNETR(
            img_size = self.configuration_manager.patch_size,
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            feature_size = 16,
            hidden_size = 768,
            mlp_dim = 3072,
            num_heads = 12,
            proj_type= "conv",
            norm_name = "instance",
            conv_block = True,
            res_block = True,
            dropout_rate = 0.0,
            spatial_dims = convert_conv_op_to_dim(arch_init_kwargs['conv_op']),
            qkv_bias = False,
            save_attn = False,
        )
