# OPS Explorer

Optical Pooled Screening (OPS) combines high-content imaging with pooled genetic screens to reveal the relationship between genes and cell morphology.

The OPS Explorer is a centralized location to visualize and interact with standardized fluoresence imaging and scRNAseq data accessible via CLI, in formats optimized for model training (OME-Zarr V3, H5AD, parquet), with a published schema on GitHub.

<div class="hero-buttons">
<a href="https://biohub.ai/ops" class="md-button md-button--primary">Use the Explorer</a>
<a href="tutorials/quickstart/" class="md-button md-button--secondary">Explorer Quickstart</a>
</div>

V1 capabilities include:
- Dataset collection pages with experimental context and standardized schema
- Interactive data explorer with synchronized imaging and scRNA-seq data
- Visualizations of imaging and/or scRNAseq UMAP embeddings, feature tables, volcano plots, and inline representative cell images
- Gene knockout search and exploration across 1,000 perturbations
- All data available for download via CLIThe OPS Explorer is the first centralized destination for Optical Pooled Screening (OPS) data, giving researchers harmonized, large-scale genetic perturbation imaging datasets in one place.

## Getting Started

<div class="tile-grid">
<a href="tutorials/" class="tile">
<div class="tile-title">Explorer Tutorial</div>
<div class="tile-tagline">Learn how to navigate datasets, search genes, and interpret visualizations.</div>
</a>
<a href="download/" class="tile">
<div class="tile-title">Download Data</div>
<div class="tile-tagline">Access processed images, feature tables, and raw data files.</div>
<div class="tile-arrow">→</div>
</a>
<a href="cli/" class="tile">
<div class="tile-title">CLI Reference</div>
<div class="tile-tagline">Programmatic access and command-line tools for data retrieval.</div>
<div class="tile-arrow">→</div>
</a>
<a href="schema/" class="tile">
<div class="tile-title">Data Schema</div>
<div class="tile-tagline">Details on data structure, organization, and relationships</div>
<div class="tile-arrow">→</div>
</a>
</div>

---

## Contribute Your Data
For data contributor inquiries, contact: [contact email TBD]

## Citation

If you use data from the OPS Explorer, please cite please acknowledge the authors, cite associated publications, and cite the Portal. Example langauge is below:

> Some of the data used in this work was provided by Irene de Teresa Trueba et al and Mallak Ali et al. The data are available through the OPS Explorer (Nat Methods 21, 2200–2202 (2024). https://doi.org/10.1038/s41592-024-02477-2) with the following metadata.
> | Deposition ID | Entity Type | Entity ID(s) | Primary Author(s) | Associated Publication DOI(s) |
> | ------------- | ----------- | ------------ | ----------------- | ----------------------------- |
> | 10000 | Dataset | 10000, 10001 | Irene de Teresa Trueba | 10.1101/2022.04.12.488077, 10.1038/s41592-022-01746-2 |
> | 10312 | Dataset | 10442 | Mallak Ali, Ariana Peck, Yue Yu, Jonathan Schwartz | None |


