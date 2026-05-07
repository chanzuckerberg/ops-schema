# OPS Data Standard — Example Images

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Example Images

**Scope:** Per visualization
**Container format:** Plain directory tree (NOT a Zarr store)
**Per-leaf format:** OME-Zarr (`.zarr`)
**File path:** `visualizations/{visualization_id}/examples/`

> **[PENDING — Item #6]** This section requires further specification. The structure below reflects current understanding.

**What is an "example image"?** An example image is a representative single-cell image crop selected for visualization purposes — it is a small, lightweight preview of what a perturbation looks like phenotypically. Example images are NOT a complete record of all cells; they are a curated subset (1–30 per barcode) chosen to illustrate the perturbation effect.

**Why doesn't this follow full OME-NGFF HCS plate conventions?** The `examples/` directory is a visualization artifact, not the primary image data. It is a plain directory tree keyed by `channel_combo`, `perturbation_id`, and `barcode`, with each leaf cell crop stored as an independent OME-Zarr store. The intermediate directories (`{channel_combo}/`, `{perturbation_id}/`, `{barcode}/`) are NOT Zarr groups — they have no `zarr.json` and the tree is not openable as a single hierarchical Zarr store. Validators MUST NOT apply OME-NGFF HCS compliance checks to this artifact.

This file contains representative single-cell image crops used for visualization, organized hierarchically by perturbation and cell.

### File Structure

```
examples/
└── {channel_combo}/        # One subdirectory per channel combination (e.g., "DAPI_COXIV_CENPA_WGA")
    └── {perturbation_id}/  # One subdirectory per perturbation; MUST match a perturbation_id in perturbation_library.csv
        └── {barcode}/      # One subdirectory per barcode; 1–10 barcodes per perturbation; MUST match a barcode in perturbation_library.csv
            └── 0.zarr/ ... N.zarr/   # 1–30 OME-Zarr stores; each is one single-cell crop
```

> **Note — Channel combinations:** Most experiments use a single staining panel, resulting in one subdirectory at this level. In the rare case where a single experiment accumulates data across multiple staining panels (e.g., different rounds of immunofluorescence), each panel produces a distinct channel combination. Since there is one `examples/` directory per visualization, and a visualization may cluster data from multiple staining panels together, this level allows the viewer to display the appropriate crop channels for each panel. The `{channel_combo}` key uses channel names joined by underscores (e.g., `"DAPI_COXIV_CENPA_WGA"`).

> **Note — `.zarr` suffix on leaves:** Each `{N}.zarr/` directory IS a self-contained OME-Zarr store (with its own `zarr.json` declaring it as a group, plus a level-0 array). The `.zarr` suffix is required so that viewers and `zarr.open(...)` calls can correctly identify each leaf as an independent store. The intermediate directories above the leaves do NOT use `.zarr` since they are not Zarr stores.

When the sibling `aggregated_data.h5ad` uses an `observation_unit` with more than one column (e.g., `["gene_id", "cell_cycle_phase"]`), every column in `observation_unit` that is not already represented by `{perturbation_id}` or `{barcode}` MUST appear as an additional level nested between `{perturbation_id}` and `{barcode}`, in the order declared in `uns['observation_unit']`:

```
examples/
└── {channel_combo}/
    └── {perturbation_id}/
        └── {cell_cycle_phase}/   # one nested level per additional observation_unit column, in declared order
            └── {barcode}/
                └── 0.zarr/ ... N.zarr/
```

`{perturbation_id}` and `{barcode}` are always present in the path (they are the directory anchors), so if either appears in `observation_unit` it MUST NOT be re-emitted as an additional nested level — i.e., `observation_unit = ["perturbation_id"]`, `["perturbation_id", "barcode"]`, or `["barcode"]` produce the same flat layout below `{channel_combo}/{perturbation_id}/{barcode}/`. Only stratification columns *other than* perturbation_id and barcode add path levels.

This ensures every `aggregate_id` in `aggregated_data.h5ad` resolves to a subset-accurate group of crops — so images shown on dot selection correspond to the specific aggregation row, not just the perturbation overall.

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
<td><strong>Mirrors aggregated_data.h5ad grouping</strong></td>
<td>The directory hierarchy of <code>examples/</code> MUST mirror the aggregation grouping declared in the sibling <code>aggregated_data.h5ad</code>'s <code>uns['observation_unit']</code>. Any <code>observation_unit</code> column beyond <code>perturbation_id</code> and <code>barcode</code> (which are already path anchors) MUST be nested between <code>{perturbation_id}</code> and <code>{barcode}</code>, in the order declared. Every <code>aggregate_id</code> in <code>aggregated_data.h5ad</code> MUST resolve to at least one crop directory whose path matches all of its <code>observation_unit</code> values.</td>
</tr>
<tr>
<td><strong>Barcodes per perturbation</strong></td>
<td>Each perturbation MUST have between 1 and 10 barcodes. Each barcode subdirectory MUST contain at least one cell image crop.</td>
</tr>
<tr>
<td><strong>Leaf format</strong></td>
<td>Each leaf <code>{N}.zarr/</code> MUST be a self-contained OME-Zarr store containing a single-cell image crop, with its own channel metadata (axis names, channel labels, and rendering hints). The <code>.zarr</code> suffix is required so the leaf is identifiable as a Zarr store. This makes each crop self-describing — viewers can resolve channel names by opening the leaf URL directly, without cross-referencing any parent.</td>
</tr>
<tr>
<td><strong>Channel order</strong></td>
<td>Image arrays in each leaf MUST follow the same channel order as <code>channels_metadata[]</code> in the primary OME-NGFF HCS plate (see <a href="zarr-images.md">Zarr Images</a>). Each leaf's own <code>omero.channels</code> entries MUST reflect this same order so the leaf is independently renderable without cross-referencing the plate.</td>
</tr>
<tr>
<td><strong>Leaf root metadata</strong></td>
<td>Each leaf's <code>zarr.json</code> attributes MUST include a <code>perturbation_id</code> key. MUST match a <code>perturbation_id</code> value in <code>perturbation_library.csv</code>.</td>
</tr>
</tbody>
</table>

---
