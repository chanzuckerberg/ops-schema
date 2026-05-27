"""
Shared numerical constants and small helpers for OPS Zarr-image validation.

Extracted so the v0.1 (and future) spec model modules can import them without
pulling in any DCA-specific code. Mirrors the values from the upstream DCA
spec where they coincide; OPS-only overrides live in the per-spec models.
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Size limits (bytes)
# ---------------------------------------------------------------------------

CHUNK_MIN_BYTES = 512 * 1024  # 512 KB — MUST
CHUNK_REC_BYTES = 1024 * 1024  # 1 MB   — SHOULD

SHARD_MIN_BYTES = 1024**3  # 1 GB    — MUST (when array >= 1 GB; DCA only)
SHARD_MAX_BYTES = 5 * 1024**4  # 5 TB    — MUST
SHARD_REC_BYTES = 5 * 1024**3  # 5 GB    — SHOULD

# ---------------------------------------------------------------------------
# Codecs
# ---------------------------------------------------------------------------

ALLOWED_CODECS = frozenset({"zstd", "lz4", "blosc"})
RECOMMENDED_CODEC = "zstd"
RECOMMENDED_LEVEL_MAX = 3

# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------

SPATIAL_AXES = {"z", "y", "x"}
NON_SPATIAL_AXES = {"t", "c"}

# ---------------------------------------------------------------------------
# Chunk / shard shape recommendations
# ---------------------------------------------------------------------------

SPATIAL_CHUNK_RECOMMENDED = 128  # SHOULD — each spatial dim
TC_CHUNK_RECOMMENDED = 1  # SHOULD — time and channel dims
SPATIAL_SHARD_MAX_RECOMMENDED = 2048  # SHOULD — each spatial shard dim
TIME_SHARD_MIN_RECOMMENDED = 16  # SHOULD — time shard dim

# ---------------------------------------------------------------------------
# Dtype recommendations
# ---------------------------------------------------------------------------

RAW_DTYPES_RECOMMENDED = frozenset({"uint8", "uint16"})
LABEL_DTYPE_RECOMMENDED = "uint32"

# ---------------------------------------------------------------------------
# Multiresolution
# ---------------------------------------------------------------------------

DOWNSAMPLING_FACTOR_RECOMMENDED = 2  # SHOULD — spatial dims


def _nbytes(shape: list[int], dtype: str) -> int:
    return math.prod(shape) * np.dtype(dtype).itemsize
