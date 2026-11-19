# Assets and redistribution boundary

The repository intentionally excludes all third-party raw images, model checkpoints, source snapshots, caches, and large training artifacts.

## Upstream codec

Use the upstream repository `BYchao100/Deep-Lossy-Plus-Residual-Coding` at the commit recorded in `configs/reproduction.json`. Follow the upstream project for checkpoint acquisition, then verify the local file against the SHA-256 stored in the reproduction config.

## Datasets

- **DIV2K**: required for the DIV2K validation crops and the clean-rate calibration stream.
- **Kodak Lossless True Color Image Suite**: required for cross-dataset evaluation.
- **CLIC validation data**: required for cross-dataset evaluation.

Only coordinate/hash manifests are released here. Users must obtain images from the official dataset providers and are responsible for their license/terms.
