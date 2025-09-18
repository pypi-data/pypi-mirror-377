from nnunetv2.training.nnUNetTrainer.nnUNetTrainerDist import nnUNetTrainerDist
from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision
import torch
from smz.models.datnet import DTAnet
from torch import autocast
from nnunetv2.utilities.helpers import empty_cache, dummy_context
from nnunetv2.training.loss.dice import MemoryEfficientSoftDiceLoss, get_tp_fp_fn_tn
from nnunetv2.training.loss.robust_ce_loss import RobustCrossEntropyLoss
from nnunetv2.training.loss.compound_losses import DC_and_CE_loss, DC_and_BCE_loss
from nnunetv2.training.loss.deep_supervision import DeepSupervisionWrapper


class ADTLNetTrainer(NeuronSegBaseTrainerNoDeepSupervision):
    def __init__(self, plans: dict, configuration: str, fold: int, dataset_json: dict,
                device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.cls_loss = None
        self.alpha = 0.4

    def initialize(self):
        super().initialize()
        self.cls_loss = torch.nn.CrossEntropyLoss()

    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):
        return DTAnet(
            num_channels = num_input_channels,
            num_classes = num_output_channels
        )
    

    def train_step(self, batch: dict) -> dict:
        data = batch['data']
        target = batch['target']
        cls_target = torch.tensor([0 if 'SN' in i else 1 for i in batch['keys']], device=self.device)

    
        data = data.to(self.device, non_blocking=True)

        if isinstance(target, list):
            target = [i.to(self.device, non_blocking=True) for i in target]
        else:
            target = target.to(self.device, non_blocking=True)

        self.optimizer.zero_grad(set_to_none=True)
        # Autocast can be annoying
        # If the device_type is 'cpu' then it's slow as heck and needs to be disabled.
        # If the device_type is 'mps' then it will complain that mps is not implemented, even if enabled=False is set. Whyyyyyyy. (this is why we don't make use of enabled=False)
        # So autocast will only be active if we have a cuda device.
        with autocast(self.device.type, enabled=True) if self.device.type == 'cuda' else dummy_context():
            sn_output, ws_output, cls_out = self.network(data)

            sn_mask = (cls_target == 0)
            ws_mask = (cls_target == 1)

            seg_output = torch.zeros_like(sn_output)
            seg_output[sn_mask] = sn_output[sn_mask]
            seg_output[ws_mask] = ws_output[ws_mask]

            # seg_loss = self.loss(sn_output, target) + self.loss(ws_output, target)
            seg_loss = self.loss(seg_output, target)
            cls_loss = self.cls_loss(cls_out, cls_target)
            l = self.alpha * cls_loss + (1 - self.alpha) * seg_loss

        if self.grad_scaler is not None:
            self.grad_scaler.scale(l).backward()
            self.grad_scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 3)
            self.grad_scaler.step(self.optimizer)
            self.grad_scaler.update()
        else:
            l.backward()
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 3)
            self.optimizer.step()
        return {'loss': l.detach().cpu().numpy()}


    def on_validation_epoch_start(self):
        self.network.eval()

    def validation_step(self, batch: dict) -> dict:
        data = batch['data']
        target = batch['target']
        cls_target = torch.tensor([0 if 'SN' in i else 1 for i in batch['keys']], device=self.device)

        data = data.to(self.device, non_blocking=True)
        if isinstance(target, list):
            target = [i.to(self.device, non_blocking=True) for i in target]
        else:
            target = target.to(self.device, non_blocking=True)

        # Autocast can be annoying
        # If the device_type is 'cpu' then it's slow as heck and needs to be disabled.
        # If the device_type is 'mps' then it will complain that mps is not implemented, even if enabled=False is set. Whyyyyyyy. (this is why we don't make use of enabled=False)
        # So autocast will only be active if we have a cuda device.
        with autocast(self.device.type, enabled=True) if self.device.type == 'cuda' else dummy_context():
            output, cls_output = self.network(data)
            del data
            seg_loss = self.loss(output, target)
            cls_loss = self.cls_loss(cls_output, cls_target)
            l = self.alpha * cls_loss + (1 - self.alpha) * seg_loss

        # we only need the output with the highest output resolution (if DS enabled)
        if self.enable_deep_supervision:
            output = output[0]
            target = target[0]

        # the following is needed for online evaluation. Fake dice (green line)
        axes = [0] + list(range(2, output.ndim))

        if self.label_manager.has_regions:
            predicted_segmentation_onehot = (torch.sigmoid(output) > 0.5).long()
        else:
            # no need for softmax
            output_seg = output.argmax(1)[:, None]
            predicted_segmentation_onehot = torch.zeros(output.shape, device=output.device, dtype=torch.float32)
            predicted_segmentation_onehot.scatter_(1, output_seg, 1)
            del output_seg

        if self.label_manager.has_ignore_label:
            if not self.label_manager.has_regions:
                mask = (target != self.label_manager.ignore_label).float()
                # CAREFUL that you don't rely on target after this line!
                target[target == self.label_manager.ignore_label] = 0
            else:
                if target.dtype == torch.bool:
                    mask = ~target[:, -1:]
                else:
                    mask = 1 - target[:, -1:]
                # CAREFUL that you don't rely on target after this line!
                target = target[:, :-1]
        else:
            mask = None

        tp, fp, fn, _ = get_tp_fp_fn_tn(predicted_segmentation_onehot, target, axes=axes, mask=mask)

        tp_hard = tp.detach().cpu().numpy()
        fp_hard = fp.detach().cpu().numpy()
        fn_hard = fn.detach().cpu().numpy()
        if not self.label_manager.has_regions:
            # if we train with regions all segmentation heads predict some kind of foreground. In conventional
            # (softmax training) there needs tobe one output for the background. We are not interested in the
            # background Dice
            # [1:] in order to remove background
            tp_hard = tp_hard[1:]
            fp_hard = fp_hard[1:]
            fn_hard = fn_hard[1:]

        return {'loss': l.detach().cpu().numpy(), 'tp_hard': tp_hard, 'fp_hard': fp_hard, 'fn_hard': fn_hard}