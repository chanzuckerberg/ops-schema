# OPS Schema v0.1.0 — Zarr Example: `phenotyping_v3.zarr`

**Source path:** `/hpc/projects/icd.fast.ops/ops0031_20250424/3-assembly/phenotyping_v3.zarr`

Zarr v3 OME-NGFF (v0.5) HCS plate store with 7 hierarchy levels. See [zarr-images.md](zarr-images.md) for the full field specification.

---

## Level 0 — Plate Root

**File:** `phenotyping_v3.zarr/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  ome:
    version: "0.5"
    plate:
      version: "0.5"
      name: "ops0031_20250424"
      field_count: 1
      acquisitions:
        - id: 0
      rows:
        - name: "A"
      columns:
        - name: "1"
        - name: "2"
        - name: "3"
      wells:
        - path: "A/1"
          rowIndex: 0
          columnIndex: 0
        - path: "A/2"
          rowIndex: 0
          columnIndex: 1
        - path: "A/3"
          rowIndex: 0
          columnIndex: 2
  channels_metadata:
    - name: "Phase2D"
      index: 0
      channel_type: "labelfree"           # DCA-aligned value
      description: "Projected 2D reconstruction of label-free brightfield imaging"
      fluorophore: null
      excitation_wavelength_nm: null
      emission_wavelength_nm: null
      antibody_catalog_id: null
    - name: "Focus3D"
      index: 1
      channel_type: "labelfree"           # DCA-aligned value
      description: "Reconstructed focal slice from 3D reconstruction of label-free brightfield"
      fluorophore: null
      excitation_wavelength_nm: null
      emission_wavelength_nm: null
      antibody_catalog_id: null
    - name: "GFP"
      index: 2
      channel_type: "fluorescence"        # DCA-aligned value (was "fluorescent")
      biological_annotation:
        biological_target: "5xUPRE"       # renamed from "organelle"
        marker: null
        marker_type: null
        full_label: "5xUPRE"
      description: "Max projected 5xUPRE"
      fluorophore: "GFP"
      excitation_wavelength_nm: 488
      emission_wavelength_nm: 510
      antibody_catalog_id: null
    - name: "mCherry"
      index: 3
      channel_type: "fluorescence"        # DCA-aligned value (was "fluorescent")
      biological_annotation:
        biological_target: "ER"           # renamed from "organelle"
        marker: "SEC61B"
        marker_type: "endogenous_tag"
        full_label: "ER, SEC61B"
      description: "Max projected ER visualized via SEC61B"
      fluorophore: "mCherry"
      excitation_wavelength_nm: 587
      emission_wavelength_nm: 610
      antibody_catalog_id: null
    - name: "nuclei_prediction"
      index: 4
      channel_type: "predicted"           # DCA-aligned value (was "virtual_stain")
      biological_annotation:
        biological_target: "nuclei"       # renamed from "organelle"
        marker: "virtual stain"
        marker_type: "virtual_stain"
        full_label: "nuclei, virtual stain"
      description: "Nuclei visualized via virtual stain"
      fluorophore: null
      excitation_wavelength_nm: null
      emission_wavelength_nm: null
      antibody_catalog_id: null
    - name: "membrane_prediction"
      index: 5
      channel_type: "predicted"           # DCA-aligned value (was "virtual_stain")
      biological_annotation:
        biological_target: "membrane"     # renamed from "organelle"
        marker: "virtual stain"
        marker_type: "virtual_stain"
        full_label: "membrane, virtual stain"
      description: "Membrane visualized via virtual stain"
      fluorophore: null
      excitation_wavelength_nm: null
      emission_wavelength_nm: null
      antibody_catalog_id: null
```

---

## Level 1 — Row Group

**File:** `phenotyping_v3.zarr/A/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes: {}
```

---

## Level 2 — Column of Row A (Well Group)

**File:** `phenotyping_v3.zarr/A/1/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  ome:
    version: "0.5"
    well:
      version: "0.5"
      images:
        - acquisition: 0
          path: "0"
  microscopy:
    microscope_type: null                # e.g., "inverted", "upright"
    objective: null                      # e.g., "20x Plan Apo"
    magnification: null                  # e.g., 20
    numerical_aperture: null             # e.g., 0.75
    acquisition_mode: null               # e.g., "confocal", "widefield", "light_sheet"
    is_live_imaging: false
    is_fixed_imaging: true
  omero:
    name: "0"
    channels:
      - label: "Phase2D"
        active: true
        color: "FFFFFF"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: -0.2
          end: 0.2
          min: -10.0
          max: 10.0
      - label: "Focus3D"
        active: true
        color: "FFFFFF"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: 0.0
          end: 65535.0
          min: 0.0
          max: 65535.0
      - label: "GFP"
        active: true
        color: "00FF00"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: 0.0
          end: 65535.0
          min: 0.0
          max: 65535.0
      - label: "mCherry"
        active: true
        color: "FF00FF"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: 0.0
          end: 65535.0
          min: 0.0
          max: 65535.0
      - label: "nuclei_prediction"
        active: true
        color: "FFFFFF"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: 0.0
          end: 65535.0
          min: 0.0
          max: 65535.0
      - label: "membrane_prediction"
        active: true
        color: "FFFFFF"
        family: "linear"
        coefficient: 1.0
        inverted: false
        window:
          start: 0.0
          end: 65535.0
          min: 0.0
          max: 65535.0
    rdefs:
      defaultT: 0
      defaultZ: 0
      model: "color"
  container:
    container_uid: null                  # e.g., "plate_001_A1"
    container_type: null                 # e.g., "96-well plate"
    well_position: "A1"
    cell_line: null                      # e.g., "HEK293T"
    culture_conditions:
      media: null                        # e.g., "DMEM + 10% FBS"
      temperature_celsius: null
      co2_percentage: null
    cell_product_lot_id: null
    passage_number: null
  acquisition_uid: null                  # e.g., "acq_ops0031_20250424_000"
  acquisition_timestamp: null            # e.g., "2025-04-24T00:00:00Z" (ISO 8601)
```

---

## Level 3 — Image Group (Multiscales)

**File:** `phenotyping_v3.zarr/A/1/0/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  ome:
    version: "0.5"
    multiscales:
      - version: "0.5"
        name: "0"
        axes:
          - name: "T"
            type: "time"
            unit: "second"
          - name: "C"
            type: "channel"
          - name: "Z"
            type: "space"
            unit: "micrometer"
          - name: "Y"
            type: "space"
            unit: "micrometer"
          - name: "X"
            type: "space"
            unit: "micrometer"
        datasets:
          - path: "0"
            coordinateTransformations:
              - type: "scale"
                scale: [1.0, 1.0, 2.0, 0.65, 0.65]
          - path: "1"
            coordinateTransformations:
              - type: "scale"
                scale: [1.0, 1.0, 4.0, 1.3, 1.3]
          - path: "2"
            coordinateTransformations:
              - type: "scale"
                scale: [1.0, 1.0, 8.0, 2.6, 2.6]
          - path: "3"
            coordinateTransformations:
              - type: "scale"
                scale: [1.0, 1.0, 16.0, 5.2, 5.2]
          - path: "4"
            coordinateTransformations:
              - type: "scale"
                scale: [1.0, 1.0, 32.0, 10.4, 10.4]
        downsamplingMethod: "gaussian"    # RECOMMENDED per OPS schema
    omero:
      version: "0.5"
      id: 0
      name: "0"
      channels:
        - label: "Phase2D"
          active: true
          color: "FFFFFF"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: -0.2
            end: 0.2
            min: -10.0
            max: 10.0
        - label: "Focus3D"
          active: true
          color: "FFFFFF"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: 0.0
            end: 65535.0
            min: 0.0
            max: 65535.0
        - label: "GFP"
          active: true
          color: "00FF00"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: 0.0
            end: 65535.0
            min: 0.0
            max: 65535.0
        - label: "mCherry"
          active: true
          color: "FF00FF"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: 0.0
            end: 65535.0
            min: 0.0
            max: 65535.0
        - label: "nuclei_prediction"
          active: true
          color: "FFFFFF"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: 0.0
            end: 65535.0
            min: 0.0
            max: 65535.0
        - label: "membrane_prediction"
          active: true
          color: "FFFFFF"
          family: "linear"
          coefficient: 1.0
          inverted: false
          window:
            start: 0.0
            end: 65535.0
            min: 0.0
            max: 65535.0
      rdefs:
        defaultT: 0
        defaultZ: 0
        model: "color"
        projection: "normal"
  custom_metadata:
    normalization:
      Phase2D:
        dataset_statistics:
          mean: -5.50e-05
          std: 0.2159
          median: 0.0
          iqr: 0.1363
        fov_statistics:
          mean: -7.55e-05
          std: 0.1987
          median: 0.0
          iqr: 0.1290
      Focus3D:
        dataset_statistics:
          mean: -7.79e-05
          std: 0.2660
          median: 0.0
          iqr: 0.1993
        fov_statistics:
          mean: -1.66e-04
          std: 0.2558
          median: 0.0
          iqr: 0.1898
      GFP:
        dataset_statistics:
          mean: 88.32
          std: 48.72
          median: 112.25
          iqr: 9.007
        fov_statistics:
          mean: 87.75
          std: 48.63
          median: 111.90
          iqr: 9.043
      mCherry:
        dataset_statistics:
          mean: 127.14
          std: 90.55
          median: 126.0
          iqr: 57.43
        fov_statistics:
          mean: 124.68
          std: 88.83
          median: 125.0
          iqr: 54.72
      nuclei_prediction:
        dataset_statistics:
          mean: 2.530
          std: 6.717
          median: 0.372
          iqr: 0.738
        fov_statistics:
          mean: 2.594
          std: 7.046
          median: 0.367
          iqr: 0.697
      membrane_prediction:
        dataset_statistics:
          mean: 0.314
          std: 0.499
          median: 0.177
          iqr: 0.472
        fov_statistics:
          mean: 0.339
          std: 0.502
          median: 0.210
          iqr: 0.506
    clims_per_level:
      # method: "p0.1-99.5-coarsest+scale2^steps"
      "1":
        contrast_limits: [-6.672, 7.406]
        contrast_limits_per_channel:
          Phase2D: [-6.672, 7.406]
          Focus3D: [-0.842, 0.776]
          GFP: [150.0, 4383.96]
          mCherry: [150.0, 12745.29]
          nuclei_prediction: [0.0, 413.27]
          membrane_prediction: [-0.2, 20.24]
      "2":
        contrast_limits: [-3.153, 3.886]
        contrast_limits_per_channel:
          Phase2D: [-3.153, 3.886]
          Focus3D: [-0.438, 0.371]
          GFP: [150.0, 2702.20]
          mCherry: [150.0, 7347.38]
          nuclei_prediction: [0.0, 229.59]
          membrane_prediction: [-0.2, 11.24]
      "3":
        contrast_limits: [-1.393, 2.126]
        contrast_limits_per_channel:
          Phase2D: [-1.393, 2.126]
          Focus3D: [-0.236, 0.169]
          GFP: [150.0, 1861.32]
          mCherry: [150.0, 4648.43]
          nuclei_prediction: [0.0, 137.76]
          membrane_prediction: [-0.2, 6.746]
      "4":
        contrast_limits: [-0.513, 1.247]
        contrast_limits_per_channel:
          Phase2D: [-0.513, 1.247]
          Focus3D: [-0.134, 0.068]
          GFP: [150.0, 1440.88]
          mCherry: [150.0, 3298.95]
          nuclei_prediction: [0.0, 91.84]
          membrane_prediction: [0.0, 4.497]
```

---

## Level 4 — Resolution Array

**File:** `phenotyping_v3.zarr/A/1/0/0/zarr.json` (full-resolution; levels 1–4 follow same schema)

```yaml
zarr_format: 3
node_type: array
data_type: float32
shape: [1, 6, 1, 104688, 105281]   # [T, C, Z, Y, X]
dimension_names: [T, C, Z, Y, X]
fill_value: 0.0
attributes: {}
storage_transformers: []
chunk_grid:
  name: regular
  configuration:
    chunk_shape: [1, 6, 1, 13312, 13312]   # outer shard shape
chunk_key_encoding:
  name: default
  configuration:
    separator: "/"
codecs:
  - name: sharding_indexed
    configuration:
      chunk_shape: [1, 1, 1, 512, 512]     # inner chunk shape
      codecs:
        - name: bytes
          configuration:
            endian: little
        - name: blosc
          configuration:
            typesize: 4
            cname: zstd
            clevel: 1
            shuffle: bitshuffle
            blocksize: 0
      index_codecs:
        - name: bytes
          configuration:
            endian: little
        - name: crc32c
      index_location: end
```

---

## Level 5 — Labels Container

**File:** `phenotyping_v3.zarr/A/1/0/labels/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  ome:
    version: "0.5"
    labels:
      - nuclear_seg
      - cell_seg
      - phase2d_vesicular_seg
      - phase2d_vesicular_dark_seg
      - focus3d_tubular_seg
      - gfp_seg
      - phase2d_tubular_seg
      - focus3d_vesicular_dark_seg
      - nucleoli_phase2d_seg
      - nucleoli_focus3d_seg
      - mcherry_seg
      - focus3d_vesicular_seg
# Note: iss_gene_image, iss_guide_image, and grid_overlay subdirectories
# also exist on disk but are not listed in the OME labels index.
```

---

## Level 6 — Label Group (per segmentation)

**File:** `phenotyping_v3.zarr/A/1/0/labels/cell_seg/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  segmentation_metadata:
    label_name: "cell_seg"
    annotation_type: "cell_segmentation"
    is_ome_label: true
    source_channel:
      index: 5                            # FK to channels_metadata[].index at plate root
                                          # (name and type removed — redundant with plate root)
    biological_annotation:
      biological_target: "cell_membrane"  # renamed from "organelle"
      marker: "virtual stain"
      marker_type: "virtual_stain"
      full_label: "cell membrane, virtual stain"
    segmentation:
      method: "cellpose-sam"
      version: "cell_seg-v1"
      stitching: "hybrid_iou"
      parameters:
        diameter: 100
        flow_threshold: 0.7
        iou_threshold: 0.1
        tile_size: 4096
        tile_overlap: 512
    statistics:
      n_cells: 44724776
    description: >
      Cell segmentation from membrane virtual stain using Cellpose-SAM
      with hybrid IoU-based stitching (IoU > 0.1)
```

---

## Level 7 — Label Resolution Array

**File:** `phenotyping_v3.zarr/A/1/0/labels/cell_seg/0/zarr.json` (full-resolution; levels 1–4 follow same schema)

```yaml
zarr_format: 3
node_type: array
data_type: int32
shape: [1, 1, 1, 104688, 105281]   # [T, C, Z, Y, X]
fill_value: 0
attributes: {}
storage_transformers: []
chunk_grid:
  name: regular
  configuration:
    chunk_shape: [1, 1, 1, 16384, 16384]   # outer shard shape
chunk_key_encoding:
  name: default
  configuration:
    separator: "/"
codecs:
  - name: sharding_indexed
    configuration:
      chunk_shape: [1, 1, 1, 512, 512]     # inner chunk shape
      codecs:
        - name: bytes
          configuration:
            endian: little
        - name: zstd
          configuration:
            level: 0
            checksum: false
      index_codecs:
        - name: bytes
          configuration:
            endian: little
        - name: crc32c
      index_location: end
```
