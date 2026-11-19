"""Checkpoint-intrinsic carrier used by the released experiments.

The public release stores the frozen five-dimensional carrier vectors directly.
This avoids exposing internal experiment labels while preserving the exact numerical
perturbations used to build the released checkpoint conditions.
"""
from __future__ import annotations
from typing import Mapping, MutableMapping

TARGET_TENSOR = "residual_compressor.layers.2.bias"
TARGET_INDICES = (45, 46, 47, 48, 49)
DEFAULT_ALPHA = 0.03
CARRIER_VECTORS = {'K0': [0.8605126621622845, 0.17684973788329592, -0.916840094108144, 1.239812605937006, -1.3603349118744426], 'K1': [-1.7269795652141873, -0.1553556712943991, 0.702295037067499, 1.2240313147203905, -0.043991115279302585], 'K2': [-0.4704052118918604, -1.3046559993675404, -0.5353958292108658, 0.9094266711029954, 1.4010303693672712], 'K3': [-1.5543157003361512, 1.3508342523189547, -0.2496399905795522, -0.31858599604341176, 0.7717074346401605]}


def apply_carrier_to_state_dict(state_dict: MutableMapping, owner: str, alpha: float = DEFAULT_ALPHA,
                                target_tensor: str = TARGET_TENSOR):
    """Apply the frozen owner carrier in place and return ``state_dict``.

    ``state_dict[target_tensor]`` is expected to be a PyTorch tensor. Exactly five
    scalar coordinates are changed; no runtime codec hook is introduced.
    """
    if owner not in CARRIER_VECTORS:
        raise KeyError(f"unknown owner: {owner}")
    if target_tensor not in state_dict:
        raise KeyError(f"missing tensor: {target_tensor}")
    tensor = state_dict[target_tensor]
    if tensor.ndim != 1 or tensor.shape[0] <= TARGET_INDICES[-1]:
        raise ValueError(f"unexpected target shape: {tuple(tensor.shape)}")
    import torch
    h = torch.tensor(CARRIER_VECTORS[owner], dtype=tensor.dtype, device=tensor.device)
    tensor[list(TARGET_INDICES)] = tensor[list(TARGET_INDICES)] + float(alpha) * h
    return state_dict
