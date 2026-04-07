# OPS Data Standard — Perturbation Library

Part of the [OPS Data Standard](schema.md) v0.1.0.

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
<td>Stable unique identifier for this perturbation entry, used as the cross-table foreign key linking this library to <code>aggregated_data.h5ad</code>, <code>cell_data.parquet</code>, and <code>examples.zarr</code>. SHOULD be based on <code>gene_id</code> or <code>gene_symbol</code>. Multiple sgRNAs targeting the same gene WILL share the same <code>perturbation_id</code>. This field MUST NOT change after data submission, even if gene annotations (e.g., Ensembl IDs or gene symbols) are later updated.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST NOT be <code>"na"</code>. MUST remain stable after submission.</td>
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
<td>Ensembl gene ID for the gene targeted by this perturbation. For control guides, MUST be <code>"non-targeting"</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. For targeting rows, MUST be a version-stripped Ensembl gene ID (e.g., <code>"ENSG00000186092"</code>) that is present in GENCODE v48 (GRCh38). For control rows, MUST be <code>"non-targeting"</code>.</td>
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
<td>Human-readable gene symbol for the gene targeted by this perturbation (e.g., <code>"BRCA2"</code>). Looked up from GENCODE using <code>gene_id</code>. Equivalent to <code>feature_name</code> in CELLxGENE schema v7.1.0. For control guides, MUST be <code>"non-targeting"</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL for targeting rows. MUST be the <code>gene_name</code> attribute from GENCODE for the <code>gene_id</code>. Defaults to <code>gene_id</code> if no <code>gene_name</code> is assigned. For control rows, MUST be <code>"non-targeting"</code>.</td>
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
<td><code>String</code>. MUST be unique within the perturbation library. MUST be composed only of the characters <code>A</code>, <code>C</code>, <code>G</code>, or <code>T</code>.</td>
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
<td>System MUST annotate when <code>sgrna_target_locus</code> is present.</td>
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
<td>System MUST annotate when <code>derived_gene_id</code> is present.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. MUST be the <code>gene_name</code> attribute from GENCODE for the <code>derived_gene_id</code>. Defaults to <code>derived_gene_id</code> if no gene name is assigned.</td>
</tr>
</tbody>
</table>

---
