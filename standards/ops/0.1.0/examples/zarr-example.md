# OPS Schema v0.1.0 — Zarr Example: `example_screen.zarr`

**Source path:** `/path/to/example_screen.zarr`

Zarr v3 OME-NGFF (v0.5) HCS plate store with 7 hierarchy levels. See [zarr-images.md](zarr-images.md) for the full field specification.

---

## Level 0 — Plate Root

**File:** `example_screen.zarr/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  ome:
    version: "0.5"
    plate:
      version: "0.5"
      name: "example_screen"
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

**File:** `example_screen.zarr/A/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes: {}
```

---

## Level 2 — Column of Row A (Well Group)

**File:** `example_screen.zarr/A/1/zarr.json`

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
  acquisition_uid: null                  # e.g., "acq_example_screen_000"
  acquisition_timestamp: null            # e.g., "2025-04-24T00:00:00Z" (ISO 8601)
```

---

## Level 3 — Image Group (Multiscales)

**File:** `example_screen.zarr/A/1/0/zarr.json`

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
          mean: 0.0
          std: 0.20
          median: 0.0
          iqr: 0.13
        fov_statistics:
          mean: 0.0
          std: 0.20
          median: 0.0
          iqr: 0.13
      Focus3D:
        dataset_statistics:
          mean: 0.0
          std: 0.25
          median: 0.0
          iqr: 0.19
        fov_statistics:
          mean: 0.0
          std: 0.25
          median: 0.0
          iqr: 0.19
      GFP:
        dataset_statistics:
          mean: 90.0
          std: 50.0
          median: 110.0
          iqr: 9.0
        fov_statistics:
          mean: 90.0
          std: 50.0
          median: 110.0
          iqr: 9.0
      mCherry:
        dataset_statistics:
          mean: 125.0
          std: 90.0
          median: 125.0
          iqr: 55.0
        fov_statistics:
          mean: 125.0
          std: 90.0
          median: 125.0
          iqr: 55.0
      nuclei_prediction:
        dataset_statistics:
          mean: 2.5
          std: 7.0
          median: 0.37
          iqr: 0.72
        fov_statistics:
          mean: 2.5
          std: 7.0
          median: 0.37
          iqr: 0.72
      membrane_prediction:
        dataset_statistics:
          mean: 0.30
          std: 0.50
          median: 0.18
          iqr: 0.47
        fov_statistics:
          mean: 0.30
          std: 0.50
          median: 0.18
          iqr: 0.47
    clims_per_level:
      # method: "p0.1-99.5-coarsest+scale2^steps"
      "1":
        contrast_limits: [-6.5, 7.5]
        contrast_limits_per_channel:
          Phase2D: [-6.5, 7.5]
          Focus3D: [-0.8, 0.8]
          GFP: [150.0, 4400.0]
          mCherry: [150.0, 12800.0]
          nuclei_prediction: [0.0, 415.0]
          membrane_prediction: [-0.2, 20.0]
      "2":
        contrast_limits: [-3.0, 4.0]
        contrast_limits_per_channel:
          Phase2D: [-3.0, 4.0]
          Focus3D: [-0.4, 0.4]
          GFP: [150.0, 2700.0]
          mCherry: [150.0, 7400.0]
          nuclei_prediction: [0.0, 230.0]
          membrane_prediction: [-0.2, 11.0]
      "3":
        contrast_limits: [-1.4, 2.1]
        contrast_limits_per_channel:
          Phase2D: [-1.4, 2.1]
          Focus3D: [-0.24, 0.17]
          GFP: [150.0, 1860.0]
          mCherry: [150.0, 4650.0]
          nuclei_prediction: [0.0, 138.0]
          membrane_prediction: [-0.2, 6.8]
      "4":
        contrast_limits: [-0.5, 1.2]
        contrast_limits_per_channel:
          Phase2D: [-0.5, 1.2]
          Focus3D: [-0.13, 0.07]
          GFP: [150.0, 1440.0]
          mCherry: [150.0, 3300.0]
          nuclei_prediction: [0.0, 92.0]
          membrane_prediction: [0.0, 4.5]
```

---

## Level 4 — Resolution Array

**File:** `example_screen.zarr/A/1/0/0/zarr.json` (full-resolution; levels 1–4 follow same schema)

```yaml
zarr_format: 3
node_type: array
data_type: float32
shape: [1, 6, 1, 65536, 65536]   # [T, C, Z, Y, X]
dimension_names: [T, C, Z, Y, X]
fill_value: 0.0
attributes: {}
storage_transformers: []
chunk_grid:
  name: regular
  configuration:
    chunk_shape: [1, 6, 1, 8192, 8192]   # outer shard shape
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

**File:** `example_screen.zarr/A/1/0/labels/zarr.json`

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
      - mitochondria_seg
      - er_seg
      - golgi_seg
      - gfp_seg
      - lysosome_seg
      - lipid_droplet_seg
      - nucleoli_seg
      - nucleoli_seg_2
      - mcherry_seg
      - organelle_seg
# ome.labels is exhaustive: every label group MUST be listed here.
```

---

## Level 6 — Label Group (per segmentation)

**File:** `example_screen.zarr/A/1/0/labels/cell_seg/zarr.json`

```yaml
zarr_format: 3
node_type: group
consolidated_metadata: null
attributes:
  segmentation_metadata:
    label_name: "cell_seg"
    annotation_type: "cell"
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
      n_cells: 12000000
    description: >
      Cell segmentation from membrane virtual stain using Cellpose-SAM
      with hybrid IoU-based stitching (IoU > 0.1)
```

---

## Level 7 — Label Resolution Array

**File:** `example_screen.zarr/A/1/0/labels/cell_seg/0/zarr.json` (full-resolution; levels 1–4 follow same schema)

```yaml
zarr_format: 3
node_type: array
data_type: int32
shape: [1, 1, 1, 65536, 65536]   # [T, C, Z, Y, X]
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
