"""
Download and prepare reference files for the OPS validator.

Run once before using the validator:
    python scripts/prepare_references.py

Downloads:
  - OBO ontology files (CL, UBERON, MONDO, PATO, HsapDv, MmusDv, EFO, Cellosaurus)
  - Ensembl 110 (GRCh38) gene table → parquet

All files are saved to src/ops_validator/reference_files/.
"""

from __future__ import annotations

import gzip
import io
import shutil
import sys
from pathlib import Path

import requests

REFERENCE_DIR = Path(__file__).parent.parent / "src" / "ops_validator" / "reference_files"

OBO_SOURCES: dict[str, str] = {
    "cl.obo.gz":         "http://purl.obolibrary.org/obo/cl.obo",
    "uberon.obo.gz":     "http://purl.obolibrary.org/obo/uberon.obo",
    "mondo.obo.gz":      "http://purl.obolibrary.org/obo/mondo.obo",
    "pato.obo.gz":       "http://purl.obolibrary.org/obo/pato.obo",
    "hsapdv.obo.gz":     "http://purl.obolibrary.org/obo/hsapdv.obo",
    "mmusdv.obo.gz":     "http://purl.obolibrary.org/obo/mmusdv.obo",
    "efo.obo.gz":        "https://www.ebi.ac.uk/efo/efo.obo",
    "cellosaurus.obo.gz": "https://ftp.expasy.org/databases/cellosaurus/cellosaurus.obo",
}

ENSEMBL_BIOMART_URL = (
    "https://sep2023.archive.ensembl.org/biomart/martservice"
    "?query=<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    "<!DOCTYPE Query>"
    "<Query virtualSchemaName=\"default\" formatter=\"TSV\" header=\"0\" uniqueRows=\"0\" count=\"\" datasetConfigVersion=\"0.6\">"
    "<Dataset name=\"hsapiens_gene_ensembl\" interface=\"default\">"
    "<Attribute name=\"ensembl_gene_id\"/>"
    "<Attribute name=\"external_gene_name\"/>"
    "</Dataset>"
    "</Query>"
)

ENSEMBL_REST_URL = (
    "https://sep2023.archive.ensembl.org/biomart/martservice?query="
    '%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E'
    '%3C%21DOCTYPE+Query%3E'
    '%3CQuery+virtualSchemaName%3D%22default%22+formatter%3D%22TSV%22+header%3D%221%22+uniqueRows%3D%221%22+count%3D%22%22+datasetConfigVersion%3D%220.6%22%3E'
    '%3CDataset+name%3D%22hsapiens_gene_ensembl%22+interface%3D%22default%22%3E'
    '%3CAttribute+name%3D%22ensembl_gene_id%22%2F%3E'
    '%3CAttribute+name%3D%22external_gene_name%22%2F%3E'
    '%3C%2FDataset%3E'
    '%3C%2FQuery%3E'
)


def download_and_compress(url: str, dest: Path, force: bool = False) -> None:
    if dest.exists() and not force:
        print(f"  Already exists: {dest.name} — skipping")
        return
    print(f"  Downloading {dest.name} from {url} ...")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    with gzip.open(dest, "wb") as out:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            out.write(chunk)
    print(f"  Saved: {dest}")


def download_ensembl_gene_table(dest: Path, force: bool = False) -> None:
    if dest.exists() and not force:
        print(f"  Already exists: {dest.name} — skipping")
        return

    try:
        import pandas as pd
    except ImportError:
        print("  pandas required — pip install pandas pyarrow")
        sys.exit(1)

    print("  Downloading Ensembl 110 gene table from BioMart ...")
    resp = requests.get(ENSEMBL_REST_URL, timeout=120)
    resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    rows = [line.split("\t") for line in lines[1:] if line]  # skip header
    df = pd.DataFrame(rows, columns=["gene_id", "gene_name"])
    df = df[df["gene_id"].str.startswith("ENSG")].drop_duplicates("gene_id").reset_index(drop=True)
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

    print("\n=== Downloading Ensembl 110 gene reference ===")
    ensembl_dest = REFERENCE_DIR / "ensembl_110_human.parquet"
    try:
        download_ensembl_gene_table(ensembl_dest, force=force)
    except Exception as e:
        print(f"  ERROR downloading Ensembl table: {e}")

    print("\nDone. Reference files are ready.")


if __name__ == "__main__":
    force = "--force" in sys.argv
    main(force=force)
