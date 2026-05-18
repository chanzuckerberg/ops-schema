# OPS Data Schema

The complete schema is detailed in the [OPS Schema Repository](https://github.com/chanzuckerberg/ops-schema/tree/main/standards/ops/0.1.0).

<div class="tile-grid">

  <a href="schema-overview/" class="tile">
    <h3 class="tile-title">Schema Overview</h3>

    <p class="tile-tagline">
      Complete technical specification for standardized OPS data structure and validation.
    </p>
  </a>

</div>

---

## About the OPS Standard

The OPS Data Standard (v0.1.0) defines a four-level hierarchy for organizing multimodal perturbation screening data:

1. **Collection** — One submission per publication; groups experiments from a single study
2. **Experiment** — One or more screens from a collection
3. **Visualization** — Aggregated views of experiment data (e.g., by cell state)

All submissions MUST conform to the standardized schema covering:

- Metadata (collection, experimental, perturbation library)
- Single-cell feature tables (Parquet format)
- Aggregated data (AnnData H5AD format)
- Example images (Zarr v3 with OME-NGFF metadata)

Data contributors receive white-glove onboarding support and a citable collection page.

---

## Submission & Contribution

The OPS Explorer is currently accepting submissions from academic labs and industry partners with existing OPS datasets. Reach out to support@biohub.org.

## Version History

- **v0.1.0** (Draft) — Initial specification; pending items tracked on GitHub before v1.0.0 release
