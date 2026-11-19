# Reproducibility guide

The public repository separates the small reference implementation from the exact environment/assets used for full model execution.

## Frozen assets

The upstream codec commit, source-checkpoint SHA-256, tracked source-file hashes, carrier tensor/indices/vectors, alpha, thresholds, clean-rate schedule, and reduced-query protocol are recorded in `configs/reproduction.json`.

The upstream source snapshot, pretrained checkpoint, raw dataset images, return archives, caches, and derived checkpoints are intentionally not redistributed. Use `python scripts/verify_assets.py` to verify locally obtained upstream assets.

## Environment

The frozen model environment used Python 3.9, PyTorch 1.11.0, torchvision 0.12.0, CUDA 11.3, NumPy 1.23.5, CompressAI 1.2.0, torchac 0.9.3, and timm 0.5.4.

## Public experiment utilities

- `experiments/mark_checkpoint.py`: apply an owner carrier to the frozen checkpoint tensor and verify the expected output hash when requested.
- `experiments/verify_profiles.py`: evaluate black-box residual-codelength vectors against registered FP32/FP16 profiles using the frozen owner thresholds.
- `experiments/fp16_roundtrip.py`: deterministic storage-precision round-trip for checkpoint robustness evaluation.
- `experiments/query_budget.py`: reproduce reduced-query decisions from caller-supplied codelength vectors and challenge hashes using the frozen order rule.

The compact `evidence/` tables preserve final numerical summaries. Internal orchestration names, machine paths, raw logs, and temporary return packages are deliberately excluded from the public surface.

## Negative result

The mild-copy robustness condition is retained in `evidence/summary.json` as a negative result rather than being silently removed or rewritten.
