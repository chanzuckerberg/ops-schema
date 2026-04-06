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
<td>Cellular compartment measured. MUST be one of <code>"nucleus"</code> or <code>"cell"</code>.</td>
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
<td><code>X_{method}</code></td>
<td><code>Float32, shape=(n_perturbations, 2)</code></td>
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
