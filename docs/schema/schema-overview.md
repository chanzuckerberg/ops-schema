# OPS Data Schema: Technical Specification

## Overview

The Optical Pooled Screening (OPS) Data Standard (v0.1.0) is an open specification for standardizing how multimodal genetic perturbation screening data is organized, validated, and shared. It enables seamless aggregation of OPS experiments across labs and makes data model-ready for AI applications.

### Core Principles

1. **Standardization** — Consistent schema ensures compatibility across labs and tools
2. **Accessibility** — Clear specifications enable automated validation and tool development
3. **Interoperability** — Built on established standards (Zarr, OME-NGFF, AnnData, Parquet)
4. **Extensibility** — Versioned schema allows growth while maintaining backward compatibility

---

## Data Model Hierarchy

Collection [1 per submission; groups experiments from a single publication]
└── Experiment (Screen) [1 or more per collection]
└── Visualization (Subset) [1 or more per experiment]

### Key Relationships

All artifacts are connected via stable identifier fields:

- `perturbation_id` — stable join key linking sgRNAs targeting the same gene
- `barcode` — per-sgRNA primary key (unique within experiment)
- `cell_uid` — globally unique cell identifier
- `aggregate_id` — index into aggregated data

---

## Required Artifacts

### Level 0: Visualization Layer (Required for Web Portal)

| Artifact | Scope | Purpose |
|----------|-------|---------|
| Collection Metadata | Per collection | Publication, contacts, governance |
| Experimental Metadata | Per experiment | Screen design, cell line, protocols |
| Perturbation Library | Per experiment | sgRNA→gene mappings, controls |
| Example Images | Per visualization | Representative crops for display |
| Aggregated Data | Per visualization | UMAP, gene expression, feature statistics |

### Level 1: Data Sharing Layer (The Standard)

| Artifact | Format | Scope |
|----------|--------|-------|
| scFeature Table | Parquet | Per experiment; one row per cell |
| Zarr Images | Zarr v3 + OME-NGFF | Per experiment; all raw/processed images |
| (Optional) Feature Definitions | CSV | Per experiment; custom feature metadata |

---

## File Structure

A complete OPS submission follows this directory layout:
{collection_root}/
├── collection_metadata.yaml
└── {screen_name}/
├── metadata/
│   ├── experimental_metadata.yaml
│   ├── perturbation_library.csv
│   └── feature_definitions.csv (optional)
├── cell_data.parquet
├── {screen_name}.zarr
└── visualizations/
└── {visualization_id}/
├── aggregated_data.h5ad
└── examples.zarr

---

## Key Validation Rules

Before submission, all data MUST pass these cross-artifact checks:

| Rule | Condition | Requirement |
|------|-----------|-------------|
| V-1 | Cell culture data | Tissue must be specific Cell Ontology (CL) term |
| V-1b | Cell line data | Tissue must be Cellosaurus (CVCL) accession |
| V-2 | Tissue/organoid data | Use most accurate UBERON anatomy term |
| V-3 | *Homo sapiens* | Development stage from HsapDv ontology |
| V-4 | *Mus musculus* | Development stage from MmusDv ontology |
| V-6 | Multi-slice Z-stack | Z-axis scale and unit MUST be specified |
| V-7 | Multiple visualizations | Cell class MUST disambiguate visualization assignment |
| V-9 | Perturbation data | Only human, mouse, or zebrafish in v0.1.0 |
| V-10 | Control perturbations | Control type MUST be "non-targeting" or "intergenic" |
| V-12 | Aggregated data | At least one control perturbation MUST be present |
| V-13 | Multi-dimensional observation units | Examples.zarr MUST nest all unit columns correctly |
| V-14 | `n_cells` field | Count MUST match cell_data rows for observation units |

---

## Dependencies & Versions

### Format Standards

| Specification | Version | Use |
|---------------|---------|-----|
| Zarr | v3 | Image and feature storage |
| OME-NGFF | v0.5 | Image metadata and multiscales |
| AnnData | v0.10+ | Aggregated feature tables |
| Parquet | v2.6 | Cell-level data |

### Ontologies (Versions TBD before v1.0.0)

- **Cellosaurus** (CVCL) — Cell line identification
- **Cell Ontology** (CL) — Cell type specification
- **Experimental Factor Ontology** (EFO) — Experimental design
- **Human Developmental Stages** (HsapDv) — Human life cycle stages
- **Mondo Disease Ontology** (MONDO) — Disease classification
- **Mouse Developmental Stages** (MmusDv) — Mouse life cycle stages
- **NCBI Taxonomy** (NCBITaxon) — Organism classification
- **Phenotype & Trait Ontology** (PATO) — Phenotype annotation
- **Uberon** (UBERON) — Anatomical structures

---

## Multimodal Experiments (e.g., CROP-seq)

For experiments combining OPS imaging with paired transcriptomics (CROP-seq):

1. **No separate YAML** for sequencing data — all CROP-seq metadata goes in `experimental_metadata.yaml` under `experiment.crop_seq_anndata`
2. **Create a visualization entry** for CROP-seq data with `aggregated_data.h5ad` (but NO `examples.zarr`)
3. **Include CROP-seq in pseudobulk** — add `"crop_seq"` to `experiment.pseudobulk` cell state labels if applicable

---

## Schema Versioning

The OPS schema follows [Semantic Versioning](https://semver.org/):

- **Major version** (breaking changes) — Renaming/removing fields or changing types
- **Minor version** (additive changes) — New optional fields or looser validation
- **Patch version** (editorial) — Documentation or typo fixes

All changes are documented in the [Schema Changelog](https://github.com/chanzuckerberg/ops-schema/blob/main/standards/ops/0.1.0/changelog.md).

---

## Submission Workflow

1. **Format** your data to the directory structure above
2. **Validate** using the published validation tools (coming soon)
3. **Contact** the OPS Explorer team to discuss onboarding
4. **Deposit** to the centralized repository
5. **Receive** a citable collection page and public access link

---

## Questions & Issues

- GitHub Issues: [OPS Schema Repo](https://github.com/chanzuckerberg/ops-schema/issues)
- Questions: [contact email TBD]

---

## Acknowledgments

The OPS Data Standard builds on [OME-Zarr](https://ngff.openmicroscopy.org/) and the [`ome-zarr-py`](https://github.com/ome/ome-zarr-py) reference implementation (BSD 2-Clause License). We are grateful to the OME community for establishing open standards for bioimaging data.
