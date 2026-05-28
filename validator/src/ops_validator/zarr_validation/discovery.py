"""
Discover Zarr store roots under a local path or an S3 URL.

A directory is treated as a Zarr store root if it contains zarr.json at its
top level.  Nested stores (multiscale sub-arrays) are excluded — only the
outermost group root is returned.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import s3fs


def _is_s3(path: str) -> bool:
    return path.startswith("s3://")


def _discover_local(root: str) -> list[str]:
    """Walk a local directory tree and return Zarr store roots."""
    stores: list[str] = []
    root_path = Path(root)

    for dirpath, dirnames, filenames in os.walk(root_path):
        if "zarr.json" in filenames:
            stores.append(str(dirpath))
            # Do not descend into sub-groups of this store; they are not
            # independent stores.  Clear dirnames in-place so os.walk skips them.
            dirnames.clear()

    return stores


def _discover_s3_walk(root: str) -> list[str]:
    """Return Zarr store roots under an S3 prefix using fs.walk().

    BFS: one ListObjectsV2-with-delimiter call per directory level.
    Prunes descent into a store once its root is found, so it avoids
    enumerating internal sub-groups.  More efficient for single/few plates;
    less efficient for deeply nested or widely scattered single images.
    """
    fs = s3fs.S3FileSystem(anon=False)
    prefix = root.rstrip("/").removeprefix("s3://")

    stores: list[str] = []
    for dirpath, dirnames, filenames in fs.walk(prefix):
        if "zarr.json" in filenames:
            stores.append("s3://" + dirpath)
            dirnames.clear()
    return stores


def _discover_s3_glob(root: str) -> list[str]:
    """Return Zarr store roots under an S3 prefix using a single flat glob scan.

    Issues one paginated ListObjectsV2 (no delimiter) for the entire prefix,
    returning all keys before filtering outermost store roots in memory.
    More efficient for deeply nested or widely scattered single images;
    less efficient for large plates where all internal objects are returned
    before filtering can occur.
    """
    fs = s3fs.S3FileSystem(anon=False)

    # Strip trailing slash and s3:// for consistent key handling
    prefix = root.rstrip("/")
    bucket_prefix = prefix.removeprefix("s3://")

    # s3fs glob("prefix/**/zarr.json") may or may not match "prefix/zarr.json"
    # depending on the s3fs version (** sometimes requires at least one segment).
    # Check the root explicitly to be safe, then deduplicate.
    all_keys: list[str] = []
    if fs.exists(f"{bucket_prefix}/zarr.json"):
        all_keys.append(f"{bucket_prefix}/zarr.json")
    all_keys.extend(fs.glob(f"{prefix}/**/zarr.json"))

    # Deduplicate (root may appear from both explicit check and glob).
    all_keys = list(dict.fromkeys(all_keys))

    # Sort by depth first (fewest slashes = outermost), then alphabetically.
    # Alphabetical-only sorting can place deep paths before shallow siblings
    # (e.g. "labels/nuclei/0" before "labels"), breaking the ancestor filter.
    all_keys.sort(key=lambda k: (k.count("/"), k))

    # The store root is the parent directory of zarr.json
    seen: set[str] = set()
    stores: list[str] = []
    for key in all_keys:
        store_key = key[: -len("/zarr.json")]  # parent of zarr.json
        # Keep only outermost: skip if any ancestor is already a store
        if any(store_key.startswith(s + "/") for s in seen):
            continue
        seen.add(store_key)
        stores.append("s3://" + store_key)

    return stores


def is_zarr_store(path: str) -> bool:
    """
    Return True if `path` is itself a Zarr store root (has zarr.json at its top level).

    Does not recurse.  Used by the runner to skip discovery when the caller
    supplies an exact store path rather than a parent directory.
    """
    if _is_s3(path):
        fs = s3fs.S3FileSystem(anon=False)
        key = path.rstrip("/").removeprefix("s3://") + "/zarr.json"
        return bool(fs.exists(key))
    return (Path(path) / "zarr.json").exists()


def discover_zarr_stores(
    root: str, strategy: Literal["glob", "walk"] = "glob"
) -> list[str]:
    """
    Return a flat list of Zarr store root paths found under `root`.

    Parameters
    ----------
    root     : local filesystem path or s3://bucket/prefix URL
    strategy : S3 discovery strategy — "glob" (default) or "walk".
               Ignored for local paths, which always use os.walk.

               "glob" issues a single paginated ListObjectsV2 scan and filters
               outermost roots in memory.  More efficient for deeply nested or
               widely scattered single images.

               "walk" uses BFS with per-level API calls, pruning descent once a
               store root is found.  More efficient for single/few plates where
               early pruning avoids enumerating internal sub-groups.
    """
    if _is_s3(root):
        if strategy == "glob":
            return _discover_s3_glob(root)
        if strategy == "walk":
            return _discover_s3_walk(root)
        raise ValueError(f"Invalid strategy {strategy!r}; expected 'glob' or 'walk'.")
    return _discover_local(root)
