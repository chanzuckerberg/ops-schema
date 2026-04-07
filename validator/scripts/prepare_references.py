"""
Download and prepare reference files for the OPS validator.

Run once before using the validator:
    python scripts/prepare_references.py

Downloads:
  - OBO ontology files (CL, UBERON, MONDO, PATO, HsapDv, MmusDv, EFO, Cellosaurus)
  - GENCODE v48 (GRCh38) gene annotation -> parquet

All files are saved to src/ops_validator/reference_files/.
"""

from __future__ import annotations

import gzip
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests
import yaml

REFERENCE_DIR = Path(__file__).parent.parent / "src" / "ops_validator" / "reference_files"
GENE_INFO_PATH = REFERENCE_DIR / "gene_info.yml"

OBO_SOURCES: dict[str, str] = {
    "cl.obo.gz": "http://purl.obolibrary.org/obo/cl.obo",
    "uberon.obo.gz": "http://purl.obolibrary.org/obo/uberon.obo",
    "mondo.obo.gz": "http://purl.obolibrary.org/obo/mondo.obo",
    "pato.obo.gz": "http://purl.obolibrary.org/obo/pato.obo",
    "hsapdv.obo.gz": "http://purl.obolibrary.org/obo/hsapdv.obo",
    "mmusdv.obo.gz": "http://purl.obolibrary.org/obo/mmusdv.obo",
    "efo.obo.gz": "https://www.ebi.ac.uk/efo/efo.obo",
    "cellosaurus.obo.gz": "https://ftp.expasy.org/databases/cellosaurus/cellosaurus.obo",
}


def download_and_compress(url: str, dest: Path, force: bool = False) -> None:
    if dest.exists() and not force:
        print(f"  Already exists: {dest.name} - skipping")
        return
    print(f"  Downloading {dest.name} from {url} ...")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    with gzip.open(dest, "wb") as out:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            out.write(chunk)
    print(f"  Saved: {dest}")


def _load_gene_info() -> dict:
    """Load gene_info.yml configuration."""
    with open(GENE_INFO_PATH) as f:
        return yaml.safe_load(f)


def _parse_gtf_genes(gtf_bytes: bytes) -> list[dict[str, str]]:
    """Parse a GENCODE GTF (gzipped bytes) and extract unique gene records.

    Filters out PAR_Y gene entries (same convention as CellxGene).
    Returns list of dicts with keys: gene_id, gene_name.
    """
    seen: set[str] = set()
    genes: list[dict[str, str]] = []

    with gzip.open(io.BytesIO(gtf_bytes), "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            feature_type = parts[2]
            if feature_type != "gene":
                continue

            attrs_str = parts[8]

            gene_id_raw = _extract_attr(attrs_str, "gene_id")

            if not gene_id_raw:
                continue

            # Filter genes suffixed with "PAR_Y" (same as CxG)
            if gene_id_raw.endswith("PAR_Y"):
                continue

            gene_name = _extract_attr(attrs_str, "gene_name")

            # Strip version suffix (e.g. ENSG00000186092.7 -> ENSG00000186092)
            gene_id = gene_id_raw.split(".")[0]

            if gene_id in seen:
                continue
            seen.add(gene_id)

            genes.append(
                {
                    "gene_id": gene_id,
                    "gene_name": gene_name or gene_id,
                }
            )

    return genes


def _extract_attr(attrs_str: str, key: str) -> str | None:
    """Extract a GTF attribute value by key."""
    # GTF attributes look like: gene_id "ENSG00000186092.7"; gene_name "OR4F5";

    match = re.search(rf'{key}\s+"([^"]+)"', attrs_str)
    return match.group(1) if match else None


def download_gencode_gene_table(
    organism_info: dict, dest: Path, force: bool = False
) -> None:
    if dest.exists() and not force:
        print(f"  Already exists: {dest.name} -- skipping")
        return

    version = str(organism_info["version"])
    url = organism_info["url"].format(version=version)

    print(f"  Downloading GENCODE v{version} GTF from {url} ...")
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()

    raw = b""
    for chunk in resp.iter_content(chunk_size=1024 * 1024):
        raw += chunk

    print(f"  Parsing GTF ({len(raw) / 1024 / 1024:.1f} MB compressed) ...")
    genes = _parse_gtf_genes(raw)

    df = pd.DataFrame(genes)
    df = df[df["gene_id"].str.startswith("ENS", na=False)]

    if len(df) < 20_000:
        raise ValueError(
            f"GENCODE GTF returned only {len(df)} gene entries -- expected ~60,000+."
        )

    df.to_parquet(dest, index=False)
    print(f"  Saved: {dest} ({len(df):,} genes)")


def main(force: bool = False) -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Downloading OBO ontology files ===")
    for filename, url in OBO_SOURCES.items():
        dest = REFERENCE_DIR / filename
        try:
            download_and_compress(url, dest, force=force)
        except Exception as e:
            print(f"  ERROR downloading {filename}: {e}")

    print("\n=== Downloading GENCODE gene references ===")
    gene_info = _load_gene_info()
    for key, organism_info in gene_info.items():
        description = organism_info["description"]
        dest = REFERENCE_DIR / f"genes_{description}.parquet"
        try:
            download_gencode_gene_table(organism_info, dest, force=force)
        except Exception as e:
            print(f"  ERROR downloading {key}: {e}")

    print("\nDone. Reference files are ready.")


if __name__ == "__main__":
    force = "--force" in sys.argv
    main(force=force)
