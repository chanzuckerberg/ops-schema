# OPS Data Standard — Aggregated Data

Part of the [OPS Data Standard](schema.md) v0.1.0.

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
<td><code>cluster_group_{N}</code></td>
<td><code>Integer</code></td>
<td>OPTIONAL</td>
<td>Cluster assignment for grouping N. Column name is user-defined. Multiple cluster groupings are supported.</td>
</tr>
</tbody>
</table>

> **Note:** The UI will display only a designated subset of features: up to 30 interpretable features as defined by CZI (standard CellProfiler-derived features; see Pending Item #10), plus up to 10 additional features defined by the submitter. The full feature set (all columns) is present in the data matrix.

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
