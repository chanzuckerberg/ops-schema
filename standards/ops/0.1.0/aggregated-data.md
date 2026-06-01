# OPS Data Standard — Aggregated Data

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Aggregated Data

**Scope:** Per visualization
**File format:** AnnData (`.h5ad`)
**File path:** `visualizations/{visualization_id}/aggregated_data.h5ad`

This file is an AnnData object where rows (`obs`) represent **aggregation units** and columns (`var`) represent **morphological features**. The shape of the object is `(n_obs × n_features)`.

Each row represents one unit of pseudobulk aggregation. The granularity is submitter-defined: rows may represent genes, guides (barcodes), or any other grouping strategy. The `observation_unit` key in `uns` declares which column(s) from `cell_data.parquet` were used to define each row as a list of strings, and `aggregate_id` (the obs index) is constructed by concatenating the values of those columns with `|` (pipe) as separator.

Each `aggregated_data.h5ad` file represents exactly **one visualization unit** — all rows in the file are displayed together as a single UMAP and a single volcano plot. A visualization corresponds to one pseudobulk aggregation rendered through one or more embeddings; multiple embeddings (e.g., UMAP, PHATE, t-SNE) of the same aggregation MAY co-exist in `obsm` within the same file, with `uns['default_embedding']` selecting which is shown first. If a submitter wants to split data into separate plots (e.g., different cell-type subsets), each plot MUST be a separate `aggregated_data.h5ad` under its own `visualization_id`.

The `var` axis MUST contain exactly the standardized feature set defined below. This fixed feature set is derived from the [Vesuvius dataset](https://vesuvius.wi.mit.edu/about). Lab-specific or extended features MUST NOT be added to this file; they belong in `metadata/feature_definitions.csv`.

---

### obs index

The `obs` index MUST be `aggregate_id`. Each value MUST be unique. Values are constructed by concatenating the values of the column(s) listed in `uns['observation_unit']`, joined with `|` (pipe). When `observation_unit` contains a single column name, `aggregate_id` is simply that column's value with no separator.

**Examples:**

| `uns['observation_unit']` | `aggregate_id` example | Interpretation |
|---|---|---|
| `["gene_id"]` | `ENSG00000130164` | Gene-level pseudobulk |
| `["barcode"]` | `ACGTACGT` | Guide-level pseudobulk |
| `["gene_id", "cell_cycle_phase"]` | `ENSG00000130164\|mitotic` | Gene × cell-cycle stratified |

### obs (rows — aggregation units)

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
<td><code>perturbation_id</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Foreign key linking this row to <code>perturbation_library.csv</code>. Every value MUST match a <code>perturbation_id</code> in <code>perturbation_library.csv</code>. Not necessarily unique — multiple rows may share the same <code>perturbation_id</code> when stratified by additional columns (e.g., cell cycle phase).</td>
</tr>
<tr>
<td><em>columns named in <code>observation_unit</code></em></td>
<td><em>varies</em></td>
<td>REQUIRED</td>
<td>Every column named in <code>uns['observation_unit']</code> MUST be present in <code>obs</code>. These columns define the aggregation grouping and their values are used to construct <code>aggregate_id</code>.</td>
</tr>
<tr>
<td><code>n_cells</code></td>
<td><code>Integer</code></td>
<td>RECOMMENDED</td>
<td>Number of cells aggregated into this row. Used by the UI to surface aggregation depth per point and to support downstream weighting or filtering. MUST be a non-negative integer. When present, MUST equal the count of rows in <code>cell_data.parquet</code> whose <code>observation_unit</code> column values match this row (see V-14). Named <code>n_cells</code> to align with <code>segmentation_metadata.statistics.n_cells</code> in <code>zarr-images.md</code>.</td>
</tr>
<tr>
<td><code>cluster_group_{N}</code></td>
<td><code>Integer</code></td>
<td>OPTIONAL</td>
<td>Cluster assignment for grouping N. Column name is user-defined. Multiple cluster groupings are supported.</td>
</tr>
</tbody>
</table>

---

### var index

The `var` index MUST be `feature_id`. Feature IDs follow the pattern `{compartment}_{channel_or_measurement}_{measurement}` (e.g., `nucleus_DAPI_mean`, `nucleus_area`). Channel names in feature IDs MUST use the experiment's actual channel names as defined in `channels_metadata[]` (e.g., `DAPI`, `COXIV`), not generic biological names (e.g., `dna`, `tubulin`). Shape features omit the channel component (e.g., `nucleus_area`, not `nucleus_shape_area`).

### var (columns — standardized features)

The `var` axis MUST contain exactly the features enumerated in the **Standardized Feature Set** section below. No additional columns are permitted.

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
<td>Human-readable name of the feature (e.g., <code>"Nucleus Area"</code>)</td>
</tr>
<tr>
<td><code>feature_type</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Category of feature. MUST be one of <code>"shape"</code>, <code>"intensity"</code>, or <code>"correlation"</code>.</td>
</tr>
<tr>
<td><code>compartment</code></td>
<td><code>String</code></td>
<td>REQUIRED</td>
<td>Cellular compartment measured (e.g., <code>"nucleus"</code>, <code>"cell"</code>, <code>"cytoplasm"</code>). Any compartment name is valid.</td>
</tr>
</tbody>
</table>

---

### Standardized Feature Set

Features are derived from the Vesuvius dataset and organized into three types across two compartments (`nucleus`, `cell`).

#### Shape features

Computed per compartment. Feature ID format: `{compartment}_{measurement}`.

| feature_id (nucleus) | feature_id (cell) | Description |
|---|---|---|
| `nucleus_area` | `cell_area` | 2D surface area of the compartment |
| `nucleus_eccentricity` | `cell_eccentricity` | Elongation (0 = circle, →1 = line) |
| `nucleus_form_factor` | `cell_form_factor` | Perimeter-to-area ratio |
| `nucleus_solidity` | `cell_solidity` | Convexity of the compartment boundary |

#### Intensity features

Computed per compartment × channel. Feature ID format: `{compartment}_{channel}_{measurement}`.

| Measurement | feature_id suffix | Description |
|---|---|---|
| `mean` | `_{channel}_mean` | Average pixel intensity within compartment |
| `integrated` | `_{channel}_integrated` | Sum of pixel intensity values within compartment |
| `mass_displacement` | `_{channel}_mass_displacement` | Distance between geometric and intensity-weighted centroids |
| `mean_edge` | `_{channel}_mean_edge` | Average intensity at compartment border |
| `std_edge` | `_{channel}_std_edge` | Standard deviation of border pixel intensity |
| `mean_frac_0` | `_{channel}_mean_frac_0` | Mean intensity in innermost concentric ring |
| `mean_frac_3` | `_{channel}_mean_frac_3` | Mean intensity in outermost concentric ring |

`{channel}` MUST be a channel name present in the experiment's Zarr `channels_metadata`, using the exact name as defined there. For example: `nucleus_DAPI_mean`, `cell_COXIV_integrated`.

#### Correlation features

Pearson correlation between pixel-level intensities of two channels, computed per compartment. Feature ID format: `{compartment}_correlation_{channel_a}_{channel_b}` (channels listed alphabetically).

All pairwise combinations of the experiment's channels are included (channels listed alphabetically). For example: `nucleus_correlation_CENPA_DAPI`, `cell_correlation_COXIV_WGA`.

---

### X (data matrix)

`AnnData.X` MUST be a `Float32` matrix of shape `(n_obs × n_features)` containing the **aggregated feature values per aggregation unit** (e.g., mean across all cells assigned to that unit). MUST be stored as `numpy.float32`. Sparse matrices SHOULD use `scipy.sparse.csr_matrix`.

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
<td><code>Float32, shape=(n_obs, n_features)</code></td>
<td>OPTIONAL</td>
<td>Per-feature p-values for each aggregation unit. Same shape as <code>X</code>.</td>
</tr>
<tr>
<td><code>neg_log10_fdr</code></td>
<td><code>Float32, shape=(n_obs, n_features)</code></td>
<td>OPTIONAL</td>
<td>−log₁₀(FDR-adjusted p-value) per feature per aggregation unit. Same shape as <code>X</code>. Primary value used in the volcano plot. RECOMMENDED when <code>p_values</code> is present.</td>
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
<td><code>X_{method}</code></td>
<td><code>Float32, shape=(n_obs, 2)</code></td>
<td>REQUIRED (at least one)</td>
<td>2D embedding coordinates for visualization. At least one MUST be present (e.g., <code>X_umap</code>, <code>X_phate</code>, <code>X_tsne</code>). The key referenced by <code>uns['default_embedding']</code> MUST exist in <code>obsm</code>.</td>
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
<td><code>observation_unit</code></td>
<td><code>List[String]</code></td>
<td>REQUIRED</td>
<td>Declares which column(s) were used to define each row in <code>obs</code>. Every column named here MUST exist in <code>obs</code>. The values of these columns, concatenated with <code>|</code>, MUST equal the corresponding <code>aggregate_id</code>. Examples: <code>["gene_id"]</code>, <code>["barcode"]</code>, <code>["gene_id", "cell_cycle_phase"]</code>.</td>
</tr>
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
<tr>
<td><code>neg_log10_fdr_threshold</code></td>
<td><code>Float</code></td>
<td>RECOMMENDED</td>
<td>Significance threshold for the volcano plot, expressed in the same −log₁₀(FDR) units as the <code>neg_log10_fdr</code> layer. For example, an FDR cutoff of <code>0.05</code> is stored as <code>1.30103</code> (= −log₁₀(0.05)). The UI uses this value to draw the horizontal threshold line and to color dots above/below the cutoff. When absent, the UI falls back to <code>−log₁₀(0.05) ≈ 1.30103</code>. MUST be a positive finite float when present.</td>
</tr>
</tbody>
</table>

---
