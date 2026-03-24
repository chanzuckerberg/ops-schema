# OPS Data Standard — scFeature Table

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## scFeature Table

**Scope:** Per experiment
**File format:** Parquet
**File path:** `{screen_name}/cell_data.parquet`

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
<td>The <code>perturbation_id</code> value from <code>perturbation_library.csv</code> assigned to this cell. MUST match a valid <code>perturbation_id</code> in <code>perturbation_library.csv</code>. Serves as the foreign key linking each cell to its perturbation group. MUST NOT change after submission.</td>
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
