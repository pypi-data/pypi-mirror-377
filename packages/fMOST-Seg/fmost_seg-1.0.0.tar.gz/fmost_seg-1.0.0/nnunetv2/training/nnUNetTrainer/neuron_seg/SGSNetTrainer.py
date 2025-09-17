from nnunetv2.training.nnUNetTrainer.nnUNetTrainerDist import nnUNetTrainerDist
from nnunetv2.training.nnUNetTrainer.neuron_seg.NeuronSegBaseTrainer import NeuronSegBaseTrainerNoDeepSupervision
import torch
from smz.models.sgsnet import SGSNet
from torch import autocast
from nnunetv2.utilities.helpers import empty_cache, dummy_context
from nnunetv2.training.loss.dice import MemoryEfficientSoftDiceLoss, get_tp_fp_fn_tn



class SGSNetTrainer(nnUNetTrainerDist, NeuronSegBaseTrainerNoDeepSupervision):
    @staticmethod
    def build_network_architecture(
        architecture_class_name, 
        arch_init_kwargs, 
        arch_init_kwargs_req_import, 
        num_input_channels, 
        num_output_channels, 
        enable_deep_supervision = True):
        return SGSNet(
            in_dim = num_input_channels,
            out_dim = num_output_channels,
            num_filters = 16
        )
    
    def train_step(self, batch: dict) -> dict:
        data = batch['data']
        target = batch['target']
        dist = batch['dist']

        # import napari
        # viewer = napari.Viewer()
        # viewer.add_image(data[0].cpu().numpy(), name='data')
        # viewer.add_image(target[0][0].cpu().numpy(), name='target')
        # viewer.add_image(skel[0][0].cpu().numpy(), name='skel')
        # napari.run()

        data = data.to(self.device, non_blocking=True)
        if isinstance(target, list):
            target = [i.to(self.device, non_blocking=True) for i in target]
            dist = [i.to(self.device, non_blocking=True) for i in dist]
        else:
            target = target.to(self.device, non_blocking=True)
            dist = dist.to(self.device, non_blocking=True)

        self.optimizer.zero_grad(set_to_none=True)
        # Autocast can be annoying
        # If the device_type is 'cpu' then it's slow as heck and needs to be disabled.
        # If the device_type is 'mps' then it will complain that mps is not implemented, even if enabled=False is set. Whyyyyyyy. (this is why we don't make use of enabled=False)
        # So autocast will only be active if we have a cuda device.
        with autocast(self.device.type, enabled=True) if self.device.type == 'cuda' else dummy_context():
            det_out, seg_out = self.network(data)
            # del data
            l = self.loss(seg_out, target, dist, det_out)

        if self.grad_scaler is not None:
            self.grad_scaler.scale(l).backward()
            self.grad_scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 12)
            self.grad_scaler.step(self.optimizer)
            self.grad_scaler.update()
        else:
            l.backward()
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 12)
            self.optimizer.step()
        return {'loss': l.detach().cpu().numpy()}
    

    def validation_step(self, batch: dict) -> dict:
        data = batch['data']
        target = batch['target']
        dist = batch['dist']

        data = data.to(self.device, non_blocking=True)
        if isinstance(target, list):
            target = [i.to(self.device, non_blocking=True) for i in target]
            dist = [i.to(self.device, non_blocking=True) for i in dist]
        else:
            target = target.to(self.device, non_blocking=True)
            dist = dist.to(self.device, non_blocking=True)

        # Autocast can be annoying
        # If the device_type is 'cpu' then it's slow as heck and needs to be disabled.
        # If the device_type is 'mps' then it will complain that mps is not implemented, even if enabled=False is set. Whyyyyyyy. (this is why we don't make use of enabled=False)
        # So autocast will only be active if we have a cuda device.
        with autocast(self.device.type, enabled=True) if self.device.type == 'cuda' else dummy_context():
            det_out, seg_out = self.network(data)
            del data
            l = self.loss(seg_out, target, dist, det_out)

        # we only need the output with the highest output resolution (if DS enabled)
        if self.enable_deep_supervision:
            seg_out = seg_out[0]
            target = target[0]

        # the following is needed for online evaluation. Fake dice (green line)
        axes = [0] + list(range(2, seg_out.ndim))

        if self.label_manager.has_regions:
            predicted_segmentation_onehot = (torch.sigmoid(seg_out) > 0.5).long()
        else:
            # no need for softmax
            output_seg = seg_out.argmax(1)[:, None]
            predicted_segmentation_onehot = torch.zeros(seg_out.shape, device=seg_out.device, dtype=torch.float32)
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