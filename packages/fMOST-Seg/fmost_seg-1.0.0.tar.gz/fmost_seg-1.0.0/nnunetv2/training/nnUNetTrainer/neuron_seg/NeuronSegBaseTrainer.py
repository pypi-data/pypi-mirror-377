from nnunetv2.training.nnUNetTrainer.variants.optimizer.nnUNetTrainerAdam import nnUNetTrainerAdam3en4
import torch

class NeuronSegBaseTrainer(nnUNetTrainerAdam3en4):
    pass

class NeuronSegBaseTrainerNoDeepSupervision(nnUNetTrainerAdam3en4):
    def __init__(
        self,
        plans: dict,
        configuration: str,
        fold: int,
        dataset_json: dict,
        device: torch.device = torch.device("cuda"),
    ):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.enable_deep_supervision = False
        
    def set_deep_supervision_enabled(self, enabled: bool):
        pass

class nnUNetTrainerStage4(NeuronSegBaseTrainer):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):

        arch_init_kwargs['n_stages'] = 4
        arch_init_kwargs['features_per_stage'] = arch_init_kwargs['features_per_stage'][:4]
        arch_init_kwargs['kernel_sizes'] = arch_init_kwargs['kernel_sizes'][:4]
        arch_init_kwargs['strides'] = arch_init_kwargs['strides'][:4]
        arch_init_kwargs['n_conv_per_stage'] = arch_init_kwargs['n_conv_per_stage'][:4]
        arch_init_kwargs['n_conv_per_stage_decoder'] = arch_init_kwargs['n_conv_per_stage_decoder'][:4-1]
        return NeuronSegBaseTrainer.build_network_architecture(
            architecture_class_name, 
            arch_init_kwargs, 
            arch_init_kwargs_req_import, 
            num_input_channels, 
            num_output_channels, 
            enable_deep_supervision
        )

