# OPS Data Standard — Example Images

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Example Images

**Scope:** Per visualization
**File format:** OME-Zarr (`.zarr`)
**File path:** `visualizations/{visualization_id}/examples.zarr`

> **[PENDING — Item #6]** This section requires further specification. The structure below reflects current understanding.

**What is an "example image"?** An example image is a representative single-cell image crop selected for visualization purposes — it is a small, lightweight preview of what a perturbation looks like phenotypically. Example images are NOT a complete record of all cells; they are a curated subset (1–30 per barcode) chosen to illustrate the perturbation effect.

**Why doesn't this follow full OME-NGFF HCS plate conventions?** The `examples.zarr` store is a visualization artifact, not the primary image data. It uses a simple Zarr group hierarchy keyed by `perturbation_id` and `barcode`, without the full OME-NGFF HCS plate/row/well/image nesting. Validators MUST NOT apply OME-NGFF HCS compliance checks to this artifact.

This file contains representative single-cell image crops used for visualization, organized hierarchically by perturbation and cell.

### File Structure

```
examples.zarr/
└── {perturbation_id}/      # One group per perturbation; MUST match a perturbation_id in perturbation_library.csv
    └── {barcode}/          # One group per barcode; 1–10 barcodes per perturbation; MUST match a barcode in perturbation_library.csv
        └── 0/ ... N/       # 1–30 images in standard Zarr format; each array is one single-cell crop
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
<td><strong>Barcodes per perturbation</strong></td>
<td>Each perturbation MUST have between 1 and 10 barcodes. Each barcode group MUST contain at least one cell image crop.</td>
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
