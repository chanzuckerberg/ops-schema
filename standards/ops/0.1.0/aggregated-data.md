# OPS Data Standard — Aggregated Data

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Aggregated Data

**Scope:** Per visualization
**File format:** AnnData (`.h5ad`)
**File path:** `visualizations/{visualization_id}/aggregated_data.h5ad`

This file is an AnnData object where rows (`obs`) represent **perturbations** and columns (`var`) represent **morphological features**. The shape of the object is `(n_perturbations × n_features)`.

This file is the shared data object for the visualization layer. It backs both the **volcano plot** (per-feature effect sizes and significance per perturbation) and the **UMAP** (perturbation-level embedding derived from the feature matrix).

The `var` axis MUST contain exactly the standardized feature set defined below. This fixed feature set is derived from the [Vesuvius dataset](https://vesuvius.wi.mit.edu/about). Lab-specific or extended features MUST NOT be added to this file; they belong in `metadata/feature_definitions.csv`.

---

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
<td><code>cell_cycle_phase</code></td>
<td><code>String</code></td>
<td>OPTIONAL</td>
<td>Cell cycle phase for this row. MUST be one of <code>"interphase"</code> or <code>"mitotic"</code> when present. When cell cycle stratification is used, each perturbation appears as two rows — one per phase.</td>
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

The `var` index MUST be `feature_id`. Feature IDs follow the pattern `{compartment}__{channel_or_type}__{measurement}` (e.g., `nucleus__dna__mean`, `cell__shape__area`).

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
<td>Cellular compartment measured. MUST be one of <code>"nucleus"</code> or <code>"cell"</code>.</td>
</tr>
</tbody>
</table>

---

### Standardized Feature Set

Features are derived from the Vesuvius dataset and organized into three types across two compartments (`nucleus`, `cell`).

#### Shape features

Computed per compartment. Feature ID format: `{compartment}__shape__{measurement}`.

| feature_id (nucleus) | feature_id (cell) | Description |
|---|---|---|
| `nucleus__shape__area` | `cell__shape__area` | 2D surface area of the compartment |
| `nucleus__shape__eccentricity` | `cell__shape__eccentricity` | Elongation (0 = circle, →1 = line) |
| `nucleus__shape__form_factor` | `cell__shape__form_factor` | Perimeter-to-area ratio |
| `nucleus__shape__solidity` | `cell__shape__solidity` | Convexity of the compartment boundary |

#### Intensity features

Computed per compartment × channel. Feature ID format: `{compartment}__{channel}__{measurement}`.

| Measurement | feature_id suffix | Description |
|---|---|---|
| `mean` | `__{channel}__mean` | Average pixel intensity within compartment |
| `integrated` | `__{channel}__integrated` | Sum of pixel intensity values within compartment |
| `mass_displacement` | `__{channel}__mass_displacement` | Distance between geometric and intensity-weighted centroids |
| `mean_edge` | `__{channel}__mean_edge` | Average intensity at compartment border |
| `std_edge` | `__{channel}__std_edge` | Standard deviation of border pixel intensity |
| `mean_frac_0` | `__{channel}__mean_frac_0` | Mean intensity in innermost concentric ring |
| `mean_frac_3` | `__{channel}__mean_frac_3` | Mean intensity in outermost concentric ring |

`{channel}` MUST be a channel name present in the experiment's Zarr `channels_metadata`. For example: `nucleus__dna__mean`, `cell__tubulin__integrated`.

#### Correlation features

Pearson correlation between pixel-level intensities of two channels, computed per compartment. Feature ID format: `{compartment}__correlation__{channel_a}_{channel_b}` (channels listed alphabetically).

All pairwise combinations of the experiment's channels are included. For example: `nucleus__correlation__dna_tubulin`, `cell__correlation__actin_gh2ax`.

---

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
<tr>
<td><code>neg_log10_fdr</code></td>
<td><code>Float32, shape=(n_perturbations, n_features)</code></td>
<td>OPTIONAL</td>
<td>−log₁₀(FDR-adjusted p-value) per feature per perturbation. Same shape as <code>X</code>. Primary value used in the volcano plot. RECOMMENDED when <code>p_values</code> is present.</td>
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
