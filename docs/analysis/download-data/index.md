# Explore Data Before Downloading

OPS collections can be tens to hundreds of gigabytes. Before committing to a download, you usually want to take a look at subsets of the data and confirm it covers the perturbations you care about, the cells are healthy, the effect sizes look reasonable, and the feature set matches what your downstream analysis needs. There are two complementary ways to do that without pulling the full collection.


## 1. Click-through preview: the OPS Explorer

The [OPS Explorer](https://chanzuckerberg.github.io/ops-schema/) is the visual preview layer for every published OPS dataset. Without downloading anything you can:

- Browse collections and per-experiment metadata
- Open the **volcano plot** for any visualization to see which perturbations move which features
- Open the **UMAP/embedding** to see how perturbations cluster
- Pull up representative single-cell **example crops** for any perturbation
- Inspect the schema/feature definitions before you write code against them

Use this when you want to look at data through processed figures and images. See the [Explorer Tutorial](./viewer-quickstart.md) for a walk-through.


## 2. Programmatic preview: the analysis notebook

When you want to slice the data and/or explore it in more depth, e.g., count cells per perturbation, rank features by significance, plot a custom feature distribution, test a hypothesis, you can use the OPS analysis code.

> **Open the notebook:** [OPS Analysis](../ops_analysis.ipynb) - view the code in your browser without running it locally, or download the source `.ipynb` from the same page to run it yourself.

**What the notebook covers:**

- Load the collection's `collection_metadata.yaml`, `cell_data.parquet`, and `aggregated_data.h5ad`
- **Slice** cells by perturbation, by non-targeting control, by cell-cycle phase, by minimum cell count, etc.
- **Slice** perturbations by significance on a chosen feature, and features most affected by a chosen perturbation
- **Visualize:** feature distribution vs control, single-perturbation volcano, all-perturbation scatter for one feature, the perturbation embedding, top-perturbation × top-feature heatmap, cluster composition

### Run it yourself

```bash
# 1. Install the analysis dependencies
pip install pandas numpy anndata matplotlib seaborn pyyaml

# 2. Open the notebook
jupyter lab docs/ops_analysis.ipynb
```

