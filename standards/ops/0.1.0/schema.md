# Optical Pooled Screening (OPS) Data Standard

Contact: [TBD]@chanzuckerberg.com

Document Status: _Draft_

Version: 0.1.0

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [BCP 14](https://tools.ietf.org/html/bcp14), [RFC2119](https://www.rfc-editor.org/rfc/rfc2119.txt), and [RFC8174](https://www.rfc-editor.org/rfc/rfc8174.txt) when, and only when, they appear in all capitals, as shown here.

---

## Table of Contents

- [Collection Metadata](collection-metadata.md) — Per-collection publication and provenance metadata (`collection_metadata.yaml`)
- [Experimental Metadata](experimental-metadata.md) — Per-experiment biological, experimental, and technical context (`experimental_metadata.yaml`)
- [Perturbation Library](perturbation-library.md) — Per-experiment sgRNA library with cross-table join keys (`perturbation_library.csv`)
- [scFeature Table](cell-data.md) — Per-experiment single-cell feature table (`cell_data.parquet`)
- [Aggregated Data](aggregated-data.md) — Per-visualization perturbation-level AnnData (`aggregated_data.h5ad`)
- [Feature Definitions](feature-definitions.md) — Per-experiment optional feature catalog (`feature_definitions.csv`)
- [Example Images](example-images.md) — Per-visualization representative single-cell image crops (`examples.zarr`)
- [Zarr Images](zarr-images.md) — Per-experiment primary OME-NGFF HCS image store (`{screen_name}.zarr`)
- [Changelog](changelog.md) — Appendix A: version history

---

## Schema Versioning

The OPS schema version is based on [Semantic Versioning](https://semver.org/).

**Major version** is incremented when incompatible schema updates are introduced:
- Renaming or removing metadata fields
- Changing the type or format of a metadata field

**Minor version** is incremented when additive schema updates are introduced:
- Adding new metadata fields
- Changing validation requirements for an existing field

**Patch version** is incremented for editorial updates.

All changes are documented in the schema [Changelog](changelog.md).

---

## Dependencies

The following external specifications and ontologies are referenced by this schema. Ontology versions are pinned per schema version to ensure consistent validation.

### Format Dependencies

<table>
<thead>
<tr>
<th>Specification</th>
<th>Version</th>
<th>Reference</th>
</tr>
</thead>
<tbody>
<tr>
<td>Zarr</td>
<td>v3</td>
<td><a href="https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html">https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html</a></td>
</tr>
<tr>
<td>OME-NGFF</td>
<td>v0.5</td>
<td><a href="https://ngff.openmicroscopy.org/0.5/">https://ngff.openmicroscopy.org/0.5/</a></td>
</tr>
<tr>
<td>OME-NGFF HCS</td>
<td>v0.5</td>
<td><a href="https://ngff.openmicroscopy.org/0.5/#hcs-layout">https://ngff.openmicroscopy.org/0.5/#hcs-layout</a></td>
</tr>
<tr>
<td>AnnData</td>
<td>v0.10+</td>
<td><a href="https://anndata.readthedocs.io">https://anndata.readthedocs.io</a></td>
</tr>
<tr>
<td>Parquet</td>
<td>v2.6</td>
<td><a href="https://parquet.apache.org/docs/file-format/">https://parquet.apache.org/docs/file-format/</a></td>
</tr>
</tbody>
</table>

### Ontology Dependencies

The following ontology versions are pinned for this schema version. Submissions MUST be validated against these specific releases.

<table>
<thead>
<tr>
<th>Ontology</th>
<th>OBO Prefix</th>
<th>Version Pinned</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="https://www.cellosaurus.org">Cellosaurus</a></td>
<td>CVCL</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://obofoundry.org/ontology/cl.html">Cell Ontology</a></td>
<td>CL</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://www.ebi.ac.uk/efo">Experimental Factor Ontology</a></td>
<td>EFO</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://obofoundry.org/ontology/hsapdv.html">Human Developmental Stages</a></td>
<td>HsapDv</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://obofoundry.org/ontology/mondo.html">Mondo Disease Ontology</a></td>
<td>MONDO</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://obofoundry.org/ontology/mmusdv.html">Mouse Developmental Stages</a></td>
<td>MmusDv</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://obofoundry.org/ontology/ncbitaxon.html">NCBI organismal classification</a></td>
<td>NCBITaxon</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://www.obofoundry.org/ontology/pato.html">Phenotype And Trait Ontology</a></td>
<td>PATO</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
<tr>
<td><a href="http://www.obofoundry.org/ontology/uberon.html">Uberon multi-species anatomy ontology</a></td>
<td>UBERON</td>
<td><em>[TBD before v1.0.0]</em></td>
</tr>
</tbody>
</table>

> **Note:** Following the CELLxGENE schema convention, ontology versions will be pinned to specific releases at the time of v1.0.0 publication. A machine-readable `ontology_info.json` sidecar file will accompany the v1.0.0 release to support programmatic validation.

---

## Data Model Overview

OPS datasets are organized in a four-level hierarchy:

```
Collection                      [1 per submission; groups experiments from a single publication]
└── Experiment (Screen)         [1 or more per collection]
    └── Visualization (Subset)  [1 or more per experiment]
```

### Cross-File Linkage

The following diagram shows how the key identifier fields connect all artifacts:

```
collection_metadata.yaml
│
└── experimental_metadata.yaml  (per experiment)
        │
        └── perturbation_library.csv
                │  barcode           ← per-sgRNA primary key (unique within experiment)
                │  perturbation_id   ← stable join key (submitter-defined)
                │                      shared by all sgRNAs targeting the same gene
                │
                ├──────────────────────────────────────────┐
                ▼                                          ▼
        cell_data.parquet                     aggregated_data.h5ad
        (one row per cell)                    obs index = aggregate_id
          cell_uid  ← globally unique         (one row per aggregation unit)
          perturbation_id FK                  perturbation_id FK
                                              uns['observation_unit'] declares grouping (list)
                │
                ▼
        examples.zarr/
        └── {perturbation_id}/
            └── {barcode}/      ← image crop indexed by barcode (1–10 per perturbation)
```

### Level 0 — Visualization Artifacts (required for data visualization)

<table>
<thead>
<tr>
<th>Artifact</th>
<th>Scope</th>
<th>Required</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="collection-metadata.md">Collection Metadata</a></td>
<td>Per collection</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="perturbation-library.md">Perturbation Library</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="example-images.md">Example Images</a></td>
<td>Per visualization</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="experimental-metadata.md">Experimental Metadata</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="aggregated-data.md">Aggregated Data</a></td>
<td>Per visualization</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="feature-definitions.md">Feature Definitions</a></td>
<td>Per experiment</td>
<td>OPTIONAL</td>
</tr>
</tbody>
</table>

### Level 1 — Data Sharing Artifacts (the data standard)

<table>
<thead>
<tr>
<th>Artifact</th>
<th>Scope</th>
<th>Required</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="cell-data.md">scFeature Table</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="zarr-images.md">Zarr Images</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
</tbody>
</table>

---

## Submission Structure

A complete, valid OPS submission MUST conform to the following directory structure. All paths are relative to the submission root.

```
{collection_root}/
│
├── collection_metadata.yaml           # Required. Per collection.
│
└── {screen_name}/                     # One directory per experiment.
    ├── metadata/
    │   ├── experimental_metadata.yaml # Required. Per experiment.
    │   ├── perturbation_library.csv   # Required. Per experiment.
    │   └── feature_definitions.csv   # Optional. Per experiment.
    │
    ├── cell_data.parquet              # Required. Per experiment.
    │
    ├── visualizations/
    │   └── {visualization_id}/        # One directory per visualization.
    │       ├── aggregated_data.h5ad   # Required. Per visualization.
    │       └── examples.zarr         # Required. Per visualization.
    │
    └── {screen_name}.zarr             # Required. Per experiment.
```

### Notes

- `{visualization_id}` MUST be a unique identifier within the submission.
- `{screen_name}` SHOULD match `experiment.screen_title` with spaces replaced by underscores and all characters lowercased.
- Collections with multiple experiments MUST include one `{screen_name}/` directory per experiment, each with a distinct `{screen_name}`.

### Multimodal Experiments (e.g., CROP-seq)

For experiments that include both OPS imaging data and a paired CROP-seq (or other sequencing-based) readout:

> **Note:** No separate YAML file is created for CROP-seq data. All CROP-seq metadata is added directly to the existing `experimental_metadata.yaml` using the fields below.

- The CROP-seq AnnData file (`crop_seq.h5ad`) MUST be declared in the **existing** `experimental_metadata.yaml` under the `experiment.crop_seq_anndata` field (see [experiment.crop_seq_anndata](experimental-metadata.md#experimentcrop_seq_anndata)).
- The submission MUST include a visualization entry for the CROP-seq data. This visualization MUST contain `aggregated_data.h5ad` but MUST NOT include `examples.zarr` (no image crops are required for sequencing-only readouts).
- `experiment.pseudobulk` in `experimental_metadata.yaml` SHOULD include `"crop_seq"` as a cell state label when CROP-seq groupings are used.

---

## Validation Rules

The following conditional requirements apply across fields. These are in addition to per-field constraints documented in each section below.

<table>
<thead>
<tr>
<th>#</th>
<th>Condition</th>
<th>Requirement</th>
</tr>
</thead>
<tbody>
<tr>
<td>V-1</td>
<td><code>experiment.tissue_type</code> is <code>"cell culture"</code></td>
<td><code>experiment.tissue_ontology_term_id</code> MUST be a <a href="https://www.ebi.ac.uk/ols4/ontologies/cl">Cell Ontology (CL)</a> term. The following CL terms MUST NOT be used: <code>CL:0000255</code> (eukaryotic cell), <code>CL:0000257</code> (Eumycetozoan cell), <code>CL:0000548</code> (animal cell).</td>
</tr>
<tr>
<td>V-1b</td>
<td><code>experiment.tissue_type</code> is <code>"cell line"</code></td>
<td><code>experiment.tissue_ontology_term_id</code> MUST be a <a href="https://www.cellosaurus.org">Cellosaurus</a> term in the format <code>CVCL_XXXXX</code> (e.g., <code>"CVCL_0030"</code> for HeLa). <code>experiment.development_stage_ontology_term_id</code> MUST be <code>"na"</code> and <code>experiment.development_stage</code> MUST be <code>"na"</code>.</td>
</tr>
<tr>
<td>V-2</td>
<td><code>experiment.tissue_type</code> is <code>"tissue"</code> or <code>"organoid"</code></td>
<td><code>experiment.tissue_ontology_term_id</code> MUST be the most accurate descendant of <a href="https://www.ebi.ac.uk/ols4/ontologies/uberon/classes?obo_id=UBERON:0001062"><code>UBERON:0001062</code></a> for <em>anatomical entity</em>.</td>
</tr>
<tr>
<td>V-3</td>
<td><code>experiment.organism_ontology_term_id</code> is <code>"NCBITaxon:9606"</code> (<em>Homo sapiens</em>)</td>
<td><code>experiment.development_stage_ontology_term_id</code> MUST be the most accurate descendant of <a href="https://www.ebi.ac.uk/ols4/ontologies/hsapdv/classes?obo_id=HsapDv:0000001"><code>HsapDv:0000001</code></a> for <em>life cycle</em>, unless <code>tissue_type</code> indicates a cell line, in which case it MUST be <code>"na"</code>.</td>
</tr>
<tr>
<td>V-4</td>
<td><code>experiment.organism_ontology_term_id</code> is <code>"NCBITaxon:10090"</code> (<em>Mus musculus</em>)</td>
<td><code>experiment.development_stage_ontology_term_id</code> MUST be the most accurate descendant of <a href="https://www.ebi.ac.uk/ols4/ontologies/mmusdv/classes?obo_id=MmusDv:0000001"><code>MmusDv:0000001</code></a> for <em>life cycle</em>, unless <code>tissue_type</code> indicates a cell line, in which case it MUST be <code>"na"</code>.</td>
</tr>
<tr>
<tr>
<td>V-6</td>
<td>The z-axis of the Zarr multiscales array has more than one slice (note: this rule is unrelated to <a href="https://ngff.openmicroscopy.org/rfc/6/index.html">NGFF RFC 6</a>)</td>
<td>The z-axis <code>coordinateTransformations[].scale</code> in <code>ome.multiscales</code> MUST be annotated with a non-zero value and the z-axis <code>unit</code> MUST be present (e.g., <code>"micrometer"</code>).</td>
</tr>
<tr>
<td>V-7</td>
<td>Two or more visualizations reference the same <code>cell_data.parquet</code></td>
<td><code>cell_class</code> MUST be populated for all rows in that <code>cell_data.parquet</code> to disambiguate which cells belong to which visualization.</td>
</tr>
<tr>
<td>V-9</td>
<td><code>perturbation_id</code> is present in <code>cell_data.parquet</code></td>
<td><code>experiment.organism_ontology_term_id</code> MUST be one of <code>"NCBITaxon:9606"</code> (<em>Homo sapiens</em>), <code>"NCBITaxon:10090"</code> (<em>Mus musculus</em>), or <code>"NCBITaxon:7955"</code> (<em>Danio rerio</em>). Perturbation data for all other organisms is out of scope for v0.1.0.</td>
</tr>
<tr>
<td>V-10</td>
<td><code>role</code> is <code>"control"</code> in <code>perturbation_library.csv</code></td>
<td><code>control_type</code> MUST be present and MUST be one of <code>"non-targeting"</code> or <code>"intergenic"</code>.</td>
</tr>
<tr>
<td>V-11</td>
<td><code>role</code> is <code>"targeting"</code> in <code>perturbation_library.csv</code></td>
<td><code>control_type</code> MUST NOT be present.</td>
</tr>
<tr>
<td>V-12</td>
<td><code>aggregated_data.h5ad</code> obs contains <code>perturbation_id</code> values that map to <code>perturbation_library.csv</code></td>
<td>At least one <code>perturbation_id</code> MUST resolve to a row where <code>role</code> is <code>"control"</code>.</td>
</tr>
<tr>
<td>V-13</td>
<td><code>aggregated_data.h5ad</code> declares <code>uns['observation_unit']</code> with more than one column</td>
<td>The sibling <code>examples.zarr</code> MUST nest every <code>observation_unit</code> column beyond the perturbation-identifying one between <code>{perturbation_id}</code> and <code>{barcode}</code>, in the order declared in <code>uns['observation_unit']</code>. Every <code>aggregate_id</code> in <code>aggregated_data.h5ad</code> MUST resolve to a crop group in <code>examples.zarr</code> whose path matches all of its <code>observation_unit</code> values.</td>
</tr>
<tr>
<td>V-14</td>
<td><code>aggregated_data.h5ad</code> <code>obs</code> contains <code>n_cells</code></td>
<td>For every row in <code>obs</code>, <code>n_cells</code> MUST equal the number of rows in <code>cell_data.parquet</code> whose values for the columns named in <code>uns['observation_unit']</code> match the values for that row. Applies only when every column in <code>uns['observation_unit']</code> is present in <code>cell_data.parquet</code>.</td>
</tr>
</tbody>
</table>

---

## Artifact Field Specifications

See [Collection Metadata](collection-metadata.md) for the full field specification.

See [Experimental Metadata](experimental-metadata.md) for the full field specification.

See [Perturbation Library](perturbation-library.md) for the full field specification.

See [scFeature Table](cell-data.md) for the full field specification.

See [Aggregated Data](aggregated-data.md) for the full field specification.

See [Feature Definitions](feature-definitions.md) for the full field specification.

See [Example Images](example-images.md) for the full field specification.

See [Zarr Images](zarr-images.md) for the full field specification.

---

## Acknowledgments

The OPS Data Standard builds on [OME-Zarr](https://ngff.openmicroscopy.org/) and draws on the [`ome-zarr-py`](https://github.com/ome/ome-zarr-py) reference implementation, which is distributed under the BSD 2-Clause License. We are grateful to the OME community for their work establishing open standards for bioimaging data.
