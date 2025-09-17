from typing import Tuple

import torch
import numpy as np
from skimage.morphology import skeletonize, dilation

from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform
from npu.utils import convert_mask_to_dist

class LinearDecayDistanceTransformMap(BasicTransform):
    def __init__(self, s=10):
        super().__init__()
        self.s = s
    
    def apply(self, data_dict, **params):
        seg_all = data_dict['segmentation'].numpy()
        dist_all = convert_mask_to_dist(seg_all, None, self.s, uint8=False)
        data_dict["dist"] = torch.from_numpy(dist_all)
        return data_dict