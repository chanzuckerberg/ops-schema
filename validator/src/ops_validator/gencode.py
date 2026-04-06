"""
GENCODE gene reference validation (pinned to GENCODE v48 / GRCh38).

Validates:
- gene_id: version-stripped Ensembl gene IDs
- gene_symbol: gene names matching the GENCODE v48 annotation
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

REFERENCE_DIR = Path(__file__).parent / "reference_files"
GENCODE_FILE = REFERENCE_DIR / "gencode_v48_human.parquet"

GENCODE_RELEASE = "48"
GENOME_ASSEMBLY = "GRCh38"


@lru_cache(maxsize=1)
def _load_gene_table() -> pd.DataFrame:
    return pd.read_parquet(GENCODE_FILE)


@lru_cache(maxsize=1)
def _gene_id_set() -> set[str]:
    return set(_load_gene_table()["gene_id"].values)


@lru_cache(maxsize=1)
def _gene_id_to_name() -> dict[str, str]:
    df = _load_gene_table()
    return dict(zip(df["gene_id"], df["gene_name"]))


def gene_id_exists(gene_id: str) -> bool:
    """Return True if gene_id is present in GENCODE v48."""
    return gene_id in _gene_id_set()


def gene_symbol_matches(gene_id: str, gene_symbol: str) -> bool:
    """Return True if gene_symbol matches the GENCODE v48 gene_name for gene_id."""
    return _gene_id_to_name().get(gene_id) == gene_symbol


def get_gene_symbol(gene_id: str) -> str | None:
    """Return the GENCODE v48 gene_name for gene_id, or None if not found."""
    return _gene_id_to_name().get(gene_id)


def validate_var_index(gene_ids: list[str]) -> list[str]:
    """
    Validate a list of Ensembl gene IDs from an AnnData var index.
    Returns a list of invalid IDs (empty list means all valid).
    """
    valid = _gene_id_set()
    return [gid for gid in gene_ids if gid not in valid]
