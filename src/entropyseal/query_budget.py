"""Deterministic reduced-query ordering used for the descriptive query-budget analysis."""
from __future__ import annotations
import hashlib


def ordered_indices(group: str, order_index: int, raw_rgb_sha256: list[str]) -> list[int]:
    keys=[]
    for i, digest in enumerate(raw_rgb_sha256):
        payload=f"ENTROPYSEAL_A5Q_ORDER_V1|{group}|{int(order_index)}|{digest}".encode("ascii")
        keys.append((hashlib.sha256(payload).digest(), i))
    return [i for _, i in sorted(keys)]
