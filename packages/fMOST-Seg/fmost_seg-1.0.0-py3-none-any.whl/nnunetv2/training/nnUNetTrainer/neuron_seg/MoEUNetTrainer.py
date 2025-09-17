from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainer, nnUNetTrainerStage4
import torch

class MoEUNetTrainer(nnUNetTrainerStage4):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):

        conv_kwargs = dict(
            type='MoeConv',
            n_experts=6,
            n_activated_experts=3,
            n_shared_experts=1,
            route_scale=1.0,
            update_rate=0.001,
            update_bs=32,
            expert_kwargs=dict(type='Conv', kernel_size=3)
        )

        architecture_class_name = 'smz.models.nnunet.architectures.unet.PlainConvUNet'
        arch_init_kwargs['conv_kwargs_per_stage'] = conv_kwargs
        arch_init_kwargs['conv_kwargs_per_stage_decoder'] = conv_kwargs
        
        return nnUNetTrainerStage4.build_network_architecture(
            architecture_class_name, 
            arch_init_kwargs, 
            arch_init_kwargs_req_import, 
            num_input_channels, 
            num_output_channels, 
            enable_deep_supervision
        )

class DenseMoEUNetTrainer(nnUNetTrainerStage4):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):

        conv_kwargs = dict(
            type='MoeConv',
            n_experts=0,
            n_activated_experts=0,
            n_shared_experts=4,
            route_scale=1.0,
            update_rate=0.001,
            update_bs=32,
            expert_kwargs=dict(type='Conv', kernel_size=3)
        )

        architecture_class_name = 'smz.models.nnunet.architectures.unet.PlainConvUNet'
        arch_init_kwargs['conv_kwargs_per_stage'] = conv_kwargs
        arch_init_kwargs['conv_kwargs_per_stage_decoder'] = conv_kwargs
        
        return nnUNetTrainerStage4.build_network_architecture(
            architecture_class_name, 
            arch_init_kwargs, 
            arch_init_kwargs_req_import, 
            num_input_channels, 
            num_output_channels, 
            enable_deep_supervision
        )

class PixelMoEUNetTrainer(nnUNetTrainerStage4):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):

        conv_kwargs = dict(
            type='PixelMoeConv',
            n_experts=6,
            n_activated_experts=3,
            n_shared_experts=1,
            route_scale=1.0,
            update_rate=0.001,
            expert_kwargs=dict(type='Conv', kernel_size=3)
        )

        architecture_class_name = 'smz.models.nnunet.architectures.unet.PlainConvUNet'
        arch_init_kwargs['conv_kwargs_per_stage'] = conv_kwargs
        arch_init_kwargs['conv_kwargs_per_stage_decoder'] = conv_kwargs
        
        return nnUNetTrainerStage4.build_network_architecture(
            architecture_class_name, 
            arch_init_kwargs, 
            arch_init_kwargs_req_import, 
            num_input_channels, 
            num_output_channels, 
            enable_deep_supervision
        )
    

