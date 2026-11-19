"""Deterministic storage-precision transformations used in robustness checks."""
from __future__ import annotations


def fp16_roundtrip_state_dict(state_dict):
    """Return a copy where floating tensors are float16-round-tripped to their original dtype."""
    out = {}
    for name, value in state_dict.items():
        v = value.detach().clone()
        if getattr(v.dtype, "is_floating_point", False):
            v = v.to(dtype=__import__("torch").float16).to(dtype=value.dtype)
        out[name] = v
    return out
