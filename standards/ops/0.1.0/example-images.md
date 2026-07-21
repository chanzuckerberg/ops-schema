# OPS Data Standard — Example Images

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Example Images

**Scope:** Per visualization
**Container format:** Zarr group (root `zarr.json`)
**Per-leaf format:** OME-Zarr (`.zarr`)
**File path:** `visualizations/{visualization_id}/examples.zarr/`

> **[PENDING — Item #6]** This section requires further specification. The structure below reflects current understanding.

**What is an "example image"?** An example image is a representative single-cell image crop selected for visualization purposes — it is a small, lightweight preview of what a perturbation looks like phenotypically. Example images are NOT a complete record of all cells; they are a curated subset (1–30 per barcode) chosen to illustrate the perturbation effect.

**Why doesn't this follow full OME-NGFF HCS plate conventions?** The `examples.zarr` store is a visualization artifact, not the primary image data. It uses a simple Zarr group hierarchy keyed by `channel_combo`, `perturbation_id`, and `barcode` (with each leaf crop a self-contained OME-Zarr store), without the full OME-NGFF HCS plate/row/well/image nesting. Validators MUST NOT apply OME-NGFF HCS compliance checks to this artifact.

### File Structure

```
examples.zarr/
└── {channel_combo}/        # One subdirectory per channel combination (e.g., "DAPI_COXIV_CENPA_WGA")
    └── {perturbation_id}/  # One subdirectory per perturbation; MUST match a perturbation_id in perturbation_library.csv
        └── {barcode}/      # One subdirectory per barcode; 1–10 barcodes per perturbation; MUST match a barcode in perturbation_library.csv
            └── 0.zarr/ ... N.zarr/   # 1–30 OME-Zarr stores; each is one single-cell crop
```

> **Note — Channel combinations:** Most experiments use a single staining panel, resulting in one subdirectory at this level. In the rare case where a single experiment accumulates data across multiple staining panels (e.g., different rounds of immunofluorescence), each panel produces a distinct channel combination. Since there is one `examples.zarr` per visualization, and a visualization may cluster data from multiple staining panels together, this level allows the viewer to display the appropriate crop channels for each panel. The `{channel_combo}` key uses channel names joined by underscores (e.g., `"DAPI_COXIV_CENPA_WGA"`).

When the sibling `aggregated_data.h5ad` uses an `observation_unit` with more than one column (e.g., `["gene_id", "cell_cycle_phase"]`), every column in `observation_unit` that is not already represented by `{perturbation_id}` or `{barcode}` MUST appear as an additional level nested between `{perturbation_id}` and `{barcode}`, in the order declared in `uns['observation_unit']`:

```
examples.zarr/
└── {channel_combo}/
    └── {perturbation_id}/
        └── {cell_cycle_phase}/   # one nested level per additional observation_unit column, in declared order
            └── {barcode}/
                └── 0.zarr/ ... N.zarr/
```

`{perturbation_id}` and `{barcode}` are always present in the path as directory anchors. If either appears in `observation_unit` it MUST NOT be re-emitted as an additional nested level — i.e., `observation_unit = ["perturbation_id"]`, `["perturbation_id", "barcode"]`, or `["barcode"]` all produce the same flat layout below `{channel_combo}/{perturbation_id}/{barcode}/`. Only stratification columns *other than* `perturbation_id` and `barcode` add path levels.

This ensures every `aggregate_id` in `aggregated_data.h5ad` resolves to a subset-accurate set of crop zarrs — so images shown on dot selection correspond to the specific aggregation row, not just the perturbation overall.

### Optional segmentation labels

Each leaf `{N}.zarr/` MAY include an OME-NGFF `labels/` container to mark **which** cell in the crop is the perturbed target — useful for disambiguating the cell of interest from neighboring cells in a Phase2D field. This is OPTIONAL; leaves without a `labels/` container are fully valid.

```
0.zarr/                  # leaf OME-Zarr crop store
├── 0/ ... K/            # image resolution arrays (the crop itself)
└── labels/              # OPTIONAL OME-NGFF labels container
    └── {label_name}/    # e.g. "cell_seg"; binary mask marking the target cell
```

When present, the `labels/` container MUST be a structurally valid OME-NGFF labels container (see [`zarr-images.md`](zarr-images.md) Levels 5 and 7):

- the `labels/` group's `ome.labels` attribute MUST list every label group name present;
- each label group MUST contain an integer-typed label array registered to the crop (matching its Y/X extent), with `segmentation_metadata.is_ome_label` set to `true` and a `segmentation_metadata.label_name` matching its `ome.labels` entry.

The label array marks **only the target cell**: a binary mask with label value `1` for the perturbed cell and `0` for background.

Each label group's `segmentation_metadata` MUST include `label_name`, `annotation_type`, and `is_ome_label`; all other Level 6 `segmentation_metadata` fields are OPTIONAL.

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
<td>The directory hierarchy of <code>examples.zarr</code> MUST mirror the aggregation grouping declared in the sibling <code>aggregated_data.h5ad</code>'s <code>uns['observation_unit']</code>. Any <code>observation_unit</code> column other than <code>perturbation_id</code> and <code>barcode</code> MUST be nested between <code>{perturbation_id}</code> and <code>{barcode}</code>, in the order declared. Every <code>aggregate_id</code> in <code>aggregated_data.h5ad</code> MUST resolve to at least one crop zarr whose path matches all of its <code>observation_unit</code> values.</td>
</tr>
<tr>
<td><strong>Barcodes per perturbation</strong></td>
<td>Each perturbation MUST have between 1 and 10 barcodes. Each barcode subdirectory MUST contain at least one cell image crop.</td>
</tr>
<tr>
<td><strong>Leaf format</strong></td>
<td>Each leaf <code>{N}.zarr/</code> MUST be a self-contained OME-Zarr store containing a single-cell image crop, with its own channel metadata (axis names, channel labels, and rendering hints). Each crop is self-describing — viewers can resolve channel names by opening the leaf URL directly.</td>
</tr>
<tr>
<td><strong>Channel order</strong></td>
<td>Image arrays in each leaf MUST follow the same channel order as <code>channels_metadata[]</code> in the primary OME-NGFF HCS plate (see <a href="zarr-images.md">Zarr Images</a>). Each leaf's own <code>omero.channels</code> entries MUST reflect this same order.</td>
</tr>
<tr>
<td><strong>Rendering hints</strong></td>
<td>Each leaf's <code>omero.channels[*]</code> SHOULD include <code>color</code> (hex RGB, e.g. <code>"0000FF"</code>) and <code>window.start</code> / <code>window.end</code> (intensity range used for contrast normalization when rendering as 8-bit). When <code>window</code> is absent, viewers MAY fall back to per-image percentile-based normalization. Submitters who want consistent contrast across the visualization SHOULD provide <code>window.start</code> / <code>window.end</code>.</td>
</tr>
<tr>
<td><strong>Leaf root metadata</strong></td>
<td>Each leaf's <code>zarr.json</code> attributes MUST include a <code>perturbation_id</code> key. MUST match a <code>perturbation_id</code> value in <code>perturbation_library.csv</code>.</td>
</tr>
<tr>
<td><strong>Segmentation labels (optional)</strong></td>
<td>Each leaf <code>{N}.zarr/</code> MAY contain an OME-NGFF <code>labels/</code> container marking the perturbed target cell in the crop. When present it MUST be a structurally valid OME-NGFF labels container: <code>labels/</code> carries an <code>ome.labels</code> list, and each label group is an integer-typed array registered to the crop with <code>is_ome_label</code> = <code>true</code> and a <code>label_name</code> matching its <code>ome.labels</code> entry (see <a href="zarr-images.md">Zarr Images</a> Levels 5 &amp; 7). The array is a binary mask (label value <code>1</code> = target cell, <code>0</code> = background). Its <code>segmentation_metadata</code> MUST include <code>label_name</code>, <code>annotation_type</code>, and <code>is_ome_label</code>; all other Level 6 fields are OPTIONAL. Viewers MAY use the label array to highlight or crop to the target cell.</td>
</tr>
</tbody>
</table>

---
