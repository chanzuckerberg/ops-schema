# OPS Data Standard — Zarr Images

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Zarr Images

**Scope:** Per experiment
**File format:** Zarr v3, OME-NGFF v0.5 HCS
**File path:** `{aggregation_name}.zarr`

This is the primary image store for phenotype imaging data. It follows the OME-NGFF HCS plate convention with OPS-specific metadata extensions. A `.json` metadata file MUST exist at each level (excluding chunk/shard data).

### Zarr Hierarchy

```
{aggregation_name}.zarr/                     Level 0: Plate root
├── A/                                  Level 1: Row group
│   └── 1/                              Level 2: Column of Row A (Well group)
│       └── 0/                          Level 3: Image group (multiscales)
│           ├── 0/ ... 4/               Level 4: Resolution arrays (full res → 16x)
│           └── labels/                 Level 5: Labels container
│               └── cell_seg/           Level 6: Label group (per segmentation)
│                   └── 0/              Level 7: Label resolution array
```

### Level 0 — Plate Root

`{aggregation_name}.zarr/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.plate.version</code></td>
<td>REQUIRED</td>
<td>OME-NGFF version</td>
</tr>
<tr>
<td><code>ome.plate.name</code></td>
<td>REQUIRED</td>
<td>Human-readable name for the plate</td>
</tr>
<tr>
<td><code>ome.plate.field_count</code></td>
<td>REQUIRED</td>
<td>Number of fields of view per well</td>
</tr>
<tr>
<td><code>ome.plate.acquisitions[].id</code></td>
<td>REQUIRED</td>
<td>Unique acquisition identifier</td>
</tr>
<tr>
<td><code>ome.plate.rows[].name</code></td>
<td>REQUIRED</td>
<td>Row labels (e.g., <code>"A"</code>, <code>"B"</code>)</td>
</tr>
<tr>
<td><code>ome.plate.columns[].name</code></td>
<td>REQUIRED</td>
<td>Column labels (e.g., <code>"1"</code>, <code>"2"</code>)</td>
</tr>
<tr>
<td><code>ome.plate.wells[].path</code></td>
<td>REQUIRED</td>
<td>Path to each well group</td>
</tr>
<tr>
<td><code>ome.plate.wells[].rowIndex</code></td>
<td>REQUIRED</td>
<td>0-based row index</td>
</tr>
<tr>
<td><code>ome.plate.wells[].columnIndex</code></td>
<td>REQUIRED</td>
<td>0-based column index</td>
</tr>
<tr>
<td><code>channels_metadata[].name</code></td>
<td>REQUIRED</td>
<td>Channel name</td>
</tr>
<tr>
<td><code>channels_metadata[].index</code></td>
<td>REQUIRED</td>
<td>0-based channel index</td>
</tr>
<tr>
<td><code>channels_metadata[].channel_type</code></td>
<td>REQUIRED</td>
<td>Type of imaging channel. Aligned with the <a href="https://github.com/chanzuckerberg/dynamic-cell-atlas-specs/blob/main/docs/v0.2/channel-metadata.rst#guidance-on-channel-type">DCA spec</a>. MUST be one of: <code>"fluorescence"</code>, <code>"chromogenic"</code>, <code>"labelfree"</code>, <code>"predicted"</code>.</td>
</tr>
<tr>
<td><code>channels_metadata[].description</code></td>
<td>REQUIRED</td>
<td>Free-text channel description</td>
</tr>
<tr>
<td><code>channels_metadata[].biological_annotation</code></td>
<td>REQUIRED for <code>fluorescence</code> and <code>predicted</code></td>
<td>Biological target being imaged</td>
</tr>
<tr>
<td><code>channels_metadata[].fluorophore</code></td>
<td>OPTIONAL</td>
<td>Fluorophore name</td>
</tr>
<tr>
<td><code>channels_metadata[].excitation_wavelength_nm</code></td>
<td>OPTIONAL</td>
<td>Excitation wavelength in nm</td>
</tr>
<tr>
<td><code>channels_metadata[].emission_wavelength_nm</code></td>
<td>OPTIONAL</td>
<td>Emission wavelength in nm</td>
</tr>
<tr>
<td><code>channels_metadata[].antibody_catalog_id</code></td>
<td>OPTIONAL</td>
<td>Antibody catalog identifier</td>
</tr>
</tbody>
</table>

### Level 1 — Row Group

`{aggregation_name}.zarr/A/`

No required metadata beyond OME-NGFF row group conventions.

### Level 2 — Well Group

`{aggregation_name}.zarr/A/1/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.well.images[].path</code></td>
<td>REQUIRED</td>
<td>Path to image groups within this well</td>
</tr>
<tr>
<td><code>ome.well.images[].acquisition</code></td>
<td>REQUIRED</td>
<td>Acquisition ID matching <code>ome.plate.acquisitions[].id</code></td>
</tr>
</tbody>
</table>

### Level 3 — Image Group (Multiscales)

`{aggregation_name}.zarr/A/1/0/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.multiscales[].name</code></td>
<td>REQUIRED</td>
<td>Name of the multiscale image</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].name</code></td>
<td>REQUIRED</td>
<td>Axis name. MUST be <code>"T"</code>, <code>"C"</code>, <code>"Z"</code>, <code>"Y"</code>, <code>"X"</code> (uppercase, per OME-NGFF v0.5 convention)</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].type</code></td>
<td>REQUIRED</td>
<td>Axis type (e.g., <code>"time"</code>, <code>"channel"</code>, <code>"space"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].axes[].unit</code></td>
<td>REQUIRED for space and time axes</td>
<td>Axis unit (e.g., <code>"micrometer"</code>, <code>"second"</code>). MUST NOT be present for channel axes, which have no physical unit.</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].path</code></td>
<td>REQUIRED</td>
<td>Path to each resolution level array</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].coordinateTransformations[].type</code></td>
<td>REQUIRED</td>
<td>Transformation type (MUST be <code>"scale"</code>)</td>
</tr>
<tr>
<td><code>ome.multiscales[].datasets[].coordinateTransformations[].scale</code></td>
<td>REQUIRED</td>
<td>Scale factors per axis</td>
</tr>
<tr>
<td><code>ome.multiscales[].downsamplingMethod</code></td>
<td>RECOMMENDED</td>
<td>Method used to generate downsampled resolution levels (e.g., <code>"gaussian"</code>, <code>"average"</code>, <code>"subsample"</code>). Stored as a custom metadata key alongside <code>ome.multiscales</code>.</td>
</tr>
<tr>
<td><code>custom_metadata</code></td>
<td>OPTIONAL</td>
<td>Per-channel normalization statistics (mean, std, median, IQR) and contrast limits. Most applicable to merged-well stores where statistics describe a single image; for per-tile stores these statistics may not be meaningful without defining an aggregation strategy across fields of view.</td>
</tr>
</tbody>
</table>

### Level 4 — Resolution Arrays

`{aggregation_name}.zarr/A/1/0/0/` through `.../4/`

At least one resolution level is REQUIRED. Multiple levels (e.g., full resolution through 16x downsampled) are RECOMMENDED for large merged-well images but not required for per-tile stores.

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>data_type</code></td>
<td>REQUIRED</td>
<td>Array data type (e.g., <code>"uint16"</code>)</td>
</tr>
<tr>
<td><code>shape</code></td>
<td>REQUIRED</td>
<td>Array shape as <code>[T, C, Z, Y, X]</code></td>
</tr>
<tr>
<td><code>chunk_grid</code></td>
<td>REQUIRED</td>
<td>Chunk or outer shard shape</td>
</tr>
<tr>
<td><code>codecs</code></td>
<td>REQUIRED</td>
<td><code>sharding_indexed</code> is RECOMMENDED for merged-well stores where tiles have been stitched into a single large array (reduces file count). For per-tile stores where each field of view is a separate small array, flat chunking with <code>bytes</code> + <code>zstd</code> (or <code>blosc/zstd</code>) is acceptable. Other codecs (e.g., <code>lz4</code>) MAY be used where performance requirements justify it.</td>
</tr>
<tr>
<td><code>index_codecs</code></td>
<td>REQUIRED when using <code>sharding_indexed</code></td>
<td>MUST use <code>bytes</code> + <code>crc32c</code></td>
</tr>
</tbody>
</table>

> **Note — Merged-well vs. per-tile stores:** Some pipelines merge all fields of view into a single well image before writing to Zarr, producing large arrays that benefit from sharding. Other pipelines (e.g., Brieflow) store each tile as a separate small array under the HCS hierarchy (`{row}/{col}/{tile}/`). The sharding requirement is designed for the merged-well case; per-tile stores already have manageable file counts and flat chunking is sufficient.

### Level 5 — Labels Container

`{aggregation_name}.zarr/A/1/0/labels/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>ome.labels</code></td>
<td>REQUIRED</td>
<td>Exhaustive list of all label group names present under this container. Every subdirectory that is a valid OME-NGFF label group MUST be listed here. Subdirectories not listed are not considered part of the standard and will be ignored by readers.</td>
</tr>
</tbody>
</table>

### Level 6 — Label Group (per segmentation)

`{aggregation_name}.zarr/A/1/0/labels/cell_seg/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>segmentation_metadata.label_name</code></td>
<td>REQUIRED</td>
<td>Name of the segmentation (e.g., <code>"cell_seg"</code>)</td>
</tr>
<tr>
<td><code>segmentation_metadata.annotation_type</code></td>
<td>REQUIRED</td>
<td>Type of biological structure annotated. Examples: <code>"cell"</code>, <code>"nucleus"</code>, <code>"cytoplasm"</code>, <code>"mitochondria"</code>, <code>"endoplasmic_reticulum"</code>, <code>"golgi"</code>, <code>"lysosome"</code>, <code>"lipid_droplet"</code></td>
</tr>
<tr>
<td><code>segmentation_metadata.is_ome_label</code></td>
<td>REQUIRED</td>
<td>Boolean. MUST be <code>true</code> for OME-NGFF compliant label arrays</td>
</tr>
<tr>
<td><code>segmentation_metadata.source_channel.index</code></td>
<td>REQUIRED</td>
<td>0-based index of the channel used for segmentation. MUST match the corresponding <code>channels_metadata[].index</code> at the Zarr plate root.</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.biological_target</code></td>
<td>REQUIRED</td>
<td>Biological target, organelle, or structure segmented (e.g., <code>"cell"</code>, <code>"nucleus"</code>, <code>"actin filament"</code>). Free text. Aligned with DCA <code>biological_target</code> field.</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.marker</code></td>
<td>REQUIRED</td>
<td>Marker used to identify the structure</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.marker_type</code></td>
<td>REQUIRED</td>
<td>Type of marker (e.g., <code>"antibody"</code>, <code>"dye"</code>)</td>
</tr>
<tr>
<td><code>segmentation_metadata.biological_annotation.full_label</code></td>
<td>REQUIRED</td>
<td>Full human-readable label for the segmentation</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.method</code></td>
<td>REQUIRED</td>
<td>Segmentation algorithm or tool used</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.version</code></td>
<td>REQUIRED</td>
<td>Version of the segmentation tool</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.stitching</code></td>
<td>REQUIRED</td>
<td>Whether stitching was applied and how. MUST be <code>false</code> if no stitching was applied, or a descriptive string identifying the stitching method (e.g., <code>"hybrid_iou"</code>).</td>
</tr>
<tr>
<td><code>segmentation_metadata.segmentation.parameters</code></td>
<td>OPTIONAL</td>
<td>Key-value pairs of segmentation parameters</td>
</tr>
<tr>
<td><code>segmentation_metadata.statistics.n_cells</code></td>
<td>REQUIRED</td>
<td>Number of segmented cells in this label group</td>
</tr>
<tr>
<td><code>segmentation_metadata.description</code></td>
<td>OPTIONAL</td>
<td>Free-text description of the segmentation</td>
</tr>
</tbody>
</table>

### Level 7 — Label Resolution Array

`{aggregation_name}.zarr/A/1/0/labels/cell_seg/0/`

<table>
<thead>
<tr>
<th>Metadata Key</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>data_type</code></td>
<td>REQUIRED</td>
<td>Array data type (e.g., <code>"uint32"</code>)</td>
</tr>
<tr>
<td><code>shape</code></td>
<td>REQUIRED</td>
<td>Array shape as <code>[T, C, Z, Y, X]</code></td>
</tr>
<tr>
<td><code>chunk_grid</code></td>
<td>REQUIRED</td>
<td>Chunk or outer shard shape</td>
</tr>
<tr>
<td><code>codecs</code></td>
<td>REQUIRED</td>
<td><code>sharding_indexed</code> is RECOMMENDED for merged-well stores. For per-tile stores, flat chunking with <code>bytes</code> + <code>zstd</code> (or <code>blosc/zstd</code>) is acceptable. Other codecs (e.g., <code>lz4</code>) MAY be used where performance requirements justify it. See <a href="https://friendly-adventure-7j9rgl2.pages.github.io/v0.2/array-standard.html#compression">array standard compression reference</a>.</td>
</tr>
<tr>
<td><code>index_codecs</code></td>
<td>REQUIRED when using <code>sharding_indexed</code></td>
<td>MUST use <code>bytes</code> + <code>crc32c</code></td>
</tr>
</tbody>
</table>

---
