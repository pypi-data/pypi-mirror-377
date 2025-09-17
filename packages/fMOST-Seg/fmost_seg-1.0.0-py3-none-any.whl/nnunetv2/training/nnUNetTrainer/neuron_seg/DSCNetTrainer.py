from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision
import torch
from torch import autocast
from nnunetv2.utilities.helpers import empty_cache, dummy_context
from smz.models.dscnet.dscnet_3d.DSCNetSmall import DSCNetSmall

class DSCNetTrainer(NeuronSegBaseTrainerNoDeepSupervision):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):
        return DSCNetSmall(
            n_channels = num_input_channels, 
            n_classes = num_output_channels, 
            kernel_size = 3, 
            extend_scope = 1.0, 
            if_offset = True, 
            device = torch.device('cuda'), 
            number = 16, 
            # dim = None
        )