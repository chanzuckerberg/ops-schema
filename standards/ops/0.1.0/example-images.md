# OPS Data Standard — Example Images

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Example Images

**Scope:** Per visualization
**File format:** OME-Zarr (`.zarr`)
**File path:** `visualizations/{visualization_id}/examples.zarr`

> **[PENDING — Item #6]** This section requires further specification. The structure below reflects current understanding.

**What is an "example image"?** An example image is a representative single-cell image crop selected for visualization purposes — it is a small, lightweight preview of what a perturbation looks like phenotypically. Example images are NOT a complete record of all cells; they are a curated subset (1–30 per barcode) chosen to illustrate the perturbation effect.

**Why doesn't this follow full OME-NGFF HCS plate conventions?** The `examples.zarr` store is a visualization artifact, not the primary image data. It uses a simple Zarr group hierarchy keyed by `channel_combo`, `perturbation_id`, and `barcode`, without the full OME-NGFF HCS plate/row/well/image nesting. Validators MUST NOT apply OME-NGFF HCS compliance checks to this artifact. The root group's `zarr.json` MAY additionally carry optional per-panel [channel-combinations metadata](#channel-combinations-metadata).

This file contains representative single-cell image crops used for visualization, organized hierarchically by perturbation and cell.

### File Structure

```
examples.zarr/
└── {channel_combo}/        # One group per channel combination (e.g., "DAPI_COXIV_CENPA_WGA")
    └── {perturbation_id}/  # One group per perturbation; MUST match a perturbation_id in perturbation_library.csv
        └── {barcode}/      # One group per barcode; 1–10 barcodes per perturbation; MUST match a barcode in perturbation_library.csv
            └── 0/ ... N/   # 1–30 images in OME-Zarr format; each array is one single-cell crop
```

> **Note — Channel combinations:** Most experiments use a single staining panel, resulting in one group at this level. In the rare case where a single experiment accumulates data across multiple staining panels (e.g., different rounds of immunofluorescence), each panel produces a distinct channel combination. Since there is one `examples.zarr` per visualization, and a visualization may cluster data from multiple staining panels together, this level allows the viewer to display the appropriate crop channels for each panel. The `{channel_combo}` key uses channel names joined by underscores (e.g., `"DAPI_COXIV_CENPA_WGA"`).

When the sibling `aggregated_data.h5ad` uses an `observation_unit` with more than one column (e.g., `["gene_id", "cell_cycle_phase"]`), every column in `observation_unit` beyond the perturbation-identifying one MUST appear as an additional level nested between `{perturbation_id}` and `{barcode}`, in the order declared in `uns['observation_unit']`:

```
examples.zarr/
└── {channel_combo}/
    └── {perturbation_id}/
        └── {cell_cycle_phase}/   # one nested level per additional observation_unit column, in declared order
            └── {barcode}/
                └── 0/ ... N/
```

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
<td>The hierarchy of <code>examples.zarr</code> MUST mirror the aggregation grouping declared in the sibling <code>aggregated_data.h5ad</code>'s <code>uns['observation_unit']</code>. Any <code>observation_unit</code> column beyond the one identifying the perturbation MUST be nested between <code>{perturbation_id}</code> and <code>{barcode}</code>, in the order declared. Every <code>aggregate_id</code> in <code>aggregated_data.h5ad</code> MUST resolve to at least one crop group whose path matches all of its <code>observation_unit</code> values.</td>
</tr>
<tr>
<td><strong>Barcodes per perturbation</strong></td>
<td>Each perturbation MUST have between 1 and 10 barcodes. Each barcode group MUST contain at least one cell image crop.</td>
</tr>
<tr>
<td><strong>Array content</strong></td>
<td>Each leaf node MUST contain a single-cell image crop as an OME-Zarr store with its own channel metadata (axis names, channel labels, and rendering hints). This makes each crop self-describing — viewers can resolve channel names without needing to cross-reference the plate root.</td>
</tr>
<tr>
<td><strong>Channel order</strong></td>
<td>Image arrays MUST follow the same channel order as <code>channels_metadata[]</code> in the Zarr plate root.</td>
</tr>
<tr>
<td><strong>Root metadata</strong></td>
<td>Zarr metadata at the root MUST include a <code>perturbation_id</code> key. MUST match a <code>perturbation_id</code> value in <code>perturbation_library.csv</code>.</td>
</tr>
<tr>
<td><strong>Channel combinations metadata</strong></td>
<td>OPTIONAL. The root group MAY carry per-panel display metadata under <code>channel_combos</code> (see <a href="#channel-combinations-metadata">Channel Combinations Metadata</a>). When present it MUST satisfy the constraints in that section.</td>
</tr>
</tbody>
</table>

---

### Channel Combinations Metadata

OPTIONAL. The `examples.zarr` root group's `zarr.json` MAY carry a `channel_combos` array under `attributes`, describing — **per channel combination** — which single channel best represents that panel and the order in which panels should be displayed. (Some datasets name this container `examples/` without the `.zarr` suffix; consumers SHOULD accept either.)

This lets a viewer render one representative channel per panel — e.g. a multi-panel grid with one column per channel combination — and order those panels, without opening a leaf to guess. It is purely presentational and entirely OPTIONAL: when absent, viewers fall back to their own channel selection and ordering (e.g. by reading a leaf's `omero.channels`). Single-panel visualizations typically omit it.

```jsonc
// examples.zarr/zarr.json
{
  "zarr_format": 3,
  "node_type": "group",
  "attributes": {
    "channel_combos": [
      { "name": "Phase2D",   "primary_channel": "Phase2D_labelfree", "priority": 1 },
      { "name": "5xUPRE",    "primary_channel": "5xUPRE_GFP",        "priority": 2 },
      { "name": "ER_SEC61B", "primary_channel": "ER_SEC61B_mCherry" }   // priority omitted → sorts last
    ]
  }
}
```

Each entry in `channel_combos` has the following fields:

<table>
<thead>
<tr>
<th>Field</th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code> (REQUIRED)</td>
<td>The channel combination. MUST match exactly one <code>{channel_combo}</code> subdirectory under the container.</td>
</tr>
<tr>
<td><code>primary_channel</code> (REQUIRED)</td>
<td>The representative channel for this panel. MUST equal an <code>omero.channels[*].label</code> that is present in <strong>every</strong> leaf under the matching <code>{channel_combo}</code> subdirectory. A single combination MAY aggregate crops from multiple source screens whose channel sets differ; the chosen channel MUST therefore be one common to all of them, otherwise a consumer filtering crops by this label would silently drop those from screens that lack it.</td>
</tr>
<tr>
<td><code>priority</code> (OPTIONAL)</td>
<td>Non-negative integer giving the panel's display order, ascending (<code>1</code> = first). Combinations without a <code>priority</code> sort after those with one, ordered lexicographically by <code>name</code>. Need not be unique or contiguous.</td>
</tr>
</tbody>
</table>

**Constraints**

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Entries map to subdirectories</strong></td>
<td>Every entry's <code>name</code> MUST correspond to an existing <code>{channel_combo}</code> subdirectory under the container. Names MUST be unique within <code>channel_combos</code> (at most one entry per combination).</td>
</tr>
<tr>
<td><strong>Coverage is not required</strong></td>
<td>A <code>{channel_combo}</code> subdirectory need not have a corresponding entry. Combinations without one fall back to viewer defaults; they are not an error.</td>
</tr>
<tr>
<td><strong>Primary channel is common to the panel</strong></td>
<td><code>primary_channel</code> MUST be a channel label present in every leaf of its combination (see the field description above).</td>
</tr>
</tbody>
</table>

---
