# OPS Data Standard — Feature Definitions

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Feature Definitions

**Scope:** Per experiment
**File format:** CSV
**File path:** `metadata/feature_definitions.csv`

This file is OPTIONAL. It SHOULD be included when datasets use non-standard feature names or novel feature extraction methods, to enable cross-dataset comparability.

Each row defines one feature. The file MUST include the following six columns:

| Column | Type | Required | Description |
|---|---|---|---|
| `feature_id` | `String` | REQUIRED | Unique identifier for the feature (e.g., `"CellProfiler__AreaShape_Area__nucleus"`). MUST match the `var` index in `aggregated_data.h5ad`. |
| `feature_name` | `String` | REQUIRED | Human-readable name of the feature (e.g., `"Nucleus Area"`). |
| `feature_type` | `String` | REQUIRED | Category of feature. MUST be one of `"morphology"`, `"intensity"`, `"texture"`, `"granularity"`, or `"categorical"`. |
| `unit` | `String` | OPTIONAL | Unit of measurement (e.g., `"pixels"`, `"um^2"`). Leave blank if not applicable. |
| `software` | `String` | OPTIONAL | Software package used to compute the feature (e.g., `"CellProfiler"`, `"vision_model"`). |
| `version` | `String` | OPTIONAL | Version of the software (e.g., `"4.2.1"`). |

---
