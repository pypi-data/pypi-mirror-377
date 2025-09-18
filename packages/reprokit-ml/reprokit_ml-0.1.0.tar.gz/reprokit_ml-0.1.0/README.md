# ReproKit-ML

**One-command determinism + manifest for ML projects.**

```bash
pip install reprokit-ml
reprokit init --data ./data
reprokit seed --seed 42
reprokit env-freeze
reprokit hash-data ./data --exclude "**/.ipynb_checkpoints/**"
reprokit manifest --config conf/train.yaml
```

- Deterministic seeds for **Torch/TF/JAX** (opt-in per framework)
- Environment freeze (pip/conda/poetry/uv) + **system/GPU** snapshot
- **Merkle data hash** with fast sampled hashing + cache
- Single **manifest.json** that binds code commit + env + data + seeds + config

> Scope is intentionally narrow: one-command determinism + manifest. Use MLflow/W&B for tracking, DVC for dataset versioning/remotes.
