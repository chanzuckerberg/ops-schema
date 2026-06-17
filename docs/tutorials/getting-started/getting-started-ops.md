# Getting Started with OPS

An initial list of **protocols, tools, and resources** for labs starting out to run and analyze OPS experiments


## What You Need to Run an OPS Experiment

Four general components:

1. A **pooled CRISPR library** delivered to cells (each cell receives one perturbation + a sequenced barcode).
2. A **phenotypic imaging readout** (e.g. fluorescent markers for organelles, signaling, morphology).
3. **In-situ sequencing** of the guide/barcode in the same cells that were imaged.
4. An **analysis pipeline** that links each cell's barcode (perturbation identity) to its image-derived features.

The protocols below are organized based on these steps.


## Screening Workflows & Chemistries

Most OPS experiments utilize a **CROP-seq** lentiviral vector, which links an sgRNA perturbation to a sequenced barcode in each cell, and differ mainly in how the barcode is read out (in-situ sequencing by synthesis vs. hybridization) and how the barcode signal is amplified. For a side-by-side schematic of the main protocols, see Kahnwald et al., *Nature Biotechnology* 43, 1055–1057 (2025).

| Workflow / chemistry | Reference | What it does |
|---|---|---|
| **CROP-seq** | [Datlinger et al., *Nat. Methods* (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5334791/) | The base lentiviral vector. Originally for droplet scRNA-seq; adopted in OPS to associate an imaging phenotype with an sgRNA perturbation. |
| **Original OPS (in-situ sequencing)** | Feldman et al., *Cell* (2019) | Foundational OPS protocol — pooled CRISPR with in-situ sequencing-by-synthesis of guide barcodes and high-content imaging readout. |
| **PerturbView** | [Kudo et al., *Nat. Biotechnol.* (2025)](https://www.nature.com/articles/s41587-024-02391-0) | Uses the ZOMBIE protocol — T7 in-vitro transcription of inserted guides (via a chimeric U6/T7 promoter) to amplify barcodes independently of the cell's own transcription. Sequencing follows fixed-cell phenotyping. |
| **CRISPRmap** | [Gu et al., *Nat. Biotechnol.* (2025)](https://www.nature.com/articles/s41587-024-02386-x) | Replaces sequencing-by-synthesis with combinatorial oligonucleotide FISH hybridization — lower cost, more robust readout. A modified version (RNAmap) detects endogenous mRNA. |
| **Perturb-FISH** | Binan et al., *Cell* (2025) | Combines MERFISH-style spatial transcriptomics with CRISPR screening; relies on T7 amplification of the sgRNA, then a modified MERFISH readout. |
| **CROPseq-multi** | [Walton et al., *bioRxiv* (2025)](https://www.biorxiv.org/content/10.1101/2024.03.17.585235v2) | A CROP-seq-inspired system to multiplex Cas9 perturbations. For OPS, an optimized in-situ protocol improves barcode counts ~10×, detects recombination, and cuts required sequencing cycles ~3×. v2 adds T7 IVT compatibility. |

Choice of workflow drives reagent cost, number of sequencing cycles, and instrument requirements. Hybridization-based readout (CRISPRmap) and T7-amplified approaches (PerturbView, CROPseq-multi v2) were each developed to reduce cost or improve barcode detection relative to the original sequencing-by-synthesis approach.


## Instrumentation

Academic labs originally adapted existing microscopes and performed manual sequencing across ~10–15 cycles to read out guides. Two commercial platforms are now commonly used:

| Instrument | Vendor | Notes |
|---|---|---|
| [Opera Phenix (Plus)](https://www.revvity.com/gb-en/product/opera-phenix-plus-system-hh14001000) | Revvity (PerkinElmer) | High-throughput imaging in single- and multi-camera configurations. Modalities: brightfield, confocal, digital phase contrast, fluorescence. |
| [AVITI24](https://www.elementbiosciences.com/) | Element Biosciences | Direct in-sample sequencing (DISS) integrating sequencing with multiplexed phenotyping of cell morphology and protein expression. Uses [Avidite Base Chemistry (ABC)](https://www.elementbiosciences.com/technology/avidite-base-chemistry) — PCR-free rolling-circle amplification, improved 4-channel base detection. |


## Phenotyping: Multiplexed Imaging & Reagents

A common limitation of OPS is the small number of protein targets imaged in parallel (typically ~3–4 markers). Iterative-staining and nanobody approaches expand this:

| Method / reagent | Reference / source | What it does |
|---|---|---|
| **IBEX** (Iterative Bleaching Extends Multiplexity) | [Radtke et al., *Nat. Protocols* (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11468668/) | Uses borohydride derivatives to bleach fluorescently conjugated antibodies between staining rounds for higher-plex imaging. |
| **cycIF** (cyclic immunofluorescence) | [Lin et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5233430/) | Stain → image in four colors → inactivate fluorophores with mild base + peroxide + light → repeat. |
| **Secondary nanobodies** | [Nanotag Biotechnologies](https://nano-tag.com/) | Oligo-tagged secondary nanobodies (small, high-affinity single-domain antibodies) enable cleavable, multi-round phenotyping panels (e.g. 30-plex). |


## Analysis Pipelines & Tools

| Tool | Purpose | Link |
|---|---|---|
| **CellProfiler** | Per-cell morphological feature extraction from images | [cellprofiler.org](https://cellprofiler.org) |
| **Cellpose** | Generalist cell/nucleus segmentation | [cellpose.org](https://www.cellpose.org/) |
| **OpticalPooledScreens** (Blainey lab) | Reference in-situ sequencing analysis — from raw data to a sequencing-read table (Feldman et al., *Cell* 2019) | [blaineylab/OpticalPooledScreens](https://github.com/blaineylab/OpticalPooledScreens) |
| **Brieflow** (Cheeseman lab) | Integrated end-to-end pipeline for fixed-cell OPS data — segmentation, barcode calling, feature–perturbation linkage ([preprint](https://www.biorxiv.org/content/10.1101/2025.05.26.656231v1)) | [cheeseman-lab/brieflow](https://github.com/cheeseman-lab/brieflow) |
| **PerturbView** | Base calling for PerturbView in tissue; alignment to Xenium spatial transcriptomics (Kudo et al., 2025) | [Genentech/PerturbView](https://github.com/Genentech/PerturbView) |
| **Perturb-FISH** | Analysis scripts from the Perturb-FISH publication (Binan et al., 2025) | [lbinan/Perturb-FISH](https://github.com/lbinan/Perturb-FISH) |
| **CellxState Explorer** | Explore published OPS datasets in-portal (gallery, embeddings, volcano plots) | See [Viewer Quickstart](./viewer-quickstart.md) |
| **OPS Data Standard v0.1.0** | Format your screen for submission to the portal | [ops-schema on GitHub](https://github.com/chanzuckerberg/ops-schema) |


## Data Format & Submission

If you intend to publish your screen to the Biohub Data Portal, format it against the OPS Data Standard.

Required artifacts:

- `perturbation_library.csv` - sgRNA barcodes, gene targets, control definitions
- `cell_data.parquet` - per-cell feature table with `cell_uid` and `perturbation_id`
- `aggregated_data.h5ad` - perturbation-level morphological profiles (required for visualization)
- `examples.zarr` - per-perturbation image crops for the gallery view


<!--
## How to Contribute to This Page

This page is a scaffold and should grow with input from people who run OPS:

1. **Add protocols** with a source link (protocols.io, a paper's methods, or a lab SOP) and a one-line note on scope.
2. **Replace _TODO_ rows** with the protocols and tools you actually use.
3. **Flag anything out of date** — chemistries and pipelines evolve quickly.
-->

