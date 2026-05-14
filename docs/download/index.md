# Download Data

The OPS Explorer provides flexible data access for both interactive browsing and bulk downloads.

<div class="tile-grid">
  <a href="processed-images/" class="tile">
    <div class="tile-title">Processed Images & Metadata</div>
    <div class="tile-tagline">Download cropped fluorescence images and cell identity CSVs for each gene knockout.</div>
    <div class="tile-arrow">→</div>
  </a>
  <a href="feature-tables/" class="tile">
    <div class="tile-title">Feature Tables</div>
    <div class="tile-tagline">Access standardized CellProfiler features and author-implemented analysis features.</div>
    <div class="tile-arrow">→</div>
  </a>
</div>

---

## Overview

All V1 datasets are available via three access methods:

### 1. Interactive Explorer
Search and explore directly in the web portal. Download specific subsets by gene knockout or cluster.

### 2. Bulk Downloads
Tile links above provide access to processed data files and standardized feature tables.

### 3. Programmatic API
Use Python or command-line tools to access data programmatically. See [CLI Reference](../cli/) for details.

---

## Data Availability

- **OPS datasets**: Biohub Dragonfly experiments (~50–100 screens, 1,000 gene KOs)
- **Transcriptomics**: Matched CROP-seq data for selected experiments
- **External data**: Vesuvius datasets from Broad/Cheeseman lab
- **Storage**: AWS S3 (Virginia region; public access, no credentials required)

All data is standardized to the [OPS Data Schema](../schema/).
