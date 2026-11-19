# EntropySeal

[![Release audit](https://github.com/niehewang/EntropySeal/actions/workflows/release-audit.yml/badge.svg)](https://github.com/niehewang/EntropySeal/actions/workflows/release-audit.yml)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![PyTorch 1.11](https://img.shields.io/badge/PyTorch-1.11-ee4c2c.svg)](https://pytorch.org/)

EntropySeal is a research implementation for **checkpoint-intrinsic ownership signals in strict-lossless learned image compression**. It embeds a small owner-specific carrier into a frozen checkpoint and verifies ownership from black-box residual codelength responses, without adding a keyed module to the deployed codec.

## What is released

- `src/entropyseal/`: compact reference implementation of checkpoint marking, FP16 profile construction, and codelength-profile decisions.
- `experiments/`: public reproduction utilities for checkpoint marking, precision round-trip, profile verification, and reduced-query replay.
- `configs/reproduction.json`: the frozen public reproduction contract (upstream commit/hash contract, carrier coordinates/vectors, alpha, thresholds, environment, seeds, and calibration schedule).
- `reference/`: compact registered owner templates/threshold metadata; third-party images are **not** redistributed.
- `evidence/`: compact numerical evidence needed to check the released decision logic without model execution.
- `scripts/release_audit.py`: fail-closed repository leakage audit used by CI.

## Scientific contract

The primary released configuration uses five scalar coordinates of `residual_compressor.layers.2.bias` (indices 45–49), carrier amplitude `alpha=0.03`, and four owner carriers (`K0`–`K3`). Verification compares a suspect residual-payload vector with registered FP32/FP16 profiles using two frozen thresholds per owner: mismatch count and mean absolute codelength difference. An owner is accepted when either registered precision profile passes both thresholds.

The exact numerical contract is machine-readable in `configs/reproduction.json`.

## Upstream dependency

The experiments use `BYchao100/Deep-Lossy-Plus-Residual-Coding` at commit `fb6a9d9d4be55b0fc11afea3b406ddebd67f41e3`. The upstream source and pretrained checkpoint are not vendored here. Before a model run, verify them with:

```bash
python scripts/verify_assets.py \
  --upstream /path/to/Deep-Lossy-Plus-Residual-Coding \
  --checkpoint /path/to/ckp.tar
```

The expected checkpoint SHA-256 and tracked source-file hashes are stored in `configs/reproduction.json`.

## Environment

The frozen environment used for the model experiments was Python 3.9, PyTorch 1.11.0, torchvision 0.12.0, CUDA runtime 11.3, NumPy 1.23.5, CompressAI 1.2.0, torchac 0.9.3, and timm 0.5.4. These versions are documented for faithful reproduction; the lightweight decision-rule utilities require only Python.

## Minimal validation

The following path requires no model weights or private assets:

```bash
python -m compileall -q src experiments scripts tests
python -m unittest discover -s tests -v
python scripts/release_audit.py
python experiments/query_budget.py --help
```

These commands compile the public surface, run lightweight tests, run the fail-closed release audit, and show the reduced-query replay interface.

## Full model reproduction

1. Obtain the upstream repository and its pretrained lossless checkpoint from the upstream project and verify the hashes.
2. Obtain the public datasets from their official sources. No raw dataset images are stored in this repository.
3. Use the frozen settings in `configs/reproduction.json` and the environment documented in `docs/reproducibility.md`.
4. Use the public utilities in `experiments/` together with locally obtained upstream assets and public datasets. Raw internal orchestration/return packages are intentionally not part of the public API.

## Data and model policy

This repository does not redistribute the upstream model checkpoint, the upstream source snapshot, DIV2K, Kodak, CLIC images, raw experiment logs, caches, or training checkpoints. See `docs/assets.md`.

## Reproducibility boundary

The repository distinguishes three layers:

1. **Core method** — small, readable code in `src/entropyseal/`.
2. **Public reproduction utilities** — portable entry points for the frozen scientific operations.
3. **Compact evidence** — final numerical summaries, without raw return archives or machine-specific logs.

This separation keeps the public release portable while preserving the scientific settings that determine the reported results.

## Security and scope

Do not commit credentials, machine-specific paths, private datasets, model checkpoints, or private infrastructure identifiers. `scripts/release_audit.py` enforces these constraints in CI. Security reports should use the repository's private vulnerability-reporting channel when available.

## Citation and license

Citation metadata and a software license are intentionally not asserted in this staging release. They should be added only after the authors and license terms are explicitly finalized. Third-party components remain under their own licenses.
