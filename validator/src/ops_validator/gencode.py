"""
Ensembl gene reference validation (pinned to Ensembl 110 / GRCh38.p14).

Validates:
- gene_id: version-stripped Ensembl gene IDs
- gene_symbol: HGNC-approved symbols matching the Ensembl 110 annotation
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

REFERENCE_DIR = Path(__file__).parent / "reference_files"
ENSEMBL_FILE = REFERENCE_DIR / "ensembl_110_human.parquet"

ENSEMBL_RELEASE = "110"
GENOME_ASSEMBLY = "GRCh38"


@lru_cache(maxsize=1)
def _load_gene_table() -> pd.DataFrame:
    if not ENSEMBL_FILE.exists():
        raise FileNotFoundError(
            f"Ensembl reference file not found: {ENSEMBL_FILE}\n"
            f"Run `python scripts/prepare_references.py` to download reference files."
        )
    return pd.read_parquet(ENSEMBL_FILE)


def gene_id_exists(gene_id: str) -> bool:
    """Return True if gene_id is present in Ensembl 110."""
    df = _load_gene_table()
    return gene_id in df["gene_id"].values


def gene_symbol_matches(gene_id: str, gene_symbol: str) -> bool:
    """Return True if gene_symbol matches the Ensembl 110 gene_name for gene_id."""
    df = _load_gene_table()
    row = df[df["gene_id"] == gene_id]
    if row.empty:
        return False
    return row.iloc[0]["gene_name"] == gene_symbol


def get_gene_symbol(gene_id: str) -> str | None:
    """Return the Ensembl 110 gene_name for gene_id, or None if not found."""
    df = _load_gene_table()
    row = df[df["gene_id"] == gene_id]
    if row.empty:
        return None
    return row.iloc[0]["gene_name"]


def validate_var_index(gene_ids: list[str]) -> list[str]:
    """
    Validate a list of Ensembl gene IDs from an AnnData var index.
    Returns a list of invalid IDs (empty list means all valid).
    """
    df = _load_gene_table()
    valid_ids = set(df["gene_id"].values)
    return [gid for gid in gene_ids if gid not in valid_ids]


def reference_present() -> bool:
    return ENSEMBL_FILE.exists()
