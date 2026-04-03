# OPS Data Standard — Feature Definitions

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Feature Definitions

**Scope:** Per experiment
**File format:** CSV
**File path:** `metadata/feature_definitions.csv`

This file is RECOMMENDED. It documents the **full set of features** measured or used in the experiment — including lab-specific, pipeline-specific, and exploratory features that go beyond the standardized visualization feature set.

This file is not limited to the features present in `aggregated_data.h5ad`. Labs SHOULD include every feature present in `cell_data.h5ad` as well as any derived or custom features used in their analysis.

Each row defines one feature. The file MUST include the following columns:

| Column | Type | Required | Description |
|---|---|---|---|
| `feature_id` | `String` | REQUIRED | Unique identifier for the feature (e.g., `"nucleus__shape__area"`, `"CellProfiler__AreaShape_Area__nucleus"`). MUST match the `var` index in `cell_data.h5ad` for features present there. |
| `feature_name` | `String` | REQUIRED | Human-readable name of the feature (e.g., `"Nucleus Area"`). |
| `feature_type` | `String` | REQUIRED | Category of feature. MUST be one of `"shape"`, `"intensity"`, `"correlation"`, `"texture"`, `"granularity"`, or `"categorical"`. |
| `compartment` | `String` | OPTIONAL | Cellular compartment the feature is measured on (e.g., `"nucleus"`, `"cell"`). |
| `channel` | `String` | OPTIONAL | Channel name the feature is derived from, if applicable. MUST match a channel name in the experiment's Zarr `channels_metadata`. |
| `unit` | `String` | OPTIONAL | Unit of measurement (e.g., `"pixels"`, `"um^2"`). Leave blank if not applicable. |
| `software` | `String` | OPTIONAL | Software package used to compute the feature (e.g., `"CellProfiler"`, `"vision_model"`). |
| `version` | `String` | OPTIONAL | Version of the software (e.g., `"4.2.1"`). |

---
