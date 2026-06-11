# OPS Explorer

Optical Pooled Screening (OPS) combines CRISPR-based genetic perturbations with high-content microscopy to reveal the relationship between genes and cell morphology.
 
The OPS Explorer is the first centralized location to visualize and interact with OPS data with a standardized schema and file formats accessible via CLI. 
<br>
<div class="hero-buttons">
  <a href="https://biohub.ai/ops-explorer/about?utm_source=docsite&utm_medium=banner&utm_campaign=ops-jun2026" class="md-button hero-button">
   Use the Explorer
  </a>
<br />
<br>
  <a href="tutorials/quickstart/" class="md-button hero-button">
   Explorer Quickstart
  </a>
</div>
<br />

**V1 capabilities include:**

  * Dataset collection pages with experimental context and standardized schema
  * Interactive data explorer with synchronized imaging and scRNA-seq data
  * Visualizations of imaging and/or scRNAseq UMAP embeddings, feature tables, volcano plots, and inline representative cell images
  * Gene knockout search and exploration across 1,000 perturbations
  * All data is available for download either in-browser or via a CLI

**Stay in touch by joining our OPS Community Slack**

1. [Use this link](https://join.slack.com/t/biohub-community/shared_invite/zt-3yxdy77dv-rJHI97SprbDXwEYP3Y1tqQ) to join the Biohub Community Slack Workspace.
   
2. Join the `#ops-explorer-community` channel ([Slack docs](https://slack.com/help/articles/205239967-Join-a-channel)).
 
3. Send a message to introduce yourself.

**Submit Feedback**

Submit feedback using [this form](https://info.biohub.org/ops-feedback).
    
## Getting Started

<div class="tile-grid">

  <a href="tutorials/" class="tile">
    <h3 class="tile-title">Explorer Tutorial</h3>
    <p class="tile-tagline">
      Comprehensive reference guides
    </p>
  </a>

  <a href="analysis/" class="tile">
    <h3 class="tile-title">Data Analysis</h3>
    <p class="tile-tagline">
      Notebooks for downloading and analyzing data
    </p>
  </a>

  <a href="cli/" class="tile">
    <h3 class="tile-title">CLI Reference</h3>
    <p class="tile-tagline">
      Command-line tool for downloading data
    </p>
  </a>

  <a href="https://github.com/chanzuckerberg/ops-schema/tree/main/standards/ops" target="_blank" rel="noopener noreferrer" class="tile">
    <h3 class="tile-title">Data Schema</h3>
    <p class="tile-tagline">
      Details on data formats and structure in Github
    </p>
  </a>
</div>

## Contribute Your Data
For data contributor inquiries, please fill out [this form](https://info.biohub.org/ops-data-contribution) or contact: support@biohub.org.

### **Submitting Data to OPS Explorer**

OPS Explorer accepts both previously published datasets and new, unpublished screens. If you have OPS data you'd like to contribute, we'd love to work with you.

### **Who can submit?**

Any lab running optical pooled screens is eligible to submit. We welcome data at any stage — whether it's been published in a journal or is being shared for the first time.

### **Getting your data into the schema**

The [OPS Data Standard](https://github.com/chanzuckerberg/ops-schema) defines a structured format for OPS datasets. Here's what the process looks like at a high level:

1. **Run your screen** using your existing pipeline  
2. **Convert your output** into the OPS Data Standard format (see below for tools)  
3. **Submit your metadata** by filling out the experimental metadata YAML  
4. **Work with the OPS Explorer team** to review and publish your dataset

### **Tools to help you convert**

We're building tools to make conversion as low-friction as possible:

* **Brieflow users:** We're working directly with the Cheeseman lab on Brieflow, which has been updated to adopt the Zarr format. Once your lab updates to the latest version of Brieflow, your pipeline output will automatically convert into the OPS schema — no additional steps required.  
* **Existing data:** The Cheeseman lab is also developing a Brieflow extension to help convert previously collected data into the schema.

### **Help us improve**

We know data conversion can be painful. We want to work directly with labs to understand what's hard about the schema or the submission process so we can keep building better tools. If something doesn't fit your workflow, please tell us — that feedback directly shapes what we build next.

### **Get in touch**

Interested in submitting or want to learn more? [Contact us](https://info.biohub.org/ops-data-contribution) to start the conversation.



## Citation

If you use data from the OPS Explorer, please acknowledge the authors, cite associated publications, and cite the OPS Explorer. Example langauge is below:

> Some of the data used in this work was provided by Anna Le et al. The data were published in *Le et al., Cell Reports, 2025* and are available through the OPS Explorer.
