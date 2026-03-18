# Optical Pooled Screening (OPS) Data Standard

Contact: [TBD]@chanzuckerberg.com

Document Status: _Draft_

Version: 0.1.0

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [BCP 14](https://tools.ietf.org/html/bcp14), [RFC2119](https://www.rfc-editor.org/rfc/rfc2119.txt), and [RFC8174](https://www.rfc-editor.org/rfc/rfc8174.txt) when, and only when, they appear in all capitals, as shown here.

---

## Pending Items for Review

The following items are unresolved and MUST be addressed before v1.0.0:

<table>
<thead>
<tr>
<th>#</th>
<th>Item</th>
<th>Owner</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><del>Additional Perturbation Library fields for alignment with Perturb-seq schema</del> — <strong>Resolved in v0.1.0. Aligned to CELLxGENE schema v7.1.0 <code>genetic_perturbations</code> structure.</strong></td>
<td>—</td>
</tr>
<tr>
<td>2</td>
<td>Aggregated Data full field specification</td>
<td>Jason / CELLxGENE schema team</td>
</tr>
<tr>
<td>3</td>
<td><del>Review <code>"cell line"</code> and <code>"organelle"</code> as valid <code>tissue_type</code> values — currently omitted to match cross-modality schema, but OPS use cases may require them. Note: CELLxGENE schema v7.0.0 added <code>"cell line"</code> as a valid <code>tissue_type</code>; consider adopting.</del> — <strong>Resolved. <code>"cell line"</code> adopted as a valid <code>tissue_type</code>, with Validation Rule V-1b requiring a Cellosaurus (<code>CVCL_XXXXX</code>) term for <code>tissue_ontology_term_id</code> and <code>development_stage_ontology_term_id</code> MUST be <code>"na"</code>. <code>"organelle"</code> remains out of scope for v0.1.0.</strong></td>
<td>TBD</td>
</tr>
<tr>
<td>4</td>
<td><del>Define valid alphabet and length constraints for <code>barcode</code> and <code>sgrna_sequence</code></del> — <strong>Resolved. <code>barcode</code> and <code>protospacer_sequence</code>: ACGT only; <code>protospacer_sequence</code> length 14–22 chars per CELLxGENE v7.1.0.</strong></td>
<td>—</td>
</tr>
<tr>
<td>5</td>
<td><del>Clarify <code>cell_seq_id</code> uniqueness scope — unique within a well, or within a <code>(plate, well_row, well_col)</code> tuple?</del> — <strong>Resolved. <code>cell_seq_id</code> MUST be unique within a <code>(plate, well_row, well_col)</code> tuple.</strong></td>
<td>TBD</td>
</tr>
<tr>
<td>6</td>
<td>Tighten Example Images artifact spec: array shape/dtype requirements for crop arrays, channel dimension requirements, behavior when a barcode has zero cells, OME-NGFF compliance scope</td>
<td>TBD</td>
</tr>
<tr>
<td>7</td>
<td>Define exhaustive enum values for <code>channels_metadata[].channel_type</code> (currently: <code>"fluorescent"</code>, <code>"brightfield"</code>, <code>"virtual_stain"</code> — are phase contrast, transmitted light, etc. valid?)</td>
<td>TBD</td>
</tr>
<tr>
<td>8</td>
<td>Define exhaustive enum values for <code>segmentation_metadata.annotation_type</code>. Current examples: <code>"cell"</code>, <code>"nucleus"</code>, <code>"cytoplasm"</code>, <code>"mitochondria"</code>, <code>"endoplasmic_reticulum"</code>, <code>"golgi"</code>, <code>"lysosome"</code>, <code>"lipid_droplet"</code>. Needs follow-up on whether event-based annotations (e.g., <code>"apoptosis"</code>, <code>"mitosis"</code>) should be included.</td>
<td>TBD</td>
</tr>
<tr>
<td>9</td>
<td>Add specimen-level metadata fields for cell line authentication, passage number, and mycoplasma testing status</td>
<td>TBD</td>
</tr>
</tbody>
</table>

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

All changes are documented in the schema [Changelog](#appendix-a-changelog).

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
                │  perturbation_id   ← composite FK: {gene_id}__{role}
                │                      shared by all sgRNAs targeting the same gene
                │
                ├──────────────────────────────────────────┐
                ▼                                          ▼
        cell_data.parquet                     aggregated_data.h5ad
        (one row per cell)                    obs index = perturbation_id
          cell_uid  ← globally unique         (one row per perturbation group)
          perturbation_id FK
                │
                ▼
        examples.zarr/
        └── {perturbation_id}/
            └── {cell_uid}/     ← image crop traceable back to cell_data.parquet
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
<td><a href="#collection-metadata">Collection Metadata</a></td>
<td>Per collection</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#perturbation-library">Perturbation Library</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#example-images">Example Images</a></td>
<td>Per visualization</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#experimental-metadata">Experimental Metadata</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#aggregated-data">Aggregated Data</a></td>
<td>Per visualization</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#feature-definitions">Feature Definitions</a></td>
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
<td><a href="#scfeature-table">scFeature Table</a></td>
<td>Per experiment</td>
<td>REQUIRED</td>
</tr>
<tr>
<td><a href="#zarr-images">Zarr Images</a></td>
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
    │   ├── cell_data.parquet          # Required. Per experiment.
    │   └── feature_definitions.json  # Optional. Per experiment.
    │
    ├── visualizations/
    │   └── {visualization_id}/        # One directory per visualization.
    │       ├── aggregated_data.h5ad   # Required. Per visualization.
    │       └── examples.zarr         # Required. Per visualization.
    │
    └── {screen_name}.zarr             # Required. Per experiment.
```

### Notes

- `{visualization_id}` MUST be a unique identifier within the submission. Format TBD (see Pending Item #2).
- `{screen_name}` SHOULD match `experiment.screen_title` with spaces replaced by underscores and all characters lowercased.
- Collections with multiple experiments MUST include one `{screen_name}/` directory per experiment, each with a distinct `{screen_name}`.

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
<td>The z-axis of the Zarr multiscales array has more than one slice</td>
<td>The z-axis <code>coordinateTransformations[].scale</code> in <code>ome.multiscales</code> MUST be annotated with a non-zero value and the z-axis <code>unit</code> MUST be present (e.g., <code>"micrometer"</code>).</td>
</tr>
<tr>
<td>V-7</td>
<td>Two or more visualizations reference the same <code>cell_data.parquet</code></td>
<td><code>cell_class</code> MUST be populated for all rows in that <code>cell_data.parquet</code> to disambiguate which cells belong to which visualization.</td>
</tr>
<tr>
<td>V-8</td>
<td><code>collection.publication_doi</code> is <code>null</code></td>
<td>Collection is considered unpublished. <code>collection.publication_reference</code> SHOULD also be <code>null</code>.</td>
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
<td><code>role</code> is <code>"control"</code> in <code>aggregated_data.h5ad</code> obs</td>
<td><code>control_type</code> MUST be present and MUST be one of <code>"non-targeting"</code> or <code>"intergenic"</code>. Values MUST match the corresponding <code>control_type</code> in <code>perturbation_library.csv</code>.</td>
</tr>
</tbody>
</table>

---

## Perturbation Library

**Scope:** Per experiment
**File format:** `.csv`
**File path:** `metadata/perturbation_library.csv`

This file contains metadata about the specific perturbations applied in the OPS experiment and any corresponding CRISPRseq experiments. Each row represents one perturbation (one sgRNA). This schema is aligned with the `uns['genetic_perturbations']` structure in the [CELLxGENE Schema v7.1.0](https://github.com/chanzuckerberg/single-cell-curation/blob/main/schema/7.1.0/schema.md).

**Primary key:** `barcode` is the unique identifier for each row (one sgRNA). Multiple rows may share the same `perturbation_id` when multiple sgRNAs target the same gene.

### perturbation_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>perturbation_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Composite identifier that groups all sgRNAs targeting the same gene and role. Constructed as <code>{gene_id}__{role}</code> (e.g., <code>"ENSG00000186092__targeting"</code>, <code>"non-targeting__control"</code>). Serves as the cross-table foreign key linking this library to <code>aggregated_data.h5ad</code>, <code>cell_data.parquet</code>, and <code>examples.zarr</code>. Multiple sgRNAs in the library WILL share the same <code>perturbation_id</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate. Derived from <code>gene_id</code> and <code>role</code>.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. Format: <code>{gene_id}__{role}</code>. MUST NOT be <code>"na"</code>.</td>
</tr>
</tbody>
</table>

### role

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>role</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Indicates whether this perturbation is a targeting guide or a control</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be one of <code>"targeting"</code> or <code>"control"</code>.</td>
</tr>
</tbody>
</table>

### gene_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>gene_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Ensembl gene ID for the gene targeted by this perturbation. For control guides, MUST be <code>"non-targeting"</code>. Used as the first component of <code>perturbation_id</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be a version-stripped Ensembl gene ID (e.g., <code>"ENSG00000186092"</code>) or <code>"non-targeting"</code>.</td>
</tr>
</tbody>
</table>

### gene_symbol

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>gene_symbol</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Human-readable gene symbol for the gene targeted by this perturbation (e.g., <code>"BRCA2"</code>). For control guides, MUST be <code>"non-targeting"</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the HGNC-approved gene symbol or <code>"non-targeting"</code>.</td>
</tr>
</tbody>
</table>

### barcode

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>barcode</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Unique nucleotide barcode sequence used to identify this perturbation in the in situ sequencing readout. MUST match barcode values in <code>cell_data.parquet</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be unique within the perturbation library. MUST be composed only of the characters <code>A</code>, <code>C</code>, <code>G</code>, or <code>T</code>. Length MUST match <code>library.barcode_length</code> in <code>experimental_metadata.yaml</code>.</td>
</tr>
</tbody>
</table>

### control_type

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>control_type</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The type of control guide. Non-targeting controls have no genomic match and serve as pure negative controls. Intergenic controls cut the genome in non-coding, non-functional regions and control for cutting effects.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate if <code>role</code> is <code>"control"</code>; otherwise this field MUST NOT be present.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be one of <code>"non-targeting"</code> or <code>"intergenic"</code>.</td>
</tr>
</tbody>
</table>

### protospacer_sequence

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>protospacer_sequence</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The protospacer (spacer) sequence of the sgRNA used to target the genome</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be composed only of the characters <code>A</code>, <code>C</code>, <code>G</code>, or <code>T</code>. Length MUST be between 14 and 22 characters inclusive.</td>
</tr>
</tbody>
</table>

### protospacer_adjacent_motif

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>protospacer_adjacent_motif</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The PAM sequence matched at the 3' end of the protospacer sequence</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be formatted as <code>"3' MOTIF"</code> (e.g., <code>"3' NGG"</code>). MOTIF MUST be composed only of IUPAC nucleotide ambiguity codes: <code>A</code>, <code>B</code>, <code>C</code>, <code>D</code>, <code>G</code>, <code>H</code>, <code>K</code>, <code>M</code>, <code>N</code>, <code>R</code>, <code>S</code>, <code>T</code>, <code>V</code>, <code>W</code>, or <code>Y</code>. MOTIF MUST contain at least one character.</td>
</tr>
</tbody>
</table>

### sgrna_target_locus

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>sgrna_target_locus</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Genomic coordinates of the sgRNA cut site, derived by GuideScan2 or equivalent tool. Equivalent to <code>derived_genomic_regions</code> in CELLxGENE schema v7.1.0.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. Format: <code>"SEQUENCE_ID:START-END(STRAND)"</code> using 1-based fully-closed coordinates (e.g., <code>"chr7:117548628-117548650(+)"</code>). MUST use ENSEMBL-style chromosome identifiers (no <code>"chr"</code> prefix for human/mouse; mitochondrial chromosome as <code>"MT"</code> not <code>"M"</code>).</td>
</tr>
</tbody>
</table>

### derived_gene_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>derived_gene_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>ENSEMBL gene identifier for the gene overlapping the target locus. Equivalent to <code>derived_features[feature_id]</code> in CELLxGENE schema v7.1.0. System-annotated when <code>sgrna_target_locus</code> is provided.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System SHOULD annotate when <code>sgrna_target_locus</code> is present.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. MUST be a versioned-stripped ENSEMBL gene identifier (e.g., <code>"ENSG00000186092"</code>).</td>
</tr>
</tbody>
</table>

### derived_gene_name

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>derived_gene_name</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Human-readable gene name corresponding to <code>derived_gene_id</code>. Equivalent to the value of <code>derived_features[feature_id]</code> in CELLxGENE schema v7.1.0.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System SHOULD annotate when <code>derived_gene_id</code> is present.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. MUST be the <code>gene_name</code> attribute from the corresponding gene reference. Defaults to <code>derived_gene_id</code> if no <code>gene_name</code> is assigned.</td>
</tr>
</tbody>
</table>

---

## Example Images

**Scope:** Per visualization
**File format:** OME-Zarr (`.zarr`)
**File path:** `visualizations/{visualization_id}/examples.zarr`

> **[PENDING — Item #6]** This section requires further specification. The structure below reflects current understanding.

This file contains representative single-cell image crops used for visualization, organized hierarchically by perturbation and cell.

### File Structure

```
examples.zarr/
└── {perturbation_id}/      # One group per perturbation (e.g., "ENSG00000186092__targeting")
    └── {cell_uid}/         # Up to 30 example cells per perturbation; MUST match cell_uid in cell_data.parquet
```

### Constraints

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Crops per perturbation</strong></td>
<td>SHOULD NOT exceed 30.</td>
</tr>
<tr>
<td><strong>Array content</strong></td>
<td>Each leaf node MUST contain a single-cell image crop as a Zarr array.</td>
</tr>
<tr>
<td><strong>Channel order</strong></td>
<td>Image arrays MUST follow the same channel order as <code>channels_metadata[]</code> in the Zarr plate root.</td>
</tr>
<tr>
<td><strong>Root metadata</strong></td>
<td>Zarr metadata at the root MUST include a <code>perturbation_id</code> key. MUST match a <code>perturbation_id</code> value in <code>perturbation_library.csv</code>.</td>
</tr>
</tbody>
</table>

---

## Collection Metadata

**Scope:** Per collection
**File format:** YAML
**File path:** `collection_metadata.yaml`

This file captures publication and provenance metadata shared across all experiments in the collection.

#### collection.title

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>collection.title</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text title for the collection</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>.</td>
</tr>
</tbody>
</table>

#### collection.publication_doi

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>collection.publication_doi</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>DOI of the associated publication. Applies to all experiments in the collection.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate if published. Otherwise MUST be <code>null</code>.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be a valid DOI URI (e.g., <code>"https://doi.org/10.1016/j.cell.2022.12.009"</code>).</td>
</tr>
</tbody>
</table>

#### collection.publication_reference

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>collection.publication_reference</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Human-readable citation string for the associated publication</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. (e.g., <code>"Funk et al. 2022 (Cell)"</code>).</td>
</tr>
</tbody>
</table>

---

## Experimental Metadata

**Scope:** Per experiment
**File format:** YAML
**File path:** `{screen_name}/metadata/experimental_metadata.yaml`

This file captures the biological, experimental, and technical context of the screen.

### Screen Information

#### experiment.screen_title

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.screen_title</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text title describing the screen</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>.</td>
</tr>
</tbody>
</table>

#### experiment.pseudobulk

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.pseudobulk</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of cell state labels used for pseudobulk groupings in this experiment</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate if pseudobulk analysis was performed.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[String]</code>. Each element is a free-text label (e.g., <code>["interphase", "mitotic"]</code>). OPTIONAL.</td>
</tr>
</tbody>
</table>

#### experiment.organism_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.organism_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The organism from which the assayed cells were derived</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be an <a href="https://www.ebi.ac.uk/ols4/ontologies/ncbitaxon">NCBI organismal classification</a> term (e.g., <code>"NCBITaxon:9606"</code> for <em>Homo sapiens</em>).</td>
</tr>
</tbody>
</table>

#### experiment.organism

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.organism</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>organism_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The tissue or cell line from which the assayed cells were derived. Validation rules depend on <code>tissue_type</code> — see Validation Rules V-1, V-1b, and V-2.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. See Validation Rules <a href="#validation-rules">V-1</a> and <a href="#validation-rules">V-2</a> for conditional requirements by <code>tissue_type</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>tissue_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue_type

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue_type</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Classification of the sample type. Governs validation of <code>tissue_ontology_term_id</code> and <code>development_stage_ontology_term_id</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be one of <code>"tissue"</code>, <code>"organoid"</code>, <code>"cell culture"</code>, or <code>"cell line"</code>.</td>
</tr>
</tbody>
</table>

#### experiment.disease_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.disease_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Disease status of the organism or cell line from which cells were derived</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be <a href="https://www.ebi.ac.uk/ols4/ontologies/pato/classes?obo_id=PATO:0000461"><code>"PATO:0000461"</code></a> for <em>normal</em> or <em>healthy</em>, or the most accurate descendant of <a href="https://www.ebi.ac.uk/ols4/ontologies/mondo/classes?obo_id=MONDO:0000001"><code>"MONDO:0000001"</code></a> for <em>disease</em>.</td>
</tr>
</tbody>
</table>

#### experiment.disease

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.disease</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>disease_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.development_stage_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.development_stage_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Development stage of the organism. For cell lines, MUST be <code>"na"</code>. See Validation Rules V-1b, V-3, V-4 for organism- and tissue-type-specific requirements.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. See Validation Rules <a href="#validation-rules">V-1b</a>, <a href="#validation-rules">V-3</a>, and <a href="#validation-rules">V-4</a>.</td>
</tr>
</tbody>
</table>

#### experiment.development_stage

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.development_stage</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>development_stage_ontology_term_id</code>. MUST be <code>"na"</code> when <code>development_stage_ontology_term_id</code> is <code>"na"</code>.</td>
</tr>
</tbody>
</table>

#### experiment.assay_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.assay_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The assay type used in the experiment</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be an <a href="https://www.ebi.ac.uk/ols4/ontologies/efo">Experimental Factor Ontology (EFO)</a> term (e.g., <code>"EFO:0022605"</code>).</td>
</tr>
</tbody>
</table>

#### experiment.assay

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.assay</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>assay_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

---

### Cell Line Information

#### cellular.growth_conditions

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.growth_conditions</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text description of growth media, supplements, and culture conditions</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include catalog numbers and concentrations for all reagents.</td>
</tr>
</tbody>
</table>

#### cellular.seeding.density_cells_cm2

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.seeding.density_cells_cm2</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Cell seeding density at the start of the experiment, in cells per cm²</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### cellular.induction.duration

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.induction.duration</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Duration of induction (e.g., Cas9 or doxycycline induction)</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate if induction was performed.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST include unit (e.g., <code>"78 hours"</code>). OPTIONAL.</td>
</tr>
</tbody>
</table>

#### cellular.plate_type

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.plate_type</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description of the plate format used for imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include well count, substrate, and catalog identifier (e.g., <code>"6-well glass-bottom (Cellvis P06-1.5H-N)"</code>).</td>
</tr>
</tbody>
</table>

---

### CRISPR Library

#### library.vector

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.vector</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Name and Addgene accession of the vector used for sgRNA delivery</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include Addgene accession number (e.g., <code>"CROPseq-puro-v2 (Addgene #127458)"</code>).</td>
</tr>
</tbody>
</table>

#### library.total_guides

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.total_guides</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Total number of unique sgRNAs in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### library.guides_per_gene

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.guides_per_gene</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Number of distinct sgRNAs targeting each gene</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### library.number_of_genes

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.number_of_genes</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Total number of genes targeted in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### library.nontargeting_controls

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.nontargeting_controls</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Number of non-targeting control sgRNAs in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### library.barcode_length

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.barcode_length</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Length of the barcode sequence in nucleotides</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### library.gene_selection

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.gene_selection</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text description of the rationale or strategy for gene selection in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### library.positive_controls

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.positive_controls</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description or list of positive control perturbations included in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code> or <code>List[String]</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### library.negative_controls

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.negative_controls</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description or list of negative control perturbations included in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code> or <code>List[String]</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

---

### In Situ Sequencing (ISS)

> **Note:** ISS metadata is included for completeness. ISS image data is NOT submitted as part of this standard.

#### iss.cycles

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.cycles</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Number of sequencing cycles performed</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### iss.objective

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.objective</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Microscope objective used for ISS imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include magnification, NA, and catalog identifier.</td>
</tr>
</tbody>
</table>

#### iss.chemistry

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.chemistry</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Sequencing chemistry used (e.g., number of colors)</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"four color"</code>).</td>
</tr>
</tbody>
</table>

#### iss.channels

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.channels</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of imaging channels used in ISS</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[Object]</code>. Each object MUST include <code>name</code> (<code>String</code>), <code>laser_wavelength_nm</code> (<code>Integer</code>), and <code>exposure_time_ms</code> (<code>Integer</code>).</td>
</tr>
</tbody>
</table>

---

### Phenotype (PH) Imaging

#### phenotype.objective

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>phenotype.objective</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Microscope objective used for phenotype imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include magnification, NA, and catalog identifier.</td>
</tr>
</tbody>
</table>

#### phenotype.exposure_time_ms

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>phenotype.exposure_time_ms</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of per-channel exposure times in milliseconds, in the same channel order as <code>channels_metadata[]</code> in the Zarr plate root.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[Integer]</code>. Length MUST equal the number of channels in <code>channels_metadata[]</code>.</td>
</tr>
</tbody>
</table>

---

### Microscope Hardware

#### microscope.system

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>microscope.system</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Name and model of the microscope system used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"Nikon Ti-2 inverted epifluorescence"</code>).</td>
</tr>
</tbody>
</table>

---

### Data Processing

#### pipeline.github

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>pipeline.github</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>GitHub repository URL or handle for the processing pipeline used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"cheeseman-lab/brieflow"</code>).</td>
</tr>
</tbody>
</table>

#### pipeline.version

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>pipeline.version</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Version of the processing pipeline used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Number</code>. (e.g., <code>1.49</code>).</td>
</tr>
</tbody>
</table>

---

## Aggregated Data

**Scope:** Per visualization
**File format:** AnnData (`.h5ad`)
**File path:** `visualizations/{visualization_id}/aggregated_data.h5ad`

> **[PENDING — Item #2]** Full field specification pending alignment with CELLxGENE schema team. The structure below reflects current understanding and will be updated prior to v1.0.0.

This file is an AnnData object where rows (`obs`) represent **perturbations** and columns (`var`) represent **morphological features**. The shape of the object is `(n_perturbations × n_features)`.

### obs index

The `obs` index MUST be `perturbation_id`. Values MUST match a `perturbation_id` in `perturbation_library.csv`.

### obs (rows — perturbations)

<table>
<thead>
<tr>
<th>Field</th>
<th>Type</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>gene_id</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Ensembl gene ID (version-stripped, e.g., <code>"ENSG00000186092"</code>). MUST be <code>"non-targeting"</code> for control rows.</td>
</tr>
<tr>
<td><code>gene_symbol</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Human-readable gene symbol (e.g., <code>"BRCA2"</code>). MUST be <code>"non-targeting"</code> for control rows.</td>
</tr>
<tr>
<td><code>role</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Whether this observation is a targeting perturbation or control. MUST be one of <code>"targeting"</code> or <code>"control"</code>. Derived from the corresponding <code>role</code> field in <code>perturbation_library.csv</code>.</td>
</tr>
<tr>
<td><code>control_type</code></td>
<td><code>String</code></td>
<td>REQUIRED if <code>role</code> is <code>"control"</code></td>
<td>Type of control guide. MUST be one of <code>"non-targeting"</code> or <code>"intergenic"</code>. MUST NOT be present if <code>role</code> is <code>"targeting"</code>.</td>
</tr>
<tr>
<td><code>cluster_group_{N}</code></td>
<td><code>Integer</code></td>
<td>OPTIONAL</td>
<td>Cluster assignment for grouping N. Column name is user-defined. Multiple cluster groupings are supported.</td>
</tr>
</tbody>
</table>

### var index

The `var` index MUST be `feature_id` — a unique identifier for each morphological feature (e.g., `"CellProfiler__AreaShape_Area__nucleus"`).

### var (columns — features)

<table>
<thead>
<tr>
<th>Field</th>
<th>Type</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>feature_name</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Human-readable name of the morphological or intensity feature</td>
</tr>
<tr>
<td><code>feature_source</code></td>
<td><code>String</code></td>
<td>OPTIONAL</td>
<td>Tool or model that produced this feature (e.g., <code>"CellProfiler"</code>, <code>"vision_model"</code>)</td>
</tr>
</tbody>
</table>

### X (data matrix)

`AnnData.X` MUST be a `Float32` matrix of shape `(n_perturbations × n_features)` containing the **aggregated feature values per perturbation** (e.g., mean across all cells assigned to that perturbation). MUST be stored as `numpy.float32`. Sparse matrices SHOULD use `scipy.sparse.csr_matrix`.

### layers (optional)

<table>
<thead>
<tr>
<th>Key</th>
<th>Type</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>p_values</code></td>
<td><code>Float32, shape=(n_perturbations, n_features)</code></td>
<td>OPTIONAL</td>
<td>Per-feature p-values for each perturbation. Same shape as <code>X</code>.</td>
</tr>
</tbody>
</table>

### obsm (embeddings)

<table>
<thead>
<tr>
<th>Key</th>
<th>Type</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>X_umap</code></td>
<td><code>Float32, shape=(n_perturbations, 2)</code></td>
<td>REQUIRED</td>
<td>UMAP 2D coordinates, one row per perturbation</td>
</tr>
<tr>
<td><code>X_{method}</code></td>
<td><code>Float32</code></td>
<td>OPTIONAL</td>
<td>Additional dimensionality reduction coordinates (e.g., <code>X_pca</code>, <code>X_tsne</code>)</td>
</tr>
</tbody>
</table>

### uns (dataset metadata)

<table>
<thead>
<tr>
<th>Key</th>
<th>Type</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>schema_version</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>OPS schema version used to produce this file (e.g., <code>"0.1.0"</code>)</td>
</tr>
<tr>
<td><code>default_embedding</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Key in <code>obsm</code> to use as the default visualization embedding (e.g., <code>"X_umap"</code>)</td>
</tr>
<tr>
<td><code>title</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Human-readable title for this visualization</td>
</tr>
</tbody>
</table>

---

## Feature Definitions

**Scope:** Per experiment
**File format:** JSON
**File path:** `metadata/feature_definitions.json`

This file is OPTIONAL. It SHOULD be included when datasets use non-standard feature names or novel feature extraction methods, to enable cross-dataset comparability.

### Morphology Features

```json
"morphology": {
  "{feature_name}": {
    "description": "String. Human-readable description of the feature.",
    "unit": "String. Unit of measurement (e.g., 'pixels', 'um^2').",
    "method": "String. Algorithm or approach used to compute the feature.",
    "software": "String. Software package used.",
    "version": "String. Version of the software."
  }
}
```

### Intensity Features

```json
"intensity": {
  "{feature_name}": {
    "description": "String.",
    "unit": "String.",
    "method": "String.",
    "software": "String.",
    "version": "String.",
    "channel_index": "Integer. 0-based index of the channel in the phenotype imaging stack.",
    "channel_name": "String. Name matching a channel in phenotype.channels.",
    "marker": "String. Biological marker measured."
  }
}
```

### Texture Features

```json
"texture": {
  "{feature_name}": {
    "description": "String.",
    "unit": "String.",
    "method": "String.",
    "software": "String.",
    "version": "String."
  }
}
```

### Granularity Features

```json
"granularity": {
  "{feature_name}": {
    "description": "String.",
    "unit": "String.",
    "method": "String.",
    "software": "String.",
    "version": "String."
  }
}
```

### Categorical Features

```json
"categorical_features": [
  {
    "feature_name": "String.",
    "description": "String.",
    "type": "categorical",
    "values": ["String", "..."],
    "method": "String."
  }
]
```

---

## scFeature Table

**Scope:** Per experiment
**File format:** Parquet
**File path:** `metadata/cell_data.parquet`

> **Scope limitations:** This table does NOT support 3D imaging, time-series data, or chemical perturbations. These use cases are out of scope for v0.1.0.

Each row is a unique cell. Individual files are generated per well and stored within the Zarr store at the well level.

### Required Fields

<table>
<thead>
<tr>
<th>Field</th>
<th>Type</th>
<th>Annotator</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>plate</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>Plate identifier</td>
</tr>
<tr>
<td><code>well_row</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>Row position of the well (e.g., <code>"A"</code>). MUST be a single uppercase letter.</td>
</tr>
<tr>
<td><code>well_col</code></td>
<td><code>Integer</code></td>
<td>System MUST annotate.</td>
<td>Column position of the well (e.g., <code>1</code>)</td>
</tr>
<tr>
<td><code>tile</code></td>
<td><code>Integer</code></td>
<td>System MUST annotate.</td>
<td>Field of view (tile) identifier within the well</td>
</tr>
<tr>
<td><code>x</code></td>
<td><code>Float</code></td>
<td>System MUST annotate.</td>
<td>X centroid coordinate of the cell within the tile, in pixels</td>
</tr>
<tr>
<td><code>y</code></td>
<td><code>Float</code></td>
<td>System MUST annotate.</td>
<td>Y centroid coordinate of the cell within the tile, in pixels</td>
</tr>
<tr>
<td><code>cell_uid</code></td>
<td><code>Integer</code></td>
<td>System MUST annotate.</td>
<td>Globally unique cell identifier across experiments. Used as the primary cross-experiment cell-level linker.</td>
</tr>
<tr>
<td><code>cell_seq_id</code></td>
<td><code>Integer</code></td>
<td>System MUST annotate.</td>
<td>Unique integer identifier for a cell. MUST be unique within a <code>(plate, well_row, well_col)</code> tuple.</td>
</tr>
<tr>
<td><code>barcode</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>Perturbation barcode assigned to this cell via in situ sequencing. MUST match a <code>barcode</code> value in <code>perturbation_library.csv</code>.</td>
</tr>
<tr>
<td><code>perturbation_id</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>The <code>perturbation_id</code> value from <code>perturbation_library.csv</code> for the perturbation assigned to this cell. MUST match a valid <code>perturbation_id</code> in the perturbation library. Format: <code>{gene_id}__{role}</code>. Equivalent to <code>obs['genetic_perturbation_id']</code> in CELLxGENE schema v7.1.0. Multiple perturbations MUST be separated by <code>" || "</code> in ascending lexical order with no duplication. The corresponding <code>experiment.organism_ontology_term_id</code> MUST be one of <code>"NCBITaxon:9606"</code> for <em>Homo sapiens</em>, <code>"NCBITaxon:10090"</code> for <em>Mus musculus</em>, or <code>"NCBITaxon:7955"</code> for <em>Danio rerio</em>.</td>
</tr>
<tr>
<td><code>genetic_perturbation_strategy</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>The CRISPR strategy used. MUST be one of <code>"CRISPR knockout screen"</code>, <code>"CRISPR activation screen"</code>, <code>"CRISPR interference screen"</code>, <code>"CRISPR knockout mutant"</code>, <code>"control"</code>, or <code>"no perturbations"</code>. Equivalent to <code>obs['genetic_perturbation_strategy']</code> in CELLxGENE schema v7.1.0.</td>
</tr>
<tr>
<td><code>gene_id</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>Ensembl gene ID derived from the assigned perturbation. MUST match the <code>gene_id</code> in the corresponding perturbation library entry.</td>
</tr>
<tr>
<td><code>gene_symbol</code></td>
<td><code>String</code></td>
<td>System MUST annotate.</td>
<td>Human-readable gene symbol derived from the assigned perturbation. MUST match the <code>gene_symbol</code> in the corresponding perturbation library entry.</td>
</tr>
</tbody>
</table>

### Optional Fields

<table>
<thead>
<tr>
<th>Field</th>
<th>Type</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>bounding_box</code></td>
<td><code>String</code> or <code>Array</code></td>
<td>Bounding box coordinates of the cell in the tile</td>
</tr>
<tr>
<td><code>cell_class</code></td>
<td><code>String</code></td>
<td>Cell state or class assignment. REQUIRED per Validation Rule V-7 when two or more visualizations reference the same scFeature table.</td>
</tr>
<tr>
<td><code>global_x</code></td>
<td><code>Float</code></td>
<td>X centroid coordinate in the global plate coordinate space</td>
</tr>
<tr>
<td><code>global_y</code></td>
<td><code>Float</code></td>
<td>Y centroid coordinate in the global plate coordinate space</td>
</tr>
</tbody>
</table>

Additional feature columns MAY be included. Column header names are not constrained, to accommodate outputs from different models and platforms (e.g., CellProfiler, vision models).

---

## Zarr Images

**Scope:** Per experiment
**File format:** Zarr v3, OME-NGFF v0.5 HCS
**File path:** `{screen_name}.zarr`

This is the primary image store for phenotype imaging data. It follows the OME-NGFF HCS plate convention with OPS-specific metadata extensions. A `.json` metadata file MUST exist at each level (excluding chunk/shard data).

### Zarr Hierarchy

```
{screen_name}.zarr/                     Level 0: Plate root
├── A/                                  Level 1: Row group
│   └── 1/                              Level 2: Well group
│       └── 0/                          Level 3: Image group (multiscales)
│           ├── 0/ ... 4/               Level 4: Resolution arrays (full res → 16x)
│           └── labels/                 Level 5: Labels container
│               └── cell_seg/           Level 6: Label group (per segmentation)
│                   └── 0/              Level 7: Label resolution array
```

### Level 0 — Plate Root

`{screen_name}.zarr/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.plate.version</code></td>
<td>REQUIRED</td>
<td>OME-NGFF version</td>
</tr>
<tr>
<td><code>ome.plate.name</code></td>
<td>REQUIRED</td>
<td>Human-readable name for the plate</td>
</tr>
<tr>
<td><code>ome.plate.field_count</code></td>
<td>REQUIRED</td>
<td>Number of fields of view per well</td>
</tr>
<tr>
<td><code>ome.plate.acquisitions[].id</code></td>
<td>REQUIRED</td>
<td>Unique acquisition identifier</td>
</tr>
<tr>
<td><code>ome.plate.rows[].name</code></td>
<td>REQUIRED</td>
<td>Row labels (e.g., <code>"A"</code>, <code>"B"</code>)</td>
</tr>
<tr>
<td><code>ome.plate.columns[].name</code></td>
<td>REQUIRED</td>
<td>Column labels (e.g., <code>"1"</code>, <code>"2"</code>)</td>
</tr>
<tr>
<td><code>ome.plate.wells[].path</code></td>
<td>REQUIRED</td>
<td>Path to each well group</td>
</tr>
<tr>
<td><code>ome.plate.wells[].rowIndex</code></td>
<td>REQUIRED</td>
<td>0-based row index</td>
</tr>
<tr>
<td><code>ome.plate.wells[].columnIndex</code></td>
<td>REQUIRED</td>
<td>0-based column index</td>
</tr>
<tr>
<td><code>channels_metadata[].name</code></td>
<td>REQUIRED</td>
<td>Channel name</td>
</tr>
<tr>
<td><code>channels_metadata[].index</code></td>
<td>REQUIRED</td>
<td>0-based channel index</td>
</tr>
<tr>
<td><code>channels_metadata[].channel_type</code></td>
<td>REQUIRED</td>
<td>See Pending Item #7 for exhaustive enum definition. Current valid values: <code>"fluorescent"</code>, <code>"brightfield"</code>, <code>"virtual_stain"</code></td>
</tr>
<tr>
<td><code>channels_metadata[].description</code></td>
<td>REQUIRED</td>
<td>Free-text channel description</td>
</tr>
<tr>
<td><code>channels_metadata[].biological_annotation</code></td>
<td>REQUIRED for <code>fluorescent</code> and <code>virtual_stain</code></td>
<td>Biological target being imaged</td>
</tr>
<tr>
<td><code>channels_metadata[].fluorophore</code></td>
<td>OPTIONAL</td>
<td>Fluorophore name</td>
</tr>
<tr>
<td><code>channels_metadata[].excitation_wavelength_nm</code></td>
<td>OPTIONAL</td>
<td>Excitation wavelength in nm</td>
</tr>
<tr>
<td><code>channels_metadata[].emission_wavelength_nm</code></td>
<td>OPTIONAL</td>
<td>Emission wavelength in nm</td>
</tr>
<tr>
<td><code>channels_metadata[].antibody_catalog_id</code></td>
<td>OPTIONAL</td>
<td>Antibody catalog identifier</td>
</tr>
</tbody>
</table>

### Level 1 — Row Group

`{screen_name}.zarr/A/`

No required metadata beyond OME-NGFF row group conventions.

### Level 2 — Well Group

`{screen_name}.zarr/A/1/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.well.images[].path</code></td>
<td>REQUIRED</td>
<td>Path to image groups within this well</td>
</tr>
<tr>
<td><code>ome.well.images[].acquisition</code></td>
<td>REQUIRED</td>
<td>Acquisition ID matching <code>ome.plate.acquisitions[].id</code></td>
</tr>
</tbody>
</table>

### Level 3 — Image Group (Multiscales)

`{screen_name}.zarr/A/1/0/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.multiscales[].name</code></td>
<td>REQUIRED</td>
<td>Name of the multiscale image</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].name</code></td>
<td>REQUIRED</td>
<td>Axis name (e.g., <code>"t"</code>, <code>"c"</code>, <code>"z"</code>, <code>"y"</code>, <code>"x"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].type</code></td>
<td>REQUIRED</td>
<td>Axis type (e.g., <code>"time"</code>, <code>"channel"</code>, <code>"space"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].unit</code></td>
<td>REQUIRED</td>
<td>Axis unit (e.g., <code>"micrometer"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].path</code></td>
<td>REQUIRED</td>
<td>Path to each resolution level array</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].coordinateTransformations[].type</code></td>
<td>REQUIRED</td>
<td>Transformation type (MUST be <code>"scale"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].coordinateTransformations[].scale</code></td>
<td>REQUIRED</td>
<td>Scale factors per axis</td>
</tr>
</tbody>
</table>

### Level 4 — Resolution Arrays

`{screen_name}.zarr/A/1/0/0/` through `.../4/`

Five resolution levels are REQUIRED: full resolution through 16x downsampled.

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>data_type</code></td>
<td>REQUIRED</td>
<td>Array data type (e.g., <code>"uint16"</code>)</td>
</tr>
<tr>
<td><code>shape</code></td>
<td>REQUIRED</td>
<td>Array shape as <code>[T, C, Z, Y, X]</code></td>
</tr>
<tr>
<td><code>chunk_grid</code></td>
<td>REQUIRED</td>
<td>Outer shard shape</td>
</tr>
<tr>
<td><code>codecs</code></td>
<td>REQUIRED</td>
<td>MUST use <code>sharding_indexed</code>. Inner codec SHOULD be <code>zstd</code>. <code>blosc/zstd</code> is accepted where the Zarr writer does not support <code>zstd</code> directly. Other codecs (e.g., <code>lz4</code>) MAY be used where performance requirements justify it.</td>
</tr>
<tr>
<td><code>index_codecs</code></td>
<td>REQUIRED</td>
<td>MUST use <code>bytes</code> + <code>crc32c</code></td>
</tr>
</tbody>
</table>

### Level 5 — Labels Container

`{screen_name}.zarr/A/1/0/labels/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.labels</code></td>
<td>REQUIRED</td>
<td>List of all label group names present under this container</td>
</tr>
</tbody>
</table>

### Level 6 — Label Group (per segmentation)

`{screen_name}.zarr/A/1/0/labels/cell_seg/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>segmentation_metadata.label_name</code></td>
<td>REQUIRED</td>
<td>Name of the segmentation (e.g., <code>"cell_seg"</code>)</td>
</tr>
<tr>
<td><code>segmentation_metadata.annotation_type</code></td>
<td>REQUIRED</td>
<td>Type of biological structure annotated. See Pending Item #8 for exhaustive enum definition. Current examples: <code>"cell"</code>, <code>"nucleus"</code>, <code>"cytoplasm"</code>, <code>"mitochondria"</code>, <code>"endoplasmic_reticulum"</code>, <code>"golgi"</code>, <code>"lysosome"</code>, <code>"lipid_droplet"</code></td>
</tr>
<tr>
<td><code>segmentation_metadata.is_ome_label</code></td>
<td>REQUIRED</td>
<td>Boolean. MUST be <code>true</code> for OME-NGFF compliant label arrays</td>
</tr>
<tr>
<td><code>segmentation_metadata.source_channel.index</code></td>
<td>REQUIRED</td>
<td>0-based index of the channel used for segmentation. MUST match the corresponding <code>channels_metadata[].index</code> at the Zarr plate root.</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.organelle</code></td>
<td>REQUIRED</td>
<td>Biological structure segmented (e.g., <code>"cell"</code>, <code>"nucleus"</code>)</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.marker</code></td>
<td>REQUIRED</td>
<td>Marker used to identify the structure</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.marker_type</code></td>
<td>REQUIRED</td>
<td>Type of marker (e.g., <code>"antibody"</code>, <code>"dye"</code>)</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.full_label</code></td>
<td>REQUIRED</td>
<td>Full human-readable label for the segmentation</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.method</code></td>
<td>REQUIRED</td>
<td>Segmentation algorithm or tool used</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.version</code></td>
<td>REQUIRED</td>
<td>Version of the segmentation tool</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.stitching</code></td>
<td>REQUIRED</td>
<td>Boolean. Whether stitching was applied</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.parameters</code></td>
<td>OPTIONAL</td>
<td>Key-value pairs of segmentation parameters</td>
</tr>
<tr>
<td><code>segmentation_metadata.statistics.n_cells</code></td>
<td>REQUIRED</td>
<td>Number of segmented cells in this label group</td>
</tr>
<tr>
<td><code>segmentation_metadata.description</code></td>
<td>OPTIONAL</td>
<td>Free-text description of the segmentation</td>
</tr>
</tbody>
</table>

### Level 7 — Label Resolution Array

`{screen_name}.zarr/A/1/0/labels/cell_seg/0/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>data_type</code></td>
<td>REQUIRED</td>
<td>Array data type (e.g., <code>"uint32"</code>)</td>
</tr>
<tr>
<td><code>shape</code></td>
<td>REQUIRED</td>
<td>Array shape as <code>[T, C, Z, Y, X]</code></td>
</tr>
<tr>
<td><code>chunk_grid</code></td>
<td>REQUIRED</td>
<td>Outer shard shape</td>
</tr>
<tr>
<td><code>codecs</code></td>
<td>REQUIRED</td>
<td>MUST use <code>sharding_indexed</code>. Inner codec SHOULD be <code>zstd</code>. <code>blosc/zstd</code> is accepted where the Zarr writer does not support <code>zstd</code> directly. Other codecs (e.g., <code>lz4</code>) MAY be used where performance requirements justify it. See <a href="https://friendly-adventure-7j9rgl2.pages.github.io/v0.2/array-standard.html#compression">array standard compression reference</a>.</td>
</tr>
<tr>
<td><code>index_codecs</code></td>
<td>REQUIRED</td>
<td>MUST use <code>bytes</code> + <code>crc32c</code></td>
</tr>
</tbody>
</table>

---

## Appendix A: Changelog

### v0.1.0 (current draft)

**Cross-file linkage**
- Replaced opaque `id` field in Perturbation Library with `perturbation_id`, a composite key `{gene_id}__{role}` (e.g., `"ENSG00000186092__targeting"`). Multiple sgRNAs targeting the same gene share the same `perturbation_id`. `barcode` is now the explicit per-sgRNA primary key.
- Renamed `gene_symbol` → `gene_id` in Perturbation Library (it stored Ensembl IDs); added `gene_symbol` for human-readable symbols (e.g., `"BRCA2"`)
- Promoted `unique_cell_uid` → `cell_uid` as REQUIRED in scFeature Table; globally unique cell identifier across experiments
- Renamed `genetic_perturbation_id` → `perturbation_id` in scFeature Table
- Added cross-file linkage diagram to Data Model Overview

**Collection tier**
- Introduced Collection as the top-level submission tier (Collection → Experiment → Visualization)
- Added `collection_metadata.yaml` with `collection.title`, `collection.publication_doi`, `collection.publication_reference`
- Removed `experiment.publication_doi` and `experiment.publication_reference` from experimental metadata

**Aggregated Data (h5ad)**
- Corrected AnnData structure to match CELLxGENE conventions: `obs` index is `perturbation_id`; `X` matrix is `Float32 (n_perturbations × n_features)`; `p_values` moved to `layers`; `uns` section added with `schema_version`, `default_embedding`, `title`

**Example Images**
- Reorganized Zarr hierarchy from `{gene_symbol}/{barcode}/{1..N}` to `{perturbation_id}/{cell_uid}/`

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
- Item #5: `cell_seq_id` MUST be unique within a `(plate, well_row, well_col)` tuple
- Removed `segmentation_metadata.source_channel.name` and `source_channel.type` — redundant with `channels_metadata[]` at the Zarr plate root; `source_channel.index` alone is the FK

**Out of scope for v0.1.0:** 3D imaging, time-series data, chemical perturbations
