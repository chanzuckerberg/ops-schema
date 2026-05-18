# OPS Data Standard — Experimental Metadata

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Experimental Metadata

**Scope:** Per experiment
**File format:** YAML
**File path:** `{aggregation_name}/metadata/experimental_metadata.yaml`

> **Scope limitations (v0.1.0):** Structured chemical/drug perturbation metadata is out of scope for this version. Experiments that multiplex genetic perturbations with chemical treatments (e.g., compound dosing, FFA treatment) SHOULD document the chemical context in `cellular.growth_conditions` as free text.

This file captures the biological, experimental, and technical context of the screen.

### Screen Information

#### experiment.screen_title

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.screen_title</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text title describing the screen</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>.</td>
</tr>
</tbody>
</table>

#### experiment.pseudobulk

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.pseudobulk</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of cell state labels used for pseudobulk groupings in this experiment. MAY include a CROP-seq cell state label (e.g., <code>"crop_seq"</code>); if a CROP-seq label is present, a corresponding CROP-seq AnnData object MUST be included in the submission (see Multimodal Experiments).</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate if pseudobulk analysis was performed.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[String]</code>. Each element is a free-text label (e.g., <code>["interphase", "mitotic"]</code>). OPTIONAL.</td>
</tr>
</tbody>
</table>

#### experiment.crop_seq_anndata

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.crop_seq_anndata</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Path to the CROP-seq AnnData file, relative to <code>{aggregation_name}/metadata/</code>. MUST be present when the experiment includes a paired CROP-seq readout (see Multimodal Experiments).</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate if CROP-seq data is included.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL. (e.g., <code>"crop_seq.h5ad"</code>).</td>
</tr>
</tbody>
</table>

#### experiment.organism_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.organism_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The organism from which the assayed cells were derived</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be an <a href="https://www.ebi.ac.uk/ols4/ontologies/ncbitaxon">NCBI organismal classification</a> term (e.g., <code>"NCBITaxon:9606"</code> for <em>Homo sapiens</em>).</td>
</tr>
</tbody>
</table>

#### experiment.organism

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.organism</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>organism_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The tissue or cell line from which the assayed cells were derived. Validation rules depend on <code>tissue_type</code> — see Validation Rules V-1, V-1b, and V-2.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. See Validation Rules <a href="schema.md#validation-rules">V-1</a> and <a href="schema.md#validation-rules">V-2</a> for conditional requirements by <code>tissue_type</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>tissue_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.tissue_type

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.tissue_type</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Classification of the sample type. Governs validation of <code>tissue_ontology_term_id</code> and <code>development_stage_ontology_term_id</code>.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be one of <code>"tissue"</code>, <code>"organoid"</code>, <code>"cell culture"</code>, or <code>"cell line"</code>.</td>
</tr>
</tbody>
</table>

#### experiment.disease_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.disease_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Disease status of the organism or cell line from which cells were derived</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be <a href="https://www.ebi.ac.uk/ols4/ontologies/pato/classes?obo_id=PATO:0000461"><code>"PATO:0000461"</code></a> for <em>normal</em> or <em>healthy</em>, or the most accurate descendant of <a href="https://www.ebi.ac.uk/ols4/ontologies/mondo/classes?obo_id=MONDO:0000001"><code>"MONDO:0000001"</code></a> for <em>disease</em>.</td>
</tr>
</tbody>
</table>

#### experiment.disease

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.disease</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>disease_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

#### experiment.development_stage_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.development_stage_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Development stage of the organism. For cell lines, MUST be <code>"na"</code>. See Validation Rules V-1b, V-3, V-4 for organism- and tissue-type-specific requirements.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. See Validation Rules <a href="schema.md#validation-rules">V-1b</a>, <a href="schema.md#validation-rules">V-3</a>, and <a href="schema.md#validation-rules">V-4</a>.</td>
</tr>
</tbody>
</table>

#### experiment.development_stage

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.development_stage</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>development_stage_ontology_term_id</code>. MUST be <code>"na"</code> when <code>development_stage_ontology_term_id</code> is <code>"na"</code>.</td>
</tr>
</tbody>
</table>

#### experiment.assay_ontology_term_id

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.assay_ontology_term_id</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>The assay type used in the experiment</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be an <a href="https://www.ebi.ac.uk/ols4/ontologies/efo">Experimental Factor Ontology (EFO)</a> term (e.g., <code>"EFO:0022605"</code>).</td>
</tr>
</tbody>
</table>

#### experiment.assay

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>experiment.assay</code></td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>System MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be the human-readable name assigned to <code>assay_ontology_term_id</code>.</td>
</tr>
</tbody>
</table>

---

### Cell Line Information

#### cellular.growth_conditions

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.growth_conditions</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text description of growth media, supplements, and culture conditions</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include catalog numbers and concentrations for all reagents.</td>
</tr>
</tbody>
</table>

#### cellular.seeding.density_cells_cm2

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.seeding.density_cells_cm2</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Cell seeding density at the start of the experiment, in cells per cm²</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### cellular.induction.duration

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.induction.duration</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Duration of induction (e.g., Cas9 or doxycycline induction)</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate if induction was performed.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST include unit (e.g., <code>"78 hours"</code>). OPTIONAL.</td>
</tr>
</tbody>
</table>

#### cellular.plate_type

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>cellular.plate_type</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description of the plate format used for imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include well count, substrate, and catalog identifier (e.g., <code>"6-well glass-bottom (Cellvis P06-1.5H-N)"</code>).</td>
</tr>
</tbody>
</table>

---

### CRISPR Library

#### library.vector

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.vector</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Name and Addgene accession of the vector used for sgRNA delivery</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include Addgene accession number (e.g., <code>"CROPseq-puro-v2 (Addgene #127458)"</code>).</td>
</tr>
</tbody>
</table>

#### library.gene_selection

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.gene_selection</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text description of the rationale or strategy for gene selection in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### library.positive_controls

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.positive_controls</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description or list of positive control perturbations included in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code> or <code>List[String]</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

#### library.negative_controls

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>library.negative_controls</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Description or list of negative control perturbations included in the library</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code> or <code>List[String]</code>. OPTIONAL.</td>
</tr>
</tbody>
</table>

---

### In Situ Sequencing (ISS)

> **Note:** ISS metadata is included for completeness. ISS image data is NOT submitted as part of this standard.

#### iss.cycles

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.cycles</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Number of sequencing cycles performed</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Integer</code>.</td>
</tr>
</tbody>
</table>

#### iss.objective

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.objective</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Microscope objective used for ISS imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include magnification, NA, and catalog identifier.</td>
</tr>
</tbody>
</table>

#### iss.chemistry

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.chemistry</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Sequencing chemistry used (e.g., number of colors)</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"four color"</code>).</td>
</tr>
</tbody>
</table>

#### iss.channels

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>iss.channels</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of imaging channels used in ISS</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter SHOULD annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[Object]</code>. Each object MUST include <code>name</code> (<code>String</code>), <code>laser_wavelength_nm</code> (<code>Integer</code>), and <code>exposure_time_ms</code> (<code>Integer</code>).</td>
</tr>
</tbody>
</table>

---

### Phenotype (PH) Imaging

#### phenotype.objective

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>phenotype.objective</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Microscope objective used for phenotype imaging</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. SHOULD include magnification, NA, and catalog identifier.</td>
</tr>
</tbody>
</table>

#### phenotype.exposure_time_ms

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>phenotype.exposure_time_ms</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>List of per-channel exposure times in milliseconds, in the same channel order as <code>channels_metadata[]</code> in the Zarr plate root.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>List[Integer]</code>. Length MUST equal the number of channels in <code>channels_metadata[]</code>.</td>
</tr>
</tbody>
</table>

---

### Microscope Hardware

#### microscope.system

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>microscope.system</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Name and model of the microscope system used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"Nikon Ti-2 inverted epifluorescence"</code>).</td>
</tr>
</tbody>
</table>

---

### Data Processing

#### pipeline.github

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>pipeline.github</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>GitHub repository URL or handle for the processing pipeline used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. (e.g., <code>"cheeseman-lab/brieflow"</code>).</td>
</tr>
</tbody>
</table>

#### pipeline.version

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>pipeline.version</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Version of the processing pipeline used</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>Number</code>. (e.g., <code>1.49</code>).</td>
</tr>
</tbody>
</table>

---
