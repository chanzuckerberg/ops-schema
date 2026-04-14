# OPS Data Standard — Changelog

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Appendix A: Changelog

### v0.1.0 (current draft)

**Cross-file linkage**
- Replaced opaque `id` field in Perturbation Library with `perturbation_id`, a submitter-defined stable identifier (SHOULD be based on `gene_id` or `gene_symbol`). Multiple sgRNAs targeting the same gene share the same `perturbation_id`. `barcode` is now the explicit per-sgRNA primary key. `perturbation_id` MUST NOT change after submission.
- Renamed `gene_symbol` → `gene_id` in Perturbation Library (it stored Ensembl IDs); added `gene_symbol` for human-readable symbols (e.g., `"BRCA2"`)
- Promoted `unique_cell_uid` → `cell_uid` as REQUIRED in scFeature Table; globally unique cell identifier across experiments
- Renamed `genetic_perturbation_id` → `perturbation_id` in scFeature Table
- Added cross-file linkage diagram to Data Model Overview

**Collection tier**
- Introduced Collection as the top-level submission tier (Collection → Experiment → Visualization)
- Added `collection_metadata.yaml` with `collection.title`, `collection.publication_doi`
- Removed `experiment.publication_doi` and `experiment.publication_reference` from experimental metadata

**Aggregated Data (h5ad)**
- Replaced `perturbation_id` as obs index with `aggregate_id` — a submitter-constructed unique key derived from the columns listed in `uns['observation_unit']`, joined with `|` (pipe). Supports gene-level, guide-level, and arbitrary stratified pseudobulk (e.g., gene × cell cycle phase).
- `perturbation_id` is now an obs column (FK to `perturbation_library.csv`), no longer the index. Not necessarily unique per row.
- Added `observation_unit` to `uns` (REQUIRED). Declares which column(s) define each aggregation row. Column values concatenated with `|` must equal the corresponding `aggregate_id`.
- Removed `cell_cycle_phase` as a special-cased obs field — now handled generically via `observation_unit`.
- Corrected AnnData structure to match CELLxGENE conventions: `X` matrix is `Float32 (n_obs × n_features)`; `p_values` moved to `layers`; `uns` section added with `schema_version`, `default_embedding`, `title`

**Example Images**
- Reorganized Zarr hierarchy from `{gene_symbol}/{barcode}/{1..N}` to `{perturbation_id}/{barcode}/{1..N}/`

**Validation rules**
- Added V-1b: `tissue_type = "cell line"` requires Cellosaurus (`CVCL_XXXXX`) term for `tissue_ontology_term_id` and `development_stage_ontology_term_id` MUST be `"na"`
- Removed V-5 (consolidated into V-1b)
- Updated V-6 to reference Zarr multiscales z-axis coordinate transformations instead of removed `phenotype.z_slices` / `phenotype.z_interval`
- Updated V-9 to reference `perturbation_id`

**Metadata deduplication**
- Removed `cellular.cell_line` (covered by `tissue_ontology_term_id` Cellosaurus term)
- Removed `phenotype.channels`, `phenotype.z_slices`, `phenotype.z_interval` (all covered by OME-NGFF Zarr metadata)
- Added `phenotype.exposure_time_ms` as a standalone list field (not in OME-NGFF v0.5)
- Added Cellosaurus (CVCL) to ontology dependencies table

**Zarr Images**
- Resolved Pending Item #3: `"cell line"` adopted as a valid `tissue_type` value
- Relaxed codec requirement: `zstd` recommended; `blosc/zstd` accepted for writers lacking native `zstd` support; `lz4` permitted where performance requires it
- Added compression reference link for Level 7 array spec

**Pending items resolved**
- Item #1: Perturbation Library fields aligned to CELLxGENE schema v7.1.0
- Item #3: `"cell line"` adopted as valid `tissue_type`; `"organelle"` remains out of scope
- Item #4: `barcode` and `protospacer_sequence` character and length constraints defined

**Still pending before v1.0.0**
- Item #2: Aggregated Data full field specification (awaiting CELLxGENE schema team alignment)
- Item #6: Example Images array shape/dtype requirements
- Item #7: Exhaustive enum for `channels_metadata[].channel_type`
- Item #8: Exhaustive enum for `segmentation_metadata.annotation_type` (examples expanded; needs follow-up on event-based annotations e.g. apoptosis, mitosis)
- Item #9: Specimen-level metadata (cell line authentication, passage number, mycoplasma testing)

**Pending items resolved (continued)**
- Item #5: `cell_seq_id` removed — redundant with `cell_uid` which is reconstructable from the Zarr hierarchy. `cell_uid` changed from Integer to String (format: `{plate}_{well}_{tile}_{cell_id}`)
- Removed `segmentation_metadata.source_channel.name` and `source_channel.type` — redundant with `channels_metadata[]` at the Zarr plate root; `source_channel.index` alone is the FK

**Out of scope for v0.1.0:** 3D imaging, time-series data, chemical perturbations
