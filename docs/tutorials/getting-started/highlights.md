# OPS Highlights

List of notable **optical pooled screening (OPS)** papers and the labs driving the field


## Foundational & Methods Papers

These papers established the core OPS approach - pooled CRISPR perturbation with in-situ sequencing of barcodes and image-based phenotyping.

| Paper | Lab / Group | Why it matters |
|---|---|---|
| Feldman et al., **"Optical Pooled Screens in Human Cells"**, *Cell* (2019) | Blainey Lab (Broad/MIT) | The foundational OPS method paper — pooled CRISPR screens with in-situ sequencing of guide barcodes and high-content imaging readout. |
| Kahnwald et al., *Nature Biotechnology* 43, 1055–1057 (2025) | — | Overview/commentary comparing the main OPS protocols (original OPS, PerturbView, CRISPRmap). |
| _TODO_ | _TODO_ | Earlier in-situ sequencing / barcode-readout precursors (e.g. ISS, FISSEQ); step-by-step wet-lab protocol papers. |

---

## Landmark Screens & Applications

Published OPS experiments (and preprints), with the cell type screened and approximate scale. Useful for seeing what's been done and at what scale.

| Study | Cell type | Cells screened | Genes (gRNAs) |
|---|---|---:|---:|
| Feldman et al., 2019 | HEK293, HeLa, U2OS, other | >1,000,000 | 952 (5,638) |
| [Kanfer et al., 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7816647/) | U2OS | >13,000,000 | 2,774 (12,775) |
| [Yan et al., 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7821101/) | hTERT-RPE1 | >1,500,000 | 544 (6,092) |
| [Chien et al., 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8099184/) | HEK293 | 15,000 | 1 |
| [Funk et al., 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC10482496/) | HeLa | >31,000,000 | 5,072 (20,445) |
| [Carlson et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10120039/) | HeLa | 10,000,000 | >20,000 (>80,000) |
| [Sivanandan et al., 2023](https://www.biorxiv.org/content/10.1101/2023.08.13.553051v3) | A549 | not specified | >2,000 (>8,000) |
| [Gentili et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11030420/) | HeLa, other | 45,000,000 | ~20,000 (~80,000) |
| [Carlson et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11014611/) | HeLa | 39,085,093 | 20,000 (80,000) |
| [Labitigan et al., 2024](https://elifesciences.org/reviewed-preprints/94964) | U2OS | ~1,500,000 | 366 |
| [Fandrey et al., 2024](https://www.nature.com/articles/s41587-024-02516-5) | HeLa, other | not specified | >20,000 (>80,000) |
| [Kudo et al., 2024](https://www.nature.com/articles/s41587-024-02391-0) | iPSC-neurons, other | not specified | 163 |
| [Eaton et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12262249/) | Bacteria | 1,600,000,000 (2M lineages) | 585 (29,738) |
| [Le et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12427603/) | HEK293, primary neurons | >2,000,000 | 644 (2,626) |
| [Quintanilla et al., 2025](https://www.biorxiv.org/content/10.1101/2025.02.15.638448v1.full) | U2OS, other | 6,000,000 | 5 (14) |
| [Ramezani et al., 2025](https://www.nature.com/articles/s41592-024-02537-7) | HeLa, A549 | >30,000,000 | >20,000 (>80,000) |
| [Binan et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12135205/) | iPSC-astrocytes, other | 76,400 | 485 |

A more complete, community-maintained [spreadsheet of published OPS experiments](https://docs.google.com/spreadsheets/d/1bawVTCB7ZUM8mjESwxR53OfBwDQRVaMT7mAi3PKppic/edit?usp=sharing) — including papers that address individual OPS components (barcoding, imaging, analysis)


## Labs to Follow

Groups actively developing or applying OPS and image-based pooled screening methods.

### Academic Labs

| Lab | Institution | Focus |
|---|---|---|
| [**Paul Blainey**](https://blainey.mit.edu/) | Broad Institute / MIT | Core OPS method development; high-throughput microscopy and microfluidics. Applied OPS across many cell types; holds OPS patents; convenes an (invitation-only) OPS technology forum. |
| [**Iain Cheeseman**](https://cheesemanlab.wi.mit.edu/) | Whitehead Institute / MIT | Control of gene expression across cell states; co-developed the [Brieflow](https://www.biorxiv.org/content/10.1101/2025.05.26.656231v1) OPS analysis pipeline with the Blainey lab. |
| [**Andrew Bassett**](https://www.sanger.ac.uk/person/bassett-andrew/) & [**Omer Bayraktar**](https://www.sanger.ac.uk/person/bayraktar-omer/) | Wellcome Sanger Institute | Spatial-transcriptomic readouts in OPS (with Mats Nilsson); RNA-dye + sgRNA-sequencing chemistry; iPSC landing-pad engineering; microglia screening. |
| [**Emma Lundberg**](https://lundberglab.stanford.edu/) (with Noor Ahmed) | Stanford | Setting up OPS with open-source sequencing/imaging automation and data registration; Zarr-based formats; PerturbView protocol on a programmable Cephla microscope. |
| [**Adam Cohen**](https://cohenweb.rc.fas.harvard.edu/) | Harvard | All-optical electrophysiology (Optopatch); voltage reporters and associated microscopy. |
| [**Clotilde Lagier-Tourenne**](https://www.lagiertourennelab.com/) | Harvard Medical School / MGH | Modifiers of FUS and TDP-43 pathology via OPS in iPSC-derived neurons (with Blainey). |
| [**Johan Paulsson**](https://paulsson.med.harvard.edu/) | Harvard Medical School | Single-cell biophysics; scientific founder of Bifrost. |
| [**Beth Stevens**](https://www.stevenslab.org/) | Harvard / Broad | Microglia biology; OPS in iPSC-derived microglia to map modifiers of phagocytosis. |
| [**Michael Ward**](https://www.ninds.nih.gov/about-ninds/who-we-are/staff-directory/michael-e-ward) | NIH / CARD | Project-based OPS in iPSC-derived neurons; developing and expanding immunofluorescent / nanobody reagents for the OPS community. |
| [**Ophir Shalem**](https://www.shalemlab.org/) | U. Pennsylvania / CHOP | Pooled gene tagging with high-throughput microscopy and optical sequencing to map subcellular protein localization in iPSC neurons. |

### Not-for-Profit & Institutional Platforms

| Organization | Lead(s) | OPS activity |
|---|---|---|
| **Broad Institute** | Paul Blainey; Sami Farhi (data); Anne Carpenter (VISTA) | Building a commercial-instrument OPS platform (Opera Phenix, automated ~15-round 2-color sequencing) with standardized QC metrics; multiple investigator entry points; ~250M filtered cell×perturbations generated to date. |
| **NIH CARD** | Michael Ward | Project-based OPS on a custom twin-camera Nikon widefield scope; focus on expanding IF reagents (oligo-conjugated nanobodies via Nanotag). |
| [**Allen Institute for Cell Science**](https://www.allencell.org/our-science-cellscapes.html) | Ru Gunawardane | CellScapes program — 3D live imaging of endogenously tagged hiPSCs for predictive, data-driven cell models. |
| **Wellcome Sanger Institute** | Andrew Bassett / Omer Bayraktar | Project-based OPS (Opera Phenix, Element); landing-pad iPSC lines and barcoded secondary nanobodies. |
| **Janelia** | Carsen Stringer | [Cellpose](https://www.cellpose.org/) — generalist segmentation widely used in image-based screening. |

### Industry / For-Profit

| Company | Notes |
|---|---|
| **Genentech / Roche** | High-content imaging of NGN2-derived neurons (with Recursion); developed an [NGN2 high-throughput screening protocol](https://www.cell.com/cell-reports-methods/fulltext/S2667-2375(24)00236-4). |
| [**Recursion**](https://www.recursion.com/) | Multimodal phenomics drug-discovery platform (genomics, transcriptomics, proteomics, phenomics); data and models proprietary. |
| [**Quiver Bioscience**](https://www.quiverbioscience.com/) | Spun out of the Adam Cohen lab; OPS platform for optogenetics and cellular readouts in iPSC-derived neurons. |
| [**Bifrost**](https://bifrost.bio/about/) | Founders incl. Johan Paulsson, George Church, Paul Blainey, Johan Elf; large-scale OPS (reports ~50M cells/week across ~20,000 genes). |

---

## Related Modalities

OPS sits alongside other pooled and/or spatial perturbation approaches. A few adjacent areas to consider:

- **Perturb-seq** - pooled CRISPR with single-cell RNA-seq readout (sequencing-based rather than imaging-based).
- **Perturb-FISH / MERFISH-based screens** - spatially resolved transcriptomic readout of pooled perturbations.
- **Cell Painting** - high-content morphological profiling (often arrayed rather than pooled), complementary feature space.
