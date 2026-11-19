#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import torch

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/reproduction.json").read_text())

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--owner", choices=sorted(CFG["carrier"]["vectors"]), required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--alpha", type=float, default=None)
    ap.add_argument("--verify-frozen-hash", action="store_true")
    args = ap.parse_args()
    expected_source = CFG["upstream"]["source_checkpoint_sha256"]
    got_source = sha256(args.checkpoint)
    if got_source != expected_source:
        raise SystemExit(f"source checkpoint hash mismatch: {got_source}")
    obj = torch.load(args.checkpoint, map_location="cpu")
    state = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    name = CFG["carrier"]["target_tensor"]
    idx = CFG["carrier"]["target_indices"]
    alpha = CFG["carrier"]["alpha"] if args.alpha is None else float(args.alpha)
    v = CFG["carrier"]["vectors"][args.owner]
    tensor = state[name]
    carrier = torch.tensor(v, dtype=tensor.dtype, device=tensor.device)
    tensor[idx] = tensor[idx] + alpha * carrier
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(obj, args.output)
    out_hash = sha256(args.output)
    print(json.dumps({"owner": args.owner, "alpha": alpha, "sha256": out_hash}, indent=2))
    if args.verify_frozen_hash and alpha == CFG["carrier"]["alpha"]:
        expected = CFG["carrier"]["expected_marked_checkpoint_sha256"][args.owner]
        if out_hash != expected:
            raise SystemExit(f"marked checkpoint hash mismatch: {out_hash} != {expected}")

if __name__ == "__main__":
    main()
